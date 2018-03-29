#!/bin/bash -eux

echo "Copying template file..."
cp /etc/nginx/funkwhale_proxy.conf{.template,}
sed -i "s/X-Forwarded-Host \$host:\$server_port/X-Forwarded-Host localhost:${WEBPACK_DEVSERVER_PORT}/" /etc/nginx/funkwhale_proxy.conf
sed -i "s/proxy_set_header X-Forwarded-Port \$server_port/proxy_set_header X-Forwarded-Port ${WEBPACK_DEVSERVER_PORT}/" /etc/nginx/funkwhale_proxy.conf

cat /etc/nginx/funkwhale_proxy.conf
nginx -g "daemon off;"
