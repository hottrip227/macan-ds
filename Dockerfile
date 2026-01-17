FROM python:3.10

# Устанавливаем ffmpeg для работы музыки
RUN apt-get update && apt-get install -y ffmpeg
pip install -q -U google-genai

# Создаем рабочую папку
WORKDIR /app

# Копируем список библиотек и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код бота
COPY . .

# Команда для запуска
CMD ["python", "main.py"]
