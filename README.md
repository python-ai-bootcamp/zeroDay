
# install app in lab mode:
install all prod dependencies
```bash
pip install -r requirements.txt
```
install additional test dependencies
```bash
pip install -r requirements_test.txt
```

# execute app in lab mode:
UI only
```bash
start uvicorn --app-dir=src main:app --host 0.0.0.0 --port 8000
```
assignmentOrchestrator backend only
```bash
start uvicorn --app-dir=src assignmentOrchestrator:app --host 0.0.0.0 --port 9000
```
execute both UI and assignmentOrchestrator ocally oln windows machine
```bash
./startLocally.sh
```

# execute tests:
without coverage
```bash
pytest
```
with coverage
```bash
./covtest.sh
```

# production scripts
to redeploy code
first push to main branch on github
then enter the /opt/zeroDay/ directory on zerodaybootcamp.xyz and execute following script
```bash
./redeploy.sh
```
in case something was changed with dependencies and/or the actual service installation enter /opt/zeroDay/
then run the following commands:
```bash
./redeploy.sh
cd $PWD
./installService.sh
```

