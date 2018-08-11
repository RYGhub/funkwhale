#!/bin/bash -eux

FORWARDED_PORT="$VUE_PORT"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME// /}"
if [ -n "$COMPOSE_PROJECT_NAME" ]; then
  echo
    FUNKWHALE_HOSTNAME="$COMPOSE_PROJECT_NAME.funkwhale.test"
    FORWARDED_PORT="443"
fi
echo "Copying template file..."
cp /etc/nginx/funkwhale_proxy.conf{.template,}
sed -i "s/X-Forwarded-Host \$host:\$server_port/X-Forwarded-Host ${FUNKWHALE_HOSTNAME}:${FORWARDED_PORT}/" /etc/nginx/funkwhale_proxy.conf
sed -i "s/proxy_set_header Host \$host/proxy_set_header Host ${FUNKWHALE_HOSTNAME}/" /etc/nginx/funkwhale_proxy.conf
sed -i "s/proxy_set_header X-Forwarded-Port \$server_port/proxy_set_header X-Forwarded-Port ${FORWARDED_PORT}/" /etc/nginx/funkwhale_proxy.conf
sed -i "s/proxy_set_header X-Forwarded-Proto \$scheme/proxy_set_header X-Forwarded-Proto ${FORWARDED_PROTO}/" /etc/nginx/funkwhale_proxy.conf

cat /etc/nginx/funkwhale_proxy.conf
nginx -g "daemon off;"
