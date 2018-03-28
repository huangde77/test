FROM techempower/nginx:0.1

RUN apt install -yqq libgcrypt11-dev cmake python

WORKDIR /installs

#http://cppcms.com/wikipp/en/page/cppcms_1x_build
#note '-rc1' in the url
ENV CPPCMS_VERSION=1.1.1
ENV BACKNAME=cppcms
ENV CPPCMS_HOME=/installs/$BACKNAME-$CPPCMS_VERSION
ENV CPPCMSROOT=${CPPCMS_HOME}-install

RUN wget -q https://download.sourceforge.net/project/cppcms/$BACKNAME/$CPPCMS_VERSION-rc1/$BACKNAME-$CPPCMS_VERSION.tar.bz2
RUN tar xf $BACKNAME-$CPPCMS_VERSION.tar.bz2

RUN cd $BACKNAME-$CPPCMS_VERSION && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=${CPPCMSROOT} .. && \
    make && make install

ENV CPPCMS_HOME=${CPPCMSROOT}


ENV CPPDB_VERSION=0.3.1
ENV BACKNAME=cppdb
ENV CPPDB_HOME=/installs/$BACKNAME-$CPPDB_VERSION
ENV CPPDBROOT=${CPPDB_HOME}-install

RUN wget -q https://download.sourceforge.net/project/cppcms/$BACKNAME/$CPPDB_VERSION/$BACKNAME-$CPPDB_VERSION.tar.bz2
RUN tar xf $BACKNAME-$CPPDB_VERSION.tar.bz2

RUN cd $BACKNAME-$CPPDB_VERSION && \
    mkdir build && cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=${CPPDBROOT} .. && \
    make && make install

ENV CPPDB_HOME=${CPPDBROOT}

ADD ./ /cppcms
WORKDIR /cppcms

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${CPPCMS_HOME}/lib:${CPPDB_HOME}/lib

RUN make
