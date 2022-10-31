# pull official base image
FROM python:3.10.4-alpine

EXPOSE 8002

# set work directory
RUN mkdir -p /scuba/app/scubamob && mkdir /scuba/system
WORKDIR "/scuba/app/scubamob"

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
#RUN apk update \
#    && apk add mysql-client gcc python3-dev musl-dev mariadb-connector-c-dev g++ nodejs

RUN apk add --update mysql-client gcc python3-dev musl-dev mariadb-connector-c-dev g++ nodejs npm

RUN ls ../

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

RUN chmod 755 /scuba/app/scubamob/entrypoint.sh

ENTRYPOINT ["/scuba/app/scubamob/entrypoint.sh"]

CMD ["/usr/local/bin/gunicorn", "--bind", "0.0.0.0:8002", "--workers", "4", "scuba.wsgi:application"]
