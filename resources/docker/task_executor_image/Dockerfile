FROM alpine:latest
ENV PYTHONUNBUFFERED=1
RUN apk add --update bash
RUN apk add --no-cache python3 py3-pip
COPY ./daemonScript.sh /daemonScript.sh
RUN chmod 777 /daemonScript.sh
CMD ["/daemonScript.sh"]
