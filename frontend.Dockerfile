FROM node:16.16-bullseye

WORKDIR /app

COPY package-lock.json package.json .
RUN npm ci

CMD ["sleep", "infinity"]
