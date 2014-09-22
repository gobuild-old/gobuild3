FROM	karalabe/xgo-latest
MAINTAINER codeskyblue@gmail.com

RUN apt-get install -y python-pip

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD run.sh /
RUN chmod +x run.sh

ADD crosscompile.py /build/
RUN mkdir -p gopath output

ENV GOPATH /gopath
ENV CGO_ENABLED 1
ENV TIMEOUT 30m

ENTRYPOINT ["./run.sh"]
CMD ["bash"]
