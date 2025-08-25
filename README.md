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

### original was. 
```
git clone --recurse-submodules https://github.com/ewdurbin/stalwart-mailman.git
```
With the current git, it's all different.
You'll need to 

- git clone 
cd mai
git pull
TAG_NS=joergmschulz CURRENT_PLATFORM=linux/arm64/v8 BUILD_ROLLING=1 ./build.sh 

- startup stalwart first, set up manually, get it working
- startup mailman db, get it working
- startup mailman-core, get it working
- startup postorious, get it working.
- test whether all works together.

## you'll need to edit the following files:
.env
stalwart.cfg (probably you'll move that to another directory)
mailman-extra.cfg (probably you'll move that to another directory and mount it from there, like /data/${DOMAIN}/mm3/core/)