FROM node:14.5.0-slim

COPY ./ ./

RUN npm install

ENV NODE_ENV production
ENV DATABASE mongo

CMD ["node", "app.js"]
