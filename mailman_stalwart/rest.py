import logging
from email.utils import parseaddr


from public import public
from zope.component import getUtility

from mailman.config import config
from mailman.interfaces.domain import IDomainManager
from mailman.interfaces.listmanager import IListManager

from mailman.runners.lmtp import split_recipient, SUBADDRESS_NAMES
from mailman.rest.helpers import child, etag, okay


def address_is_list(to, listnames=[]):
    to = parseaddr(to)[1].lower()
    local, subaddress, domain = split_recipient(to)
    if subaddress is not None:
        # Check that local-subaddress is not an actual list name.
        listname = "{}-{}@{}".format(local, subaddress, domain)
        if listname in listnames:
            local = "{}-{}".format(local, subaddress)
            subaddress = None
    listname = "{}@{}".format(local, domain)
    if listname not in listnames:
        return False
    canonical_subaddress = SUBADDRESS_NAMES.get(subaddress)
    if subaddress is None:
        # The message is destined for the mailing list.
        # nothing to do here, just keep code similar to handle_DATA
        pass
    elif canonical_subaddress is None:
        # The subaddress was bogus.
        return False
    else:
        # A valid subaddress.
        # nothing to do here, just keep code similar to handle_DATA
        pass
    return True


def _get_alias_domain(domain):
    domain_manager = getUtility(IDomainManager)
    d = domain_manager.get(domain)
    if d is not None and d.alias_domain:
        return d.alias_domain
    return domain


def canonicalize_to(to, listnames=[]):
    to = parseaddr(to)[1].lower()
    local, subaddress, domain = split_recipient(to)
    if subaddress is not None:
        # Check that local-subaddress is not an actual list name.
        listname = "{}-{}@{}".format(local, subaddress, domain)
        if listname in listnames:
            local = "{}-{}".format(local, subaddress)
            subaddress = None
    domain = _get_alias_domain(domain)
    if subaddress:
        return f"{local}-{subaddress}@{domain}"
    return f"{local}@{domain}"


@public
class MTAHook:
    def __init__(self):
        self._plugin = config.plugins["mailman_stalwart"]

    def on_get(self, request, response):
        okay(response, etag(dict(yes=True)))

    def on_post(self, request, response):
        list_manager = getUtility(IListManager)

        listnames = set(list_manager.names)
        logging.warn(listnames)
        is_list = False

        to = request.media.get("envelope", {}).get("to", {})
        modifications = []
        for address in to:
            if address_is_list(address["address"], listnames=listnames):
                modifications.append(
                    {"type": "deleteRecipient", "value": address["address"]}
                )
                modifications.append(
                    {
                        "type": "addHeader",
                        "name": "Delivered-To",
                        "value": address["address"],
                    }
                )
                modifications.append(
                    {
                        "type": "addRecipient",
                        "value": canonicalize_to(address["address"]),
                    }
                )
                is_list = True
        if is_list:
            _value = "Yes" if is_list else "No"
            modifications.append(
                {
                    "type": "addHeader",
                    "name": "X-Mailman-List",
                    "value": _value,
                }
            )
        logging.warn(modifications)
        okay(
            response,
            etag(
                {
                    "action": "accept",
                    "modifications": modifications,
                }
            ),
        )


@public
class MTAHookREST:
    def on_get(self, request, response):
        resource = {
            "my-name": "stalwart",
            "my-child-resources": "hook",
        }
        okay(response, etag(resource))

    @child()
    def hook(self, context, segments):
        return MTAHook(), []
