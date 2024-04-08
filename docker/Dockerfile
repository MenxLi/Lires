## First stage, build the web app
FROM node:20 as webapp-build

RUN mkdir /Lires
WORKDIR /

COPY . /Lires

WORKDIR /Lires/docs
RUN npm install && npm run build

WORKDIR /Lires/lires_web 
# RUN npm install -g cnpm --registry=https://registry.npm.taobao.org
# RUN cnpm install && cnpm run build
RUN npm install && npm run build

## Second stage, build the server
FROM python:3.11-bookworm as server-build
COPY --from=webapp-build /Lires /Lires
WORKDIR /

# https://mirrors.ustc.edu.cn/help/debian.html
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources

# https://mirrors.tuna.tsinghua.edu.cn/help/pypi/
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# https://stackoverflow.com/a/75722775/6775765
RUN python3 -m pip install --upgrade pip --break-system-packages
RUN pip3 install -e /Lires[all] --break-system-packages

EXPOSE 8080 
EXPOSE 8700
EXPOSE 21000-22000
ENV LRS_HOME=/root/.Lires
ENV HF_HOME=/root/.Lires/hf_home
ENTRYPOINT ["lrs-cluster", "/root/.Lires/container-cluster-config.yaml", "--init-if-not-exist"]
# ENTRYPOINT [ "/bin/bash" ]