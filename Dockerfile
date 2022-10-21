FROM ubuntu:jammy
RUN apt-get update && apt-get install -y --reinstall ca-certificates

RUN echo "\
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse \n\
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse \n\
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse \n\
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-security main restricted universe multiverse \n\
" > /etc/apt/sources.list

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y apt-utils
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y python3-pyqt5 libgl1-mesa-glx libnss3 libasound2 libxkbfile1

RUN mkdir /ResBibManager
WORKDIR /ResBibManager
COPY . .

RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN python3 -m pip install --upgrade pip
RUN pip install wheel setuptools
RUN pip install -e /ResBibManager

RUN rbm-resetconf

EXPOSE 8080
ENTRYPOINT ["resbibman", "server"]
