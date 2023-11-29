# Utilize the official Python image as a base
FROM python:3.9-slim-buster

RUN apt-get update && \
apt-get install -y libpq-dev gcc

# Set the working directory
WORKDIR /app

# Copy the necessary files
COPY ./requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

COPY . .

# Expose the port on which your FastAPI application listens
EXPOSE 8000

# Command to run your application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]