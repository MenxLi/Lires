FROM python:3.11-bookworm as server-build
WORKDIR /
COPY . /Lires

# https://mirrors.ustc.edu.cn/help/debian.html
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources

# https://mirrors.tuna.tsinghua.edu.cn/help/pypi/
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# https://stackoverflow.com/a/75722775/6775765
RUN python3 -m pip install --upgrade pip --break-system-packages
RUN pip3 install /Lires/packages/tiny_vectordb --break-system-packages
RUN pip3 install -e /Lires --break-system-packages

EXPOSE 8080
EXPOSE 8731

ENV LRS_HOME=/root/.Lires
# ENV HF_HOME=/root/.Lires/hf_home
ENTRYPOINT ["lires", "server"]