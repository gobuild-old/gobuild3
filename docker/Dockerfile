FROM	karalabe/xgo-latest
MAINTAINER codeskyblue@gmail.com

ADD run.sh /
RUN chmod +x run.sh

ENV TIMEOUT 30m
ENTRYPOINT ["/run.sh"]
