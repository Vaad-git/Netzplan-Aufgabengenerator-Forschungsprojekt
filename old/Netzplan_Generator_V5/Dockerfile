FROM python:3.12-slim

# Graphviz wird als Systemprogramm benötigt. Python-Pakete sind nicht nötig.
RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN mkdir -p ausgaben

EXPOSE 8000
CMD ["python", "api.py"]
