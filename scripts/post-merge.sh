#!/bin/bash
set -e
pnpm install --frozen-lockfile
pnpm --filter db push
python3 -m pip install -r artifacts/api-server/python/requirements.txt --quiet
