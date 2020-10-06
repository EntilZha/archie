FROM python:3.8

RUN pip install poetry==1.1.1

RUN mkdir -p /code/archie
RUN mkdir /code/archie/data
WORKDIR /code/archie
VOLUME /code/archie/data
COPY pyproject.toml poetry.lock /code/archie/
RUN poetry export --without-hashes -f requirements.txt > reqs.txt \
    && pip install -r reqs.txt

COPY . /code/archie
EXPOSE 9000

CMD ["uvicorn", "--port", "9000", "--host", "0.0.0.0", "archie.web:app"]