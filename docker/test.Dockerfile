FROM python:3.11-bookworm

# not build web app, as this directory will be mapped to host during testing
COPY . /Lires
WORKDIR /

# mirrors
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN python3 -m pip install --upgrade pip --break-system-packages
RUN pip3 install -e /Lires[dev] --break-system-packages

# for better inspection
RUN apt-get update && apt install -y tmux

# will be mapped to host
RUN mkdir /_cache

# set env
ENV LRS_HOME=/root/.Lires
ENV HF_ENDPOINT=https://hf-mirror.com
ENV HF_HOME=/_cache/huggingface
# disable tqdm, otherwise it may block the subprocess pipe for testing
ENV TQDM_DISABLE=1

WORKDIR /Lires
EXPOSE 8080
EXPOSE 8731