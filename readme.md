# выкачиваем слак

## Как установить venv и зависимости:

```shell
python3 -m venv `pwd`/.venv
source ./.venv/bin/activate
python -m pip install -r requirements.txt
```

## Как выкачать канал из слака:

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

Скачанные данные скрипт хранит в папке заданной переменной окружения `SLACK_EXPORT_ROOT_PATH`, либо `~/slack_export` в
случае, если переменная не задана.
