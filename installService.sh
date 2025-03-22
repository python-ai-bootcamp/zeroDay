#!/bin/bash

#solving of some weird nginx issue with selinux taken from here https://stackoverflow.com/questions/23948527/13-permission-denied-while-connecting-to-upstreamnginx
sudo setsebool -P httpd_can_network_connect 1

#uninstall previous configurative items
yum remove nginx -y
rm -rf /etc/nginx
sudo rm -rf /opt/certbot

#install needed dependencies for service
yum install python3.12 -y
pip install -r requirements.txt
yum install nginx -y 
yum install augeas-libs -y

#configure python to work with python3.12
ls -sf /usr/bin/python3.12  /usr/bin/python3
ls -sf /usr/bin/pydoc3.12  /usr/bin/pydoc3

#configure nginx to work with backend using http
cp /etc/nginx/nginx.conf /opt/
startOfNginxConfFile=`cat /etc/nginx/nginx.conf|grep "include /etc/nginx/conf.d/.*conf;" -B5000 -A1`
echo "$startOfNginxConfFile">/etc/nginx/nginx.conf
cat <<EOF >> /etc/nginx/nginx.conf
    server {
        listen       80;
        listen       [::]:80;
        server_name  zerodaybootcamp.xyz;
        location / {
                proxy_pass http://0.0.0.0:8000/;
        }
    }
}
EOF
service nginx restart


#install certbot
sudo python3 -m venv /opt/certbot/
sudo /opt/certbot/bin/pip install --upgrade pip
sudo /opt/certbot/bin/pip install certbot certbot-nginx
sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot
sudo certbot -n --nginx --domains="zerodaybootcamp.xyz" #still neet to set nginx server_name directive

renewCertificateLineExist=`crontab -luroot|grep renewCertificate.sh|wc -l`
if [ "${renewCertificateLineExist}" == "0" ];
then
	(crontab -l 2>/dev/null; echo "0 5 1 * * root /opt/zeroDay/renewCertificate.sh") | crontab - ;
fi

#set up the zeroDay service
mkdir -p /opt/logs
service zeroDay stop

cat <<EOF > /lib/systemd/system/zeroDay.service
[Unit]
Description=zeroDay webapp service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/zeroDay/
ExecStart= /bin/sh -c 'DOMAIN_NAME="zerodaybootcamp.xyz" /usr/local/bin/uvicorn --app-dir=src main:app --host 0.0.0.0 --port 8000 2>&1 >> /opt/logs/zeroDay_\$\$(date +%%Y_%%m_%%d__%%H_%%M_%%S).log'
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
sudo systemctl enable zeroDay
service zeroDay start
