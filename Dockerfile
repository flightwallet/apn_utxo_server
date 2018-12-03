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

# install
RUN curl -O https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh
RUN bash Miniconda2-latest-Linux-x86_64.sh -b -p /root/miniconda && rm Miniconda2-latest-Linux-x86_64.sh

# activate
ENV PATH /root/miniconda/bin:$PATH
RUN conda update -n base conda
RUN pip install --upgrade pip

# nvm environment variables
ENV NVM_DIR /root/nvm
ENV NODE_VERSION 8
# install nvm
# https://github.com/creationix/nvm#install-script
RUN mkdir NVM_DIR
RUN curl --silent -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash

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

RUN npm install -g bitcore && bitcore create mynode --testnet && cd mynode && bitcore install insight-api && bitcore install insight-ui

# RUN useradd -r -m bitcore && sudo su - bitcore

