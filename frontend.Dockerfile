FROM node:16.16-bullseye-slim

WORKDIR /app

COPY package-lock.json package.json .
RUN npm ci

CMD ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
