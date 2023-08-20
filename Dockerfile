## First stage, build the web app
FROM node:20 as webapp-build

RUN mkdir /Lires
WORKDIR /

COPY . /Lires
WORKDIR /Lires/lires_web 
RUN npm install -g cnpm --registry=https://registry.npm.taobao.org
RUN cnpm install && cnpm run build


## Second stage, build the server
FROM python:3.11-bookworm as server-build
COPY --from=webapp-build /Lires /Lires
WORKDIR /

# https://mirrors.ustc.edu.cn/help/debian.html
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources

# RUN apt-get update
# RUN apt-get -y upgrade
# RUN apt-get install -y --reinstall ca-certificates
# RUN apt-get install -y apt-utils
# RUN apt-get install -y build-essential

# https://mirrors.tuna.tsinghua.edu.cn/help/pypi/
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# https://stackoverflow.com/a/75722775/6775765
RUN python3 -m pip install --upgrade pip --break-system-packages
RUN pip3 install /Lires/packages/tiny_vectordb --break-system-packages
RUN pip3 install -e /Lires[ai] --break-system-packages

EXPOSE 8081
EXPOSE 8080
EXPOSE 8731

ENV HF_HOME=/root/.Lires/hf_home
ENTRYPOINT ["lrs-cluster", "/root/.Lires/container-cluster-config.yaml", "--init-if-not-exist"]