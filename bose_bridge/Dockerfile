ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip py3-lxml \
 && pip3 install --no-cache-dir --break-system-packages \
        upnpclient \
        websocket-client

COPY bridge.py /
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
