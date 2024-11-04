# Базовый образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем временную зону на Киев
ENV TZ=Europe/Kiev

# Обновляем пакеты и устанавливаем tzdata для изменения временной зоны
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем файлы requirements.txt и устанавливаем зависимости
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Открываем порт для доступа к FastAPI-приложению
EXPOSE 8000

# Команда для запуска приложения
CMD ["python", "main.py"]