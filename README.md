```
$ docker network create elastic
$ docker pull elasticsearch:8.14.0

$ source .env
$ docker run -v ${SETTINGS_PATH}:/usr/share/elasticsearch/config/dicts --name elastic_${NAME} -p ${ELASTIC_PORT}:9200 -e "discovery.type=single-node" -e ES_JAVA_OPTS="-Xms1g -Xmx1g" elasticsearch:8.14.0

$ docker exec -it 860 /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
copy password to .env file ELASTIC_PASSWORD
$ docker cp 860:/usr/share/elasticsearch/config/certs/http_ca.crt ./src/elastic/certs/

$ source .env
```
