ARG PYTHON_VERSION=3.12-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y cron

RUN mkdir -p /app

WORKDIR /app

RUN pip install poetry
RUN poetry install --no-dev --no-interaction --no-ansi

COPY pyproject.toml poetry.lock /app/

COPY . /app

RUN python manage.py collectstatic --noinput

# Add the cron job for running the Django management command every day
RUN echo "0 0 * * * /usr/local/bin/python /app/manage.py runjobs daily >> /var/log/cron.log 2>&1" > /etc/cron.d/django-cron
RUN chmod 0644 /etc/cron.d/django-cron
RUN crontab /etc/cron.d/django-cron

RUN touch /var/log/cron.log

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "webpeditor.wsgi"]
