#!/bin/bash

curl \
  --user admin:password \
  -XPOST \
  http://mail-server:8080/api/principal \
  --data '{"type": "domain", "name": "example.com", "description": "Example domain"}'

curl \
  --user admin:password \
  -XPOST \
  http://mail-server:8080/api/principal \
  --data '{"type": "individual", "name": "root@example.com", "description": "postmaster"}'

curl \
  --user admin:password \
  -XPATCH \
  http://mail-server:8080/api/principal/root%40example.com \
  --data '[{"action":"addItem","field":"secrets","value":"$6$ygS2f7mNlvvzeakW$KS/r6LWMlSWzT7Pi8uv2iGqK2E5npnPHd/41xW3qxYWNGbrSKGwSwjmhc7wTplolqjuM40TKH.8thwJ8rqXfi1"}]'

curl \
  --user admin:password \
  -XPOST \
  http://mail-server:8080/api/settings \
  --data '[{"type":"clear","prefix":"queue.limiter.inbound."}]'

curl \
  --user admin:password \
  -XGET \
  http://mail-server:8080/api/reload/
