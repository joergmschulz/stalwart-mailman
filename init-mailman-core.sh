#!/bin/bash

curl \
  -XPOST \
  --user restadmin:restpass \
  -H"Content-Type: application/json" \
  http://mailman-core:8001/3.1/domains \
  --data '{"mail_host": "example.com", "description": "Example Domain", "alias_domain": "x.example.com"}'
