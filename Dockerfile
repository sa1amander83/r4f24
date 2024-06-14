# Use an official Python runtime as a parent image
FROM python:3.10-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && apk add jpeg-dev zlib-dev libjpeg \
    && apk add --no-cache mariadb-connector-c-dev

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Copy project files to the container
COPY . /r4f
WORKDIR /r4f

# Collect static files
RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations



# Expose port 8000 to allow communication to/from the server
EXPOSE 8000

# Start the main process (Django)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "r4f24.wsgi:application"]

#docker build -t r4f24 .
#docker run -p 8000:8000 r4f24
