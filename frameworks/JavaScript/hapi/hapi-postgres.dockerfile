FROM node:10.12.0

COPY ./ ./

RUN npm install

ENV NODE_HANDLER sequelize-postgres

CMD ["node", "app.js"]
