# otel-example

run using docker

```
docker build .
docker compose up
```

Data will start flowing into the kafka topics `otlp_spans, otlp_logs, otlp_metrics`

to consume the data into pinot you first need to get the public ip of the node running the docker compose. Then put that in the docker-compose.yml for the `KAFKA_ADVERTISED_LISTENERS`. Specifically the EXTERNAL listener. 

Once the containers are running, you will need to log into the startree pinot container and run the following command to create the tables in pinot. 

```bash
cd ~
/bin/sh /data/create-table.sh
```

Some of the places you will want to update paths from my local to your local. These need to be absolute paths:

```
docker-compose.yml
start-docker.sh
```