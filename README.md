# postgres-trigger-replication

Demonstrates replication of a table in Postgres to Elastic Search using
Postgres trigger functions, NOTIFY and a process listening for change
notifications to sync to Elastic.

## Setup

Docker:

    cd docker
    docker-compose build

Python:

    python bootstrap.py
    ./bin/buildout


## Test

Docker (all containers must be running):

     cd docker
     docker-compose up -d

Python

     ./bin/py.test src/ptr-integration -s

## TODOs

- If no process is listening to Postgres' notifications they are dropped.
  In order to fix, write notifications to a new table so that these can
  be processed if the sync process goes offline and starts up again.
