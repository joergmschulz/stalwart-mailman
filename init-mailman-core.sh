#!/bin/bash

.  .env

curl \
  -XPOST \
  --user restadmin:${MM3_MAILMAN_REST_PASSWORD} \
  -H"Content-Type: application/json" \
  http://${MM3_CORE_IP}:8001/3.1/domains \
  --data '{"mail_host": ${DOMAIN}, "description": ${DOMAIN}, "alias_domain": mail.${DOMAIN}}'
