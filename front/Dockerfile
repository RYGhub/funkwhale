FROM node:9

EXPOSE 8080
WORKDIR /app/
ADD package.json .
RUN yarn install
VOLUME ["/app/node_modules"]
COPY . .

CMD ["npm", "run", "dev"]
