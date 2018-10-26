#!/bin/bash
mkdir $(pwd)/postgres_db
docker run -dit --name ctPostgres -p 5432:5432 -v $(pwd)/postgres_db:/var/lib/postgresql/data \
  -e POSTGRES_DB=ct -e POSTGRES_USER=ct postgres:11-alpine
