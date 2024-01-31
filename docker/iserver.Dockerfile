FROM nvcr.io/nvidia/driver:535.104.12-ubuntu22.04
WORKDIR /
COPY . /Lires

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Install rust and make sure it's up to date and using stable channel
# RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
# RUN rustup update

RUN python3 -m pip install --upgrade pip
RUN pip3 install -e /Lires[ai]

EXPOSE 8731

ENV TVDB_BACKEND=numpy
ENV LRS_HOME=/root/.Lires
ENV HF_HOME=/root/.Lires/hf_home
ENV HF_ENDPOINT=https://hf-mirror.com
ENTRYPOINT [ "lires", "ai" ]