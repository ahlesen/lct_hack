```
source .env
docker network create elastic
docker pull elasticsearch:8.14.0
docker run -v ${SETTINGS_PATH}:/usr/share/elasticsearch/config/dicts --name elastic_${NAME} -p ${ELASTIC_PORT}:9200 -e "discovery.type=single-node" -e ES_JAVA_OPTS="-Xms1g -Xmx1g" elasticsearch:8.14.0
docker exec -it 996 /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
docker cp 996:/usr/share/elasticsearch/config/certs/http_ca.crt ./src/elastic/certs/
```
