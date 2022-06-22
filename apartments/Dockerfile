ARG PYTHON_VERSION=3.10-alpine

FROM python:${PYTHON_VERSION} as builder
WORKDIR /wheels
COPY ./requirements.txt /wheels/requirements.txt
RUN pip wheel -r ./requirements.txt

FROM python:${PYTHON_VERSION}
COPY --from=builder /wheels /wheels
RUN pip install -r /wheels/requirements.txt -f /wheels \
    && rm -rf /wheels \
    && rm -rf /root/.cache/pip/*

WORKDIR /home

EXPOSE 5000
COPY . .
CMD ["python", "-m", "apartments"]
