# выкачиваем слак

## Как установить venv и зависимости:

```shell
python3 -m venv `pwd`/.venv
source ./.venv/bin/activate
python -m pip install -r requirements.txt
```

## Как получить токен приложения, под которым работать скачивание:

1. [Создать нове приложение в слаке](https://api.slack.com/apps?new_app=1)

2. Выдать ему следующие пермишены для `User Token Scopes` по ссылке https://api.slack.com/apps/{APP_ID}/oauth

````
channels:history
channels:read
files:read
groups:history
groups:read
im:history
im:read
mpim:history
mpim:read
remote_files:read
````

3. Скопировать `User OAuth Token`

## Как выкачать сообщения канала из слака:

Выставляем переменную окружения для чтения слака (можно передать и в сам скрипт параметром `-t`)

```shell
export SLACK_USER_TOKEN=xoxp-user-token-for-slack
```

Включаем музыку

```
https://music.yandex.ru/album/4784938/track/37699817
```

Запускаем скрипт в первый раз. В случае падения можно повторить - скрипт попробует продолжить с упавшего места.

```shell
python run.py load_channel -c hh-dev -l 1000 -d both
```

Если скрипт пишет `no messages found` - значит вся история в прошлое скачана

Скачивать можно в два направления.

В прошлое с места последней остановки:

```shell
python run.py load_channel -c hh-dev -l 1000 -d down
```

В прошлое с места последней остановки:

```shell
python run.py load_channel -c hh-dev -l 1000 -d up
```

И в прошлое и в будущее с места последнй остановки

```shell
python run.py load_channel -c hh-dev -l 1000 -d both
```

Скачанные данные скрипт хранит в папке заданной переменной окружения `SLACK_EXPORT_ROOT_PATH` (поддерживается только абсолютный путь), либо `~/slack_export` в случае, если переменная не задана.

## После выкачивания сообщений из чата, можно выкачать прилинкованные к ним файлы

```shell
python run.py download_files -c hh-dev -cc 4
```
