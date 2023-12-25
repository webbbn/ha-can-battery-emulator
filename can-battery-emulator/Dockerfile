ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app

COPY . .

RUN apk add --no-cache python3
RUN apk add --no-cache python3-dev
RUN apk add --no-cache py3-pip
RUN apk add build-base
RUN python3 -m venv venv
RUN . ./venv/bin/activate && python -m pip install -r requirements.txt

RUN chmod a+x run.sh

CMD [ "./run.sh" ]
