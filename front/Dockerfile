FROM node:9

EXPOSE 8080
WORKDIR /app/
ADD package.json .
RUN yarn install

COPY . .

CMD ["npm", "run", "dev"]
