# downloader2json

## Общий функционал

Загрузка фотографий с сайта https://jsonplaceholder.typicode.com

## Запуск

```
запуск в докере
docker-compose up
```

## Основные технологии

Использован паттерн Worker pool (asyncio.Queue)

## Структура приложения

src/downloader/main.py - основная логика скрипта 

src/downloader/models.py - pydantic модели для парсинга json
