# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости и pipenv
RUN apt-get update && \
    apt-get install -y libzbar0 libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir pipenv

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы Pipfile и Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Устанавливаем зависимости из Pipfile
RUN pipenv install --deploy --system && \
    rm -rf ~/.cache/pipenv

# Копируем остальные файлы проекта
COPY . .

# Открываем порт, который будет использовать приложение
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]