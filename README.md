Установка пакетів: `pip install -r requirements.txt`. Один з пакетів хоститься на CDN Яндекса, 
тому необхідно включити VPN.

Скачати це все можливо, виконавши скрипт `make download`. Потім препроцессінг `make preprocess`.
Запуск: `make server`.

Якщо ви змінили набір пакетів, треба:

1. Додати новий пакет в `./requirements.txt` та `./docker/Dockerfile`
2. Збілдити образ `docker build -t tsdaemon/classic-python .`
3. Запушити образ `docker push tsdaemon/classic-python`



