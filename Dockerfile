FROM node:16.14-alpine

RUN apk add --no-cache openssh sshpass

WORKDIR /app
COPY . .
RUN npm install
RUN chmod 700 archive-upload.sh

EXPOSE 3000

CMD ["npm", "start"]