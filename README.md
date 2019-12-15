# asin-jan-converter

I tried to convert ASIN to JAN without Amazon API.

## Setup

```console
$ cp .env.example .env
$ vi .env
$ ./setup.sh
$ docker-compose build
```

## Launch

```console
$ docker-compose up -d
```

## Run

```console
$ docker-compose exec webapp bash
$ python3 main.py jancode -A B01G6XNQ5A
```

