
```
запуск в докере
docker build -t downloader2json src/
docker run -v {folder save albums}:/code downloader2json 


poetry run downloader -h - help
poetry run downloader

```


Реализовать парсер с сайта https://jsonplaceholder.typicode.com/ в несколько потоков или процессов, объекты albums/ и photos/.
https://jsonplaceholder.typicode.com/albums/
https://jsonplaceholder.typicode.com/photos/
Скачиваем все альбомы и фотографии, кладем их по папкам /альбом/название_фотографии