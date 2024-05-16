## First stage, build the web app
FROM node:20 as webapp-build

RUN mkdir /Lires
WORKDIR /

COPY . /Lires

WORKDIR /Lires/docs
RUN npm install && npm run build

WORKDIR /Lires/plugins/obsidian
RUN npm install && npm run build

WORKDIR /Lires/lires_web 
RUN npm install && npm run build

## Second stage, build the server
FROM python:3.11-bookworm as base-build
COPY --from=webapp-build /Lires /Lires
WORKDIR /Lires

# https://mirrors.ustc.edu.cn/help/debian.html
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
# https://mirrors.tuna.tsinghua.edu.cn/help/pypi/
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# https://stackoverflow.com/a/75722775/6775765
RUN python3 -m pip install --upgrade pip --break-system-packages

# First create a layer with the requirements
RUN python3 requirements.py > requirements.txt
RUN pip3 install -r requirements.txt

# Now, build the final image
WORKDIR /
RUN pip3 install -e /Lires[all] --break-system-packages

EXPOSE 8080 
EXPOSE 8700
EXPOSE 21000-22000
ENV LRS_HOME=/root/.Lires
ENV HF_HOME=/root/.Lires/hf_home
ENTRYPOINT ["lrs-cluster", "/root/.Lires/container-cluster.yaml", "--init-if-not-exist"]
# ENTRYPOINT [ "/bin/bash" ]