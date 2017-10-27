FROM ubuntu

EXPOSE 8888

RUN mkdir /home/widget
WORKDIR /home/widget
VOLUME /home/widget

RUN apt-get update && \
    apt-get -y install curl && \
    apt-get -y install npm && \
    apt-get -y install python3-pip && \
    apt-get -y install python3-dev

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    pip3 install jupyter && \
    pip3 install -e .

CMD jupyter notebook --ip=0.0.0.0 --no-browser --allow-root
