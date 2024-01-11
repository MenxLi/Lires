## First stage, build the web app
FROM node:20 as webapp-build

RUN mkdir /Lires
WORKDIR /

COPY . /Lires
WORKDIR /Lires/lires_web 
RUN npm install -g cnpm
RUN cnpm install && cnpm run build

## Second stage, build the server
FROM python:3.11-bookworm as server-build
COPY --from=webapp-build /Lires /Lires
WORKDIR /

# mirrors
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
ENV HF_ENDPOINT=https://hf-mirror.com

RUN python3 -m pip install --upgrade pip --break-system-packages
RUN pip3 install -e /Lires[all] --break-system-packages

EXPOSE 8081
EXPOSE 8080
EXPOSE 8731


WORKDIR /Lires

ENV LRS_HOME=/root/.Lires
ENV HF_HOME=/root/.Lires/hf_home