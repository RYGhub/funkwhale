FROM node:6

EXPOSE 8080
WORKDIR /app/
ADD package.json .
RUN npm install --only=production
RUN npm install --only=dev
VOLUME ["/app/node_modules"]
COPY . .

CMD ["npm", "run", "dev"]
