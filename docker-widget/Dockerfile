FROM ubuntu

EXPOSE 8888

COPY . /home/widget
WORKDIR /home/widget

RUN apt-get update && \
    apt-get -y install curl && \
    apt-get -y install npm && \
    apt-get -y install python3-pip && \
    apt-get -y install python3-dev

RUN npm install -g n
RUN n latest

RUN pip3 install --upgrade pip && \
    pip3 install jupyter
    # python3 ./setup.py install

CMD bash
