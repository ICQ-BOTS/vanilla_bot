# [Генератор ванили](https://icq.im/Vanilla_bot)

<a href="https://icq.im/Vanilla_bot"><img src="https://github.com/ICQ-BOTS/vanilla_bot/blob/main/blanket.png" width="100" height="100"></a>


# Оглавление 
 - [Описание](https://github.com/ICQ-BOTS/vanilla_bot#описание)
 - [Установка](https://github.com/ICQ-BOTS/vanilla_bot#установка)
 - [Скриншоты работы](https://github.com/ICQ-BOTS/vanilla_bot#скриншоты-работы)

# Описание
В моем электронном мозгу тысячи ванильных цитат из интернета.

# Установка

1. Установка всех зависимостей 
```bash
pip3 install -r requirements.txt
```

2. Запуск space tarantool.
```bash
tarantoolctl start init.lua
```
> Файл из папки scheme нужно перекинуть в /etc/tarantool/instances.available

3. Вставляем свои данные в config.ini - токен

4. Запуск бота!
```bash
python3 vanilla_bot.py
```

# Скриншоты работы
<img src="https://github.com/ICQ-BOTS/vanilla_bot/blob/main/img/1.png" width="400">
<img src="https://github.com/ICQ-BOTS/vanilla_bot/blob/main/img/2.png" width="400">
