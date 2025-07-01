# Stalwart + GNU Mailman

This repository demonstrates an integration of the
[Stalwart Mail Server](https://stalw.art/docs/get-started)
with
[GNU Mailman](https://docs.mailman3.org/projects/mailman/en/latest/)
for mailing lists.

## Implementation details

This integration is constructed of a
[mailman mta integration](mailman_stalwart/mta/stalwart.py)
for creating the necessary domains/accounts/routing in Stalwart Mail Server and a
[mailman hook plugin](mailman_stalwart/rest.py) implementing a
[Stalwart MTA Hook](https://stalw.art/docs/api/mta-hooks/overview).
## changes by js
- use most current stalwart repository
- move credentials, passwords, domain names to .env
### networking
- hide public services behind traefik
- leave internal services internal 

## Getting started

You will need
[git](https://git-scm.com),
a working [docker](https://docs.docker.com) environment,
and [docker compose](https://docs.docker.com/compose/).

* Clone the repository, and submodules

```
git clone --recurse-submodules https://github.com/ewdurbin/stalwart-mailman.git
```

* Change directory into the repo

```
cd stalwart-mailman
```

* Start the services

```
docker compose up
```

* Inititialize Stalwart

This will:
  - Create an `example.com` domain in Stalwart's Directory
  - Create a `postmaster@example.com` account in Stalwart's Directory
  - Set a password `password` for the `root@example.com` account
  - Create a `user@example.com` account in Stalwart's Directory
  - Set a password `password` for the `user@example.com` account
  - Remove rate limits for demonstration
  - Reload Stalwart Mail Server's configuration

```
docker compose exec mailman-web ./init-stalwart.sh
```

* Load Fixtures

This will setup:
  - A superuser with a confirmed email address
  - A domain `example.com` for lists to be created in

In another terminal:

```
docker compose exec mailman-web python manage.py loaddata fixtures.json
```

* Open the Mailman UI and login
  * Username: `root`
  * Password: `password`

```
open http://localhost:8000/accounts/login/
```

* Initialize Mailman Core

This will setup:
  - A domain in Mailman Core to match the fixture

```
docker compose exec mailman-web ./init-mailman-core.sh
```


* Create a list

```
open http://localhost:8000/mailman3/lists/new/
```

* Open Stalwart UI and login
  * Username: `admin`
  * Password: `password`

```
open http://localhost:8081
```

* Observe that
  * The necessary domains were created <http://localhost:8081/manage/directory/domains>
  * The necessary account and aliases were created <http://localhost:8081/manage/directory/accounts>
  * The necessary next-hop was configured <http://localhost:8081/settings/smtp-out-routing/edit>
