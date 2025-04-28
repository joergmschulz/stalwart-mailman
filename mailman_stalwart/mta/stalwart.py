# Copyright (C) 2013-2025 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <https://www.gnu.org/licenses/>.

"""Creation/deletion hooks for the Stalwart mail server."""

import logging
from collections import defaultdict
from functools import lru_cache

import requests
from public import public
from requests.auth import HTTPBasicAuth
from zope.component import getUtility
from zope.interface import implementer

from mailman.config import config
from mailman.config.config import external_configuration
from mailman.interfaces.domain import IDomainManager
from mailman.interfaces.mta import (
    IMailTransportAgentAliases,
    IMailTransportAgentLifecycle,
)


def _get_alias_domain(domain):
    domain_manager = getUtility(IDomainManager)
    d = domain_manager.get(domain)
    if d is not None and d.alias_domain:
        return d.alias_domain
    return domain


class _FakeListManager:
    def __init__(self):
        self.get_alias_domain = lru_cache(maxsize=1000)(self._get_alias_domain)

    def get(self, list_name, true_mail_host):
        mail_host = self.get_alias_domain(true_mail_host)
        return _FakeList(list_name, mail_host, true_mail_host)

    def _get_alias_domain(self, mail_host):
        return _get_alias_domain(mail_host)


class _FakeList:
    def __init__(self, list_name, mail_host, true_mail_host):
        self.list_name = list_name
        self.mail_host = mail_host
        self.true_mail_host = true_mail_host
        self.posting_address = "{}@{}".format(list_name, self.mail_host)


@public
@implementer(IMailTransportAgentLifecycle)
class LMTP:
    """Connect Mailman to Stalwart mail server

    See `IMailTransportAgentLifecycle`.
    """

    def __init__(self):
        # Locate and read the Stalwart specific configuration file.
        mta_config = external_configuration(config.mta.configuration)
        self.api_uri = mta_config.get("stalwart", "api_uri")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "mailman-core",
            }
        )

        self.auth = mta_config.get("stalwart", "auth")
        if self.auth == "api_key":
            logging.warn("Configuring stalwart integration with API Key")
            self.api_key = mta_config.get("stalwart", "api_key")
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                }
            )
        elif self.auth == "basic":
            logging.warn("Configuring stalwart integration with basic auth")
            self.user = mta_config.get("stalwart", "user")
            self.password = mta_config.get("stalwart", "password")
            self.session.auth = HTTPBasicAuth(self.user, self.password)

    def create(self, mlist):
        logging.warn(f"Creating list {mlist}")
        _mlist = _FakeListManager().get(mlist.list_name, mlist.mail_host)

        individual = self._get_individual(f"{_mlist.list_name}@{_mlist.mail_host}")

        domain = self._get_domain(_mlist.mail_host)
        if domain is None:
            self._create_domain(_mlist.mail_host)
            self._create_next_hop(_mlist.mail_host)

        true_domain = self._get_domain(_mlist.true_mail_host)
        if true_domain is None:
            self._create_domain(_mlist.true_mail_host)

        if individual is None:
            individual = self._create_individual(
                f"{_mlist.list_name}@{_mlist.mail_host}"
            )

        utility = getUtility(IMailTransportAgentAliases)
        actions = []
        for alias in list(utility.destinations(mlist)):
            actions.append(
                {
                    "action": "addItem",
                    "field": "emails",
                    "value": f"{alias}@{_mlist.mail_host}",
                }
            )
            actions.append(
                {
                    "action": "addItem",
                    "field": "emails",
                    "value": f"{alias}@{_mlist.true_mail_host}",
                }
            )

        response = self.session.patch(
            f"{self.api_uri}/principal/{individual['name']}", json=actions
        )

        response.raise_for_status()
        logging.warn(response.json())

    def delete(self, mlist):
        mlist = _FakeListManager().get(mlist.list_name, mlist.mail_host)

        individual = self._get_individual(f"{mlist.list_name}@{mlist.mail_host}")
        if individual is None:
            return

        response = self.session.delete(f"{self.api_uri}/principal/{individual['name']}")
        response.raise_for_status()

    def regenerate(self, directory=None):
        pass

    def _create_next_hop(self, domain):
        response = self.session.get(
            f"{self.api_uri}/settings/list",
            params={"prefix": "queue.outbound.next-hop"},
        )
        response.raise_for_status()
        data = response.json()
        # {'data': {'total': 3, 'items': {'0000.if': "is_local_domain('', rcpt_domain)", '0000.then': "'local'", '0001.else': 'false'}}}
        rules = defaultdict(dict)
        for item, value in data["data"]["items"].items():
            i, k = item.split(".")
            rules[int(i) + 1][k] = value
        rules[0] = {
            "if": f"rcpt_domain = '{domain}'",
            "then": "'mailman'",
        }
        values = []
        for index, data in rules.items():
            for key, value in data.items():
                values.append([f"queue.outbound.next-hop.{index}.{key}", value])
        payload = [
            {"type": "clear", "prefix": "queue.outbound.next-hop"},
            {"type": "delete", "keys": ["queue.outbound.next-hop"]},
            {
                "type": "insert",
                "prefix": None,
                "assert_empty": False,
                "values": values,
            },
        ]
        logging.warn(rules)
        logging.warn(payload)
        response = self.session.post(
            f"{self.api_uri}/settings",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        response = self.session.get(
            f"{self.api_uri}/reload/",
        )
        response.raise_for_status()
        data = response.json()
        logging.warn(data)

    def _create_domain(self, domain):
        response = self.session.post(
            f"{self.api_uri}/principal",
            json={
                "type": "domain",
                "name": domain,
                "description": f"Mailman domain - {domain}",
            },
        )
        response.raise_for_status()

        return self._get_domain(domain)

    def _create_individual(self, individual):
        response = self.session.post(
            f"{self.api_uri}/principal",
            json={
                "type": "individual",
                "name": individual,
                "description": f"Mailman list - {individual}",
            },
        )
        response.raise_for_status()

        return self._get_individual(individual)

    def _get_domain(self, domain):
        response = self.session.get(
            f"{self.api_uri}/principal", params={"types": "domain"}
        )
        response.raise_for_status()

        for _domain in response.json()["data"]["items"]:
            if _domain["name"] == domain:
                return _domain
        return None

    def _get_individual(self, individual):
        response = self.session.get(
            f"{self.api_uri}/principal", params={"types": "individual"}
        )
        response.raise_for_status()

        for found_individual in response.json()["data"]["items"]:
            if found_individual["name"] == individual:
                return found_individual
        return None
