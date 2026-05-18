# Берем официальный легкий образ Python
FROM python:3.10-slim

# Запрещаем питону писать кэш-файлы и буферизировать вывод
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем папку /app внутри контейнера
WORKDIR /app

# Копируем список зависимостей и устанавливаем их
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --default-timeout=1000 -r requirements.txt

# Копируем весь остальной код
COPY . /app/

# Запускаем сервер Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]