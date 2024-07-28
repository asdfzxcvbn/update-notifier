FROM docker.io/python:3.12-alpine

COPY src src

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "/src/update_notifier.py"]
