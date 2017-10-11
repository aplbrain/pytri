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
    pip3 install jupyter && \
    pip3 install -e . && \
    jupyter nbextension install --py --symlink --sys-prefix pytri && \
    jupyter nbextension enable --py --sys-prefix pytri

CMD bash
