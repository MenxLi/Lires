FROM python:3.11-bookworm as iserver-build
WORKDIR /
COPY . /Lires

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Install rust and make sure it's up to date and using stable channel
# RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
# RUN rustup update

RUN python3 -m pip install --upgrade pip --break-system-packages
RUN pip3 install -e /Lires[ai] --break-system-packages

EXPOSE 8731

ENV LRS_HOME=/root/.Lires
ENV HF_HOME=/root/.Lires/hf_home
ENV HF_DATASETS_OFFLINE=1
# ENTRYPOINT ["python3", "-m", "lires_ai.server"]
ENTRYPOINT [ "lires", "iserver" ]