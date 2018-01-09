FROM node:9

EXPOSE 8080
WORKDIR /app/
ADD package.json .
RUN yarn install --only=production
RUN yarn install --only=dev
VOLUME ["/app/node_modules"]
COPY . .

CMD ["npm", "run", "dev"]
