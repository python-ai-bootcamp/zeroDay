
# install all prod dependencies
```bash
pip install -r requirements.txt
```

# install additional test dependencies
```bash
pip install -r requirements_test.txt
```

# to execute UI
```bash
start uvicorn --app-dir=src main:app --host 0.0.0.0 --port 8000
```

# to execute assignmentOrchestrator
```bash
start uvicorn --app-dir=src assignmentOrchestrator:app --host 0.0.0.0 --port 9000
```

# to execute both locally on windows machine
```bash
./startLocally.sh
```