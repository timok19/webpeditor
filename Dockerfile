ARG PYTHON_VERSION=3.13-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app

WORKDIR /app

# Install uv for dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock requirements.txt /app/

# Install dependencies using uv
RUN uv pip install --system -r requirements.txt

COPY . /app

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne", "-b", "127.0.0.1", "-p", "8000", "webpeditor.asgi:application"]
