# SCD Solution

Altrumus is a solution made to empower the Sickle Cell Foundation with an end-to-end solution that streamlines donor engagement, sponsorships, and fundraising efforts. Using DocuSign’s developer platform, APIs, and extensions

## Development Requirements

- Python3.11.0
- Pip
- Poetry (Python Package Manager)

## Installation

```sh
python -m venv env
source env/bin/activate
make install
```

## Runnning Localhost

`make run`

## Deploy app

`make deploy`

## Running Tests

`make test`

## Access Swagger Documentation

> <http://localhost:8080/docs>

## Access Redocs Documentation

> <http://localhost:8080/redoc>

## Project structure

Files related to application are in the `app` or `tests` directories.
Application parts are:

    app
    |
    | # Fast-API stuff
    ├── api                 - web related stuff.
    ├── routes              - web routes.
    ├── core                - application configuration, startup events, logging.
    └── main.py             - FastAPI application creation and configuration.
    └── tests               - pytest
