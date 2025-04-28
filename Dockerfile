# Hier "borgen" wir das offizielle Python-Image
FROM python:3.10

# Das hier definiert wo unsere App "bearbeitet" wird
WORKDIR /app

# Die richtigen Dateien noch in den Container kopieren
COPY webhook.py .
COPY requirements.txt .

# Die Abhängigkeiten installieren
RUN pip install -r requirements.txt

# Und hier führen wir das Skript aus
CMD ["python", "webhook.py"]