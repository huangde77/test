FROM syou/v-dev:latest

WORKDIR /app

COPY ./main.v run.sh ./

RUN git clone https://github.com/S-YOU/pico.v src && cd src && git checkout dev \
    && cd /app/src/picoev && git clone https://github.com/S-YOU/picoev src && cd src && git checkout dev \
    && cd /app/src/picohttpparser && git clone https://github.com/S-YOU/picohttpparser src && cd src && git checkout dev \
    && ln -s /app/src /root/.vmodules/syou \
    && cd /app && v -prod -cflags '-std=gnu11 -Wall -O3 -march=native -mtune=native -flto' main.v

CMD sh run.sh
