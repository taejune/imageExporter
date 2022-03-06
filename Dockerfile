FROM node:16.14-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN chmod 700 archive-upload.sh

EXPOSE 3000

CMD ["npm", "start"]