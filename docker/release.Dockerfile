## build directly from the pypi release
FROM python:3.11-bookworm

# https://mirrors.ustc.edu.cn/help/debian.html
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
# https://mirrors.tuna.tsinghua.edu.cn/help/pypi/
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# https://stackoverflow.com/a/75722775/6775765
RUN python3 -m pip install --upgrade pip --break-system-packages

WORKDIR /
RUN pip3 install Lires[all] --break-system-packages

EXPOSE 8080 
EXPOSE 8700
EXPOSE 21000-22000
ENV LRS_HOME=/root/.Lires
ENV HF_HOME=/root/.Lires/hf_home
ENTRYPOINT ["lrs-cluster", "/root/.Lires/container-cluster.yaml", "--init-if-not-exist"]