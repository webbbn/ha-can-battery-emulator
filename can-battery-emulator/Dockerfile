ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app

COPY . .

RUN apk add --no-cache gcc musl-dev python3 py3-pip && \
    python3 -m venv venv && \
    . ./venv/bin/activate && \
    python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

RUN chmod a+x run.sh

CMD [ "./run.sh" ]
