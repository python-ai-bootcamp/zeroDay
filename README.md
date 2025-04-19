
# install app in lab mode:
install all prod dependencies
```bash
pip install -r requirements.txt
```
install additional test dependencies
```bash
pip install -r requirements_test.txt
```
# run front end in lab mode
```bash
cd shell_frontend
npm run dev
```
# execute app in lab mode:
UI only
```bash
start uvicorn --app-dir=src main:app --host 0.0.0.0 --port 8000 --log-config ./resources/config/logging.yaml
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

# windows os dependencies
for app to work on windows following os dependencies needs to be installed manually
```bash
choco install docker-desktop
```
install 64bit version of gtk runtime for windows (64!!!!!)
```bash
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
```
then add following directory into your path
```bash
C:\Program Files\GTK3-Runtime Win64\bin\
```

for redhat, everything should be covered by the installService.sh script

