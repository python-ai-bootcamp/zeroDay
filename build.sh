#!/bin/bash
#mkdir -p ./shell_frontend/dist/
#rm -f ./shell_frontend/dist/main.tsx
#cp -rp ./shell_frontend/src/main.tsx ./shell_frontend/dist/
sed -i.bak -e 's/\(<AuthKeyProvider value="\).*\(">\)/\1\2/' -e 's/\(<ApiUrlProvider baseUrl="\).*\(">\)/\1https:\/\/www.zerodaybootcamp.xyz\2/' ./shell_frontend/src/main.tsx 
rm -f ./shell_frontend/dist/assets/index-*.css
rm -f ./shell_frontend/dist/assets/index-*.js
rm -f ./shell_frontend/dist/index.html
rm -f ./resources/static/assets/index-*.css
rm -f ./resources/static/assets/index-*.js
rm -f ./resources/static/index.html

pushd ./shell_frontend
npm run build
popd
cp ./shell_frontend/dist/assets/index-*.css ./resources/static/assets/
cp ./shell_frontend/dist/assets/index-*.js ./resources/static/assets/
cp ./shell_frontend/dist/index.html ./resources/static/

mv ./shell_frontend/src/main.tsx.bak ./shell_frontend/src/main.tsx
