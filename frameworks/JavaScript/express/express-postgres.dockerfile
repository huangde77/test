FROM node:14.15.5-slim

COPY ./ ./

RUN npm install

ENV NODE_ENV production

EXPOSE 8080

CMD ["node", "postgresql-app.js"]
