#!/bin/bash

./bin/startree-pinot-admin.sh AddTable \
-schemaFile /data/metrics-schema.json \
-tableConfigFile /data/metrics-table.json \
-exec

./bin/startree-pinot-admin.sh AddTable \
-schemaFile /data/logs-schema.json \
-tableConfigFile /data/logs-table.json \
-exec

./bin/startree-pinot-admin.sh AddTable \
-schemaFile /data/traces-schema.json \
-tableConfigFile /data/traces-table.json \
-exec