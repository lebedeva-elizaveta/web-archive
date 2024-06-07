FROM python:3.11.1-slim

# set work directory
WORKDIR .

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Set the environment variable for Gunicorn temporary files
ENV TMPDIR=/var/tmp

CMD ["flask", "run", "--host=0.0.0.0"]
