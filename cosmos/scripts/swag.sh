#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Generate Swagger documentation from source and verify annotations have not
# changed by checking if the swagger.yaml config is dirty or not.
make swagger
exit_status=$?

if [ $exit_status -ne 0 ]; then
    exit $exit_status
fi

if (($(git status --porcelain 2>/dev/null | grep 'server/docs/swagger.yaml' | wc -l) > 0)); then
  echo -e "${RED}Swagger docs are out of sync!!!${NC}"
  exit 1
else
  echo -e "${GREEN}Swagger docs are in sync${NC}"
fi