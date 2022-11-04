FROM python:3.10

WORKDIR /fastapi

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip3 install cython==0.29.32

COPY requirements.txt requirements-orjson.txt requirements-uvicorn.txt ./

RUN pip3 install -r requirements.txt -r requirements-orjson.txt -r requirements-uvicorn.txt

COPY . ./

EXPOSE 8080

CMD uvicorn app:app --host 0.0.0.0 --port 8080 --workers $(nproc) --log-level error
