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
