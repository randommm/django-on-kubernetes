FROM python

RUN pip install poetry

COPY poetry.lock /django_app/app/poetry.lock
COPY pyproject.toml /django_app/app/pyproject.toml
RUN cd /django_app/app && ls && poetry install

COPY django_website /django_app/app

