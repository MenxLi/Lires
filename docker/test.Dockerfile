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

RUN python3 -m pip install --upgrade pip --break-system-packages
RUN pip3 install -e /Lires[dev] --break-system-packages

# will be mapped to host
RUN mkdir /_cache

# set env
ENV LRS_HOME=/root/.Lires
ENV HF_ENDPOINT=https://hf-mirror.com
ENV TVDB_CACHE_DIR=/_cache/tiny_vectordb
ENV HF_HOME=/_cache/huggingface
# disable tqdm, otherwise it may block the subprocess pipe for testing
ENV TQDM_DISABLE=1

WORKDIR /Lires
EXPOSE 8080
EXPOSE 8731