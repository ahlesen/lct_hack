```
source .env
docker pull elasticsearch:8.14.0
docker run -v ${SETTINGS_PATH}:/usr/share/elasticsearch/config/dicts --name elastic_${NAME} -p ${ELASTIC_PORT}:9200 -e "discovery.type=single-node" -e ES_JAVA_OPTS="-Xms1g -Xmx1g" elasticsearch:8.14.0
docker exec -it 37d /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
docker cp <DOCKER_CONTAINER_HASH>:/usr/share/elasticsearch/config/certs/http_ca.crt ./elastic/certs/
```
description = [description, tags_from_llama, shazam] -> embedding

whisper - today 
shazam - mne toje zapusk (5k examples)
image_caption - null ~5k (без него скорее всего)
