
```
запуск в докере
docker build -t downloader2json src/
docker run -v {folder save albums}:/code downloader2json 


poetry run downloader -h - help
poetry run downloader async_1  - run multithreading download
poetry run downloader async_2  - run async download

```


Реализовать парсер с сайта https://jsonplaceholder.typicode.com/ в несколько потоков или процессов, объекты albums/ и photos/.
https://jsonplaceholder.typicode.com/albums/
https://jsonplaceholder.typicode.com/photos/
Скачиваем все альбоы и фотографии, кладем их по папкам /альбом/название_фотографии

Требования:

Парсер реализовать на ООП, соблюдая SOLID.
Для соединения по http можно использовать https://docs.python-requests.org/en/latest/

Необходимо реализовать декоратор, для замера работы времени всего скрипта, необходимо реализовать декоратор для замера времени метода, который скачивает.