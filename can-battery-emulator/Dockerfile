ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app

COPY . .

RUN apk add --no-cache python3 py3-pip
RUN apk add --no-cache --virtual .build-deps \
  python3-dev \
  build-base
RUN python3 -m venv venv
RUN . ./venv/bin/activate && python -m pip install -r requirements.txt
RUN apt del .build-deps

RUN chmod a+x run.sh

CMD [ "./run.sh" ]
