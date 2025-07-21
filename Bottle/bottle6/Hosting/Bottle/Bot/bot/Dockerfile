FROM node:21-alpine

ENV LANG="C.UTF-8" PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

RUN apk update
RUN apk add --no-cache zlib-dev udev nss ca-certificates
RUN apk add --no-cache chromium
RUN adduser -h /home/bot -D -u 10086 bot
RUN yarn cache clean
RUN rm -rf /tmp/* /etc/apk/* /var/cache/apk/* /usr/share/man

WORKDIR /home/bot

COPY ./*.json ./

RUN npm install
RUN npm install -g pm2
COPY . .

USER bot

# CMD ["node", "/home/bot/index.js"]
CMD ["pm2", "start", "/home/bot/index.js", "--watch", "--no-daemon"]