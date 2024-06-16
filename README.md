## Installation

Для начала надо установить все зависимости. Все запускалось на Python 3.9.19 (на сервере с GPU на 3.10.14). Желательно изолировать среду выполнения, например через pipenv, conda (использовалось на сервере с GPU - `requirements_gpu.txt`), etc.

```bash
pip3 install -r requirements.txt
```

Настроить Docker и скачать нужную версию эластика. (Если команду `docker` возможно выполнить только с командой `sudo`, то мб проблемы с правами к файлам когда запускается приложение fastapi. Придется выполнять `sudo chmod 755 src/elastic/certs` и т.д.)

```bash
docker network create elastic
docker pull elasticsearch:8.14.0
```

Далее надо заполнить все переменные окружения в файле .env. Затем подтянуть их. Этот файл лучше хранить локально.

```bash
source .env
```

Запустить эластик, находясь в root папке проекта. (в отдельном терминале)

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

С корня проекта поднять RestAPI приложения на fastapi. (в отдельном терминале)
```bash
python3 -m src.start
```

Если хочется добавить удобное демо для поиска и подсказок на streamlit. (в отдельном терминале)
```bash
streamlit run src/app_streamlit.py --server.port=8501
```

## How to use

Идем в http://0.0.0.0:8080/docs - там примеры. 
Если не разворачивать локально, а обратиться к нашему прототипы это: 
 - http://66.151.35.150:8080 - fastapi
 - http://66.151.35.150:8501 - streamlit

Примеры запросов к сервису: `notebooks/requests.ipynb`.

## License

[MIT](https://choosealicense.com/licenses/mit/)
