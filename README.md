
Перейти в каталог проекта
```
short-linker
```

Установить зависимости
```
uv sync
```

Активировать окружение проекта
```
source .venv/bin/activate
```

Подготовить БД к работе
```
python -m scripts.init_db
```

Запуск проекта
```
uvicorn main:app
```

http://127.0.0.1:8000/docs - Swagger документация API

Запуск тестов
```
uv run pytest
```
