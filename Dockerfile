FROM ubuntu:jammy
RUN apt-get update && apt-get install -y --reinstall ca-certificates

RUN apt-get -y upgrade
RUN apt-get install -y apt-utils git curl
RUN apt-get install -y python3 python3-pip

RUN mkdir /ResBibManager
WORKDIR /ResBibManager
COPY . .

# install nvm and node following: 
# https://github.com/nvm-sh/nvm#manual-install and 
# https://stackoverflow.com/questions/25899912/how-to-install-nvm-in-docker
WORKDIR /root
RUN git clone https://github.com/nvm-sh/nvm.git .nvm
WORKDIR /root/.nvm
RUN git checkout v0.39.3
RUN . ./nvm.sh && \
echo ' export NVM_DIR="$HOME/.nvm" \n [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm \n [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion\n' \
>> /root/.bashrc && \
nvm install --lts && \
nvm use --lts && cd /ResBibManager/RBMWeb2 && npm install && npm run build

WORKDIR /
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN python3 -m pip install --upgrade pip
RUN pip install -e /ResBibManager[ai]

RUN rbm-resetconf

EXPOSE 8081
EXPOSE 8080
EXPOSE 8731
ENTRYPOINT ["resbibman", "server"]
