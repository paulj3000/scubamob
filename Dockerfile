# pull official base image
FROM python:3.10.4-alpine

EXPOSE 8002

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
RUN mkdir -p /scuba/system \
    && mkdir -p /scuba/log \
    && mkdir -p /scuba/app/scubamob \
    && adduser -D -h /scuba/app/scubamob scuba

RUN apk add --update mysql-client gcc python3-dev musl-dev mariadb-connector-c-dev g++ nodejs npm

WORKDIR "/scuba/app/scubamob"

# install dependencies
COPY ./requirements.txt .
COPY ./package.json .
COPY ./manage.py .
COPY ./.babelrc .
COPY ./gulpfile.js .
COPY ./webpack.config.js .
ADD scuba scuba
ADD static static
ADD templates templates

# copy entrypoint.sh
COPY ./entrypoint.sh .

RUN chown -R scuba:scuba static \
    && chown -R scuba:scuba /scuba/log \
    && chmod 755 /scuba/app/scubamob/entrypoint.sh

USER scuba
WORKDIR "/scuba/app/scubamob"

ENTRYPOINT ["/scuba/app/scubamob/entrypoint.sh"]

CMD ["/scuba/app/scubamob/env/bin/gunicorn", "--bind", "0.0.0.0:8002", "--workers", "4", "scuba.wsgi:application", "--error-logfile", "/scuba/log/error.log", "--access-logfile", "/scuba/log/access.log"]
