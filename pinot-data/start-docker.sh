docker run \
    -p 2123:2123 \
    -p 9000:9000 \
    -p 8000:8000 \
    -p 7050:7050 \
    -p 19092:19092 \
    -p 6000:6000 \
    --platform linux/amd64 \
    -v /Users/tdenton/Development/autonation/otel-example/pinot-data:/data \
    repo.startreedata.io/external-docker-registry/startree-metrics-agent:otel-auto-nation-demo-dec-13 \
    StarTreeQuickStart -type OTEL_COLLECTOR

