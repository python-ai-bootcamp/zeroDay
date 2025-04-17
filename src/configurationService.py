import os
from systemEntities import print
domain_name = os.environ.get('DOMAIN_NAME', "127.0.0.1:8000")
print(domain_name)
protocol = "https" if os.environ.get('DOMAIN_NAME') else "http"
print(protocol)
isDevMod = "false" if os.environ.get('DOMAIN_NAME') else "true"
