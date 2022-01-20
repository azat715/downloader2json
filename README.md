
Использование 
NAME
    downloader

SYNOPSIS
    downloader COMMAND

COMMANDS
    COMMAND is one of the following:

     async_1
       run multithreading download

     async_2
       run async download


Реализовать парсер с сайта https://jsonplaceholder.typicode.com/ в несколько потоков или процессов, объекты albums/ и photos/.
https://jsonplaceholder.typicode.com/albums/
https://jsonplaceholder.typicode.com/photos/
Скачиваем все альбоы и фотографии, кладем их по папкам /альбом/название_фотографии

Требования:

Парсер реализовать на ООП, соблюдая SOLID.
Для соединения по http можно использовать https://docs.python-requests.org/en/latest/

Необходимо реализовать декоратор, для замера работы времени всего скрипта, необходимо реализовать декоратор для замера времени метода, который скачивает.

10 воркеров
2022-01-08 23:52:21.336 | DEBUG    | __main__:run:109 - загружены фотки
2022-01-08 23:52:22.835 | INFO     | __main__:main:127 - Загрузка завершена за 195.0691420000221

100 воркеров
2022-01-09 00:18:55.465 | DEBUG    | __main__:run:109 - загружены фотки
2022-01-09 00:18:55.879 | INFO     | __main__:main:127 - Загрузка завершена за 31.213502500002505
________________________________________________________
Executed in   32.00 secs   fish           external
   usr time   65.06 secs  279.00 micros   65.06 secs
   sys time    9.67 secs  305.00 micros    9.67 secs


иногда банит сайт 
raise ConnectionError(e, request=request)
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='jsonplaceholder.typicode.com', port=443): Max retries exceeded with url: /albums/ (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7fb117a9e100>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution'))