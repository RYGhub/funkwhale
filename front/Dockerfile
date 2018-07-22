FROM node:9

# needed to compile translations
RUN curl -L -o /usr/local/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 && chmod +x /usr/local/bin/jq

EXPOSE 8080
WORKDIR /app/
ADD package.json .
RUN yarn install

COPY . .

CMD ["npm", "run", "dev"]
