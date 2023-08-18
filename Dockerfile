FROM node:latest

# https://mirrors.ustc.edu.cn/help/debian.html
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update
RUN apt-get -y upgrade

RUN apt-get install -y --reinstall ca-certificates
RUN apt-get install -y apt-utils
RUN apt-get install -y python3 python3-pip build-essential

RUN mkdir /Lires
WORKDIR /

COPY . /Lires
WORKDIR /Lires/lires_web 
# RUN npm config set registry https://registry.npm.taobao.org
RUN npm install -g cnpm --registry=https://registry.npm.taobao.org
RUN cnpm install && cnpm run build

WORKDIR /

# https://mirrors.tuna.tsinghua.edu.cn/help/pypi/
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# https://stackoverflow.com/a/75722775/6775765
RUN python3 -m pip install --upgrade pip --break-system-packages
RUN pip3 install -e /Lires/packages/tiny_vectordb --break-system-packages
RUN pip3 install -e /Lires[ai] --break-system-packages

EXPOSE 8081
EXPOSE 8080
EXPOSE 8731

ENV HF_HOME=/root/.Lires/hf_home
ENTRYPOINT ["lires", "server"]