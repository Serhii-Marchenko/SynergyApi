# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Установим зависимость для работы с часовыми поясами
RUN apt-get update && apt-get install -y tzdata

# Установим часовой пояс на Киев (Europe/Kiev)
ENV TZ=Europe/Kiev

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the FastAPI app will run on
EXPOSE 5057

# Run the FastAPI app using uvicorn when the container starts
CMD ["python", "main.py"]