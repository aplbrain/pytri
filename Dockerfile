FROM ubuntu

EXPOSE 8888

COPY . /home/widget
WORKDIR /home/widget
VOLUME /home/widget

RUN apt-get update
RUN apt-get -y install curl
RUN apt-get -y install npm
RUN apt-get -y install python3-pip
RUN apt-get -y install python3-dev

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install jupyter
RUN pip3 install -e .

CMD jupyter notebook --ip=0.0.0.0 --no-browser --allow-root
