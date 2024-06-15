## Installation

Для начала надо установить все зависимости. Все запускалось на Python 3.9.19. Желательно изолировать среду выполнения, например через pipenv, conda, etc.

```bash
pip3 install -r requirements.txt
```

Настроить Docker и скачать нужную версию эластика.

```bash
docker network create elastic
docker pull elasticsearch:8.14.0
```

Далее надо заполнить все переменные окружения в файле .env. Затем подтянуть их. Этот файл лучше хранить локально.

```bash
source .env
```

Запустить эластик, находясь в root папке проекта.

```bash
docker run -v ${SETTINGS_PATH}:/usr/share/elasticsearch/config/dicts --name elastic_${NAME} -p ${ELASTIC_PORT}:9200 -e "discovery.type=single-node" -e ES_JAVA_OPTS="-Xms1g -Xmx1g" elasticsearch:8.14.0
```

Выдернуть креды эластика, находясь в root папке проекта. После вызовы внизу появится пароль, его необходимо скопировать в файл .env в переменную ELASTIC_PASSWORD. CONTAINER_HASH - хэш названия докер-контейнера.

```bash
docker exec -it ${CONTAINER_HASH} /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
```

После того как заполнили поле ELASTIC_PASSWORD, делаем еще раз source.

```bash
source .env
```

Положить файл сертификата в папку certs. CONTAINER_HASH - хэш названия докер-контейнера.

```bash
docker cp ${CONTAINER_HASH}:/usr/share/elasticsearch/config/certs/http_ca.crt ./src/elastic/certs/
```

С корня проекта поднять приложение.
```bash
python3 -m src.start
```

## License

[MIT](https://choosealicense.com/licenses/mit/)