FROM ubuntu:18.04
MAINTAINER Vladislav Belavin <belavin@phystech.edu>

# update
RUN apt-get -y update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:gophers/archive && \
    apt-get -y update && \
    apt-get install -y --no-install-recommends apt-utils curl \
    bzip2 gcc git wget g++ build-essential libc6-dev make pkg-config \
    golang-1.10-go libzmq3-dev

# install python
RUN curl -O https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh && bash Miniconda2-latest-Linux-x86_64.sh -b -p /root/miniconda && rm Miniconda2-latest-Linux-x86_64.sh
ENV PATH /root/miniconda/bin:$PATH
RUN conda update -n base conda
RUN pip install --upgrade pip

# nvm environment variables
ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION 8

# install nvm
# https://github.com/creationix/nvm#install-script
RUN curl --silent -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.2/install.sh | bash

# install node and npm
RUN source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

# add node and npm to path so the commands are available
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

# confirm installation
RUN node -v
RUN npm -v

# MongoDB
RUN sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4 && \
    echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list && \
    sudo apt-get update &&  sudo apt-get install -y mongodb-org
# sudo mongod --fork --logpath /var/log/mongodb.log
pip install uwsgi

# redis
RUN wget http://download.redis.io/redis-stable.tar.gz && tar xvzf redis-stable.tar.gz && cd redis-stable && \
    make && make install && cd .. && rm redis-stable.tar.gz && rm -rf redis-stable
# redis-server --daemonize yes

# apns python
RUN pip install gobiko.apns

# bitcore
RUN npm install -g bitcore && bitcore install -g insight-api && bitcore -g install insight-ui

WORKDIR /root/mynode
# TODO: volumes for bitcore and MongoDB
ENTRYPOINT ["nohup", "bitcore", "start", ">log.log", "&"]