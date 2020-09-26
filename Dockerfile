FROM centos
RUN yum install -y vim git python3 python2 python3-pip
RUN pip3 install click tabulate pandas numpy matplotlib xlrd
RUN cd / && \
    git clone https://github.com/vj-sarthy/get_GET.git && \
    cd get_GET && \
    git pull
WORKDIR /get_GET
