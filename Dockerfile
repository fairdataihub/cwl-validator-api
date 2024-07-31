FROM python:3.10-alpine

EXPOSE 5000

WORKDIR /app

ENV POETRY_VERSION=1.3.2

RUN apk update
RUN apk add --no-cache gcc libffi-dev musl-dev

RUN pip install "poetry==$POETRY_VERSION"

# COPY poetry.lock pyproject.toml ./
COPY pyproject.toml .

RUN poetry config virtualenvs.create false
RUN poetry install

COPY apis ./apis
COPY config.py .
COPY app.py .

# COPY entrypoint.sh .

# RUN chmod +x entrypoint.sh

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

# ENTRYPOINT ["./entrypoint.sh"]