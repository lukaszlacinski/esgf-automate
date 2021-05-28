FROM python:3.8-slim-buster

RUN mkdir /esgf-automate

WORKDIR /esgf-automate

COPY ./ ./

RUN apt-get update -y

RUN pip install poetry==1.1

RUN poetry install --no-dev

EXPOSE 5009

CMD ["/esgf-automate/.venv/bin/gunicorn", "--config", "deploy/gunicorn_config.py", "esgf_automate.action_provider_main"]

