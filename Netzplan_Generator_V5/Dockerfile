FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Graphviz wird für die SVG-Erzeugung benötigt.
RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY api.py .
COPY main.py .
COPY netzplan ./netzplan
COPY ausgaben/.gitkeep ./ausgaben/.gitkeep
RUN mkdir -p ausgaben

EXPOSE 8000
CMD ["python", "api.py"]
