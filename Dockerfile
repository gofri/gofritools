FROM alpine

RUN apk add bash git vim less xclip findutils grep sed
RUN apk add meld 
RUN apk add python3 py-pip 
RUN pip3 install --user colorama argcomplete

ENV PATH=$PATH:/gofritools
RUN git clone https://github.com/gofri/gofritools.git
