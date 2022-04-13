FROM node:16.14.2-slim

COPY ./ ./

RUN npm install

ENV NODE_HANDLER sequelize

EXPOSE 8080

CMD ["node", "app.js"]
