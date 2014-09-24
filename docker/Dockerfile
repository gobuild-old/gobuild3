FROM	karalabe/xgo-latest
MAINTAINER codeskyblue@gmail.com

RUN apt-get install -y python-pip

ADD requirements.txt /
RUN pip install -r requirements.txt

# add packer
RUN GOBIN=/usr/local/bin go get github.com/gpmgo/gopm
RUN gopm get -v -g github.com/gobuild/gobuild3/packer
RUN GOBIN=/build go install github.com/gobuild/gobuild3/packer

ADD crosscompile.py /build/
RUN mkdir -p gopath output

ADD run.sh /
RUN chmod +x run.sh

ENV GOPATH /gopath
ENV TIMEOUT 30m

ENTRYPOINT ["./run.sh"]
CMD ["bash"]
