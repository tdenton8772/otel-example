# otel-example

run using docker

```
docker compose up
```

Data will start flowing into the kafka topics `otlp_spans, otlp_logs, otlp_metrics`

to consume the data into pinot you first need to get the public ip of the node running the docker compose. Then put that in the docker-compose.yml for the `KAFKA_ADVERTISED_LISTENERS`. Specifically the EXTERNAL listener. 