#!/bin/bash

source ./.env

curl \
  -XPOST \
  --user restadmin:${MM3_MAILMAN_REST_PASSWORD} \
  -H"Content-Type: application/json" \
  http://mailman-core:8001/3.1/domains \
  --data '{"mail_host": ${DOMAIN}, "description": ${DOMAIN}, "alias_domain": mail.${DOMAIN}}'
