FROM alpine

RUN echo '/usr/bin/xclip -selection clipboard' > /usr/local/bin/xclip && chmod +x /usr/local/bin/xclip
# RUN echo -e 'set number\nset shellcmdflag=-ic' > ~/.vimrc
ADD .vimrc ~/.vimrc
RUN apk add bash-completion
RUN apk add bash git vim less xclip findutils grep sed
RUN apk add meld 
RUN apk add python3 py-pip 
RUN pip3 install --user colorama argcomplete

ENV PATH=$PATH:/gofritools
RUN git clone https://github.com/gofri/gofritools.git ${BRANCH}
RUN git config --global pull.rebase true
RUN git config --global pull.ff false

ADD default_gofignore /.gofignore
