#!/bin/bash
start uvicorn --app-dir=src main:app --host 0.0.0.0 --port 8000 --log-config ./resources/config/logging.yaml
start uvicorn --app-dir=src assignmentOrchestrator:app --host 0.0.0.0 --port 9000
