FROM python:3.10.9-alpine3.16 AS final_build

ENV APPNAME=mp3mdf

ENV USERNAME=$APPNAME
ENV HOME_FOLDER=/$APPNAME
COPY util/requirements.txt /tmp/pip-tmp/requirements.txt
COPY mp3mdf $HOME_FOLDER/
COPY util/ $HOME_FOLDER/util/
COPY model/ $HOME_FOLDER/model/
COPY constants/ $HOME_FOLDER/constants/

RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "$HOME_FOLDER" \
    "$USERNAME" \
    && apk update \
    && apk upgrade \
    && apk add --no-cache \
               bash \
    && pip install --no-cache-dir -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp \
    ## Set the right timezone in the container image
    && cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime

USER $USERNAME
WORKDIR $HOME_FOLDER

CMD ["bash"]
