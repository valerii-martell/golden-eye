# Golden Eye

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/c0531b016d07419db03a7ae51e4d6991)](https://www.codacy.com/gh/valerii-martell/golden-eye/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=valerii-martell/golden-eye&amp;utm_campaign=Badge_Grade)
[![Flake8](https://github.com/valerii-martell/golden-eye/actions/workflows/lint.yml/badge.svg)](https://github.com/valerii-martell/Movies-RESTful-API/actions/workflows/lint.yml)
[![Pytest](https://github.com/valerii-martell/golden-eye/actions/workflows/test.yml/badge.svg)](https://github.com/valerii-martell/Movies-RESTful-API/actions/workflows/test.yml)
[![CodeQL](https://github.com/valerii-martell/golden-eye/actions/workflows/codeql.yml/badge.svg)](https://github.com/valerii-martell/Movies-RESTful-API/actions/workflows/codeql.yml)
[![Deploy](https://github.com/valerii-martell/golden-eye/actions/workflows/deploy.yml/badge.svg)](https://github.com/valerii-martell/Movies-RESTful-API/actions/workflows/deploy.yml)

https://golden-eye.azurewebsites.net/

A simple web service that continuously collects current currency exchange rates from open banking
and crypto exchange APIs, displays them on the website and provides them in JSON and XML
formats through its own RESTful API. Manually editing exchange rates and
manually requesting the latest updates is also available. The system automatically collects all required currency
exchange rates and updates them in the database every hour.

**Technology stack:**

- Language: Python
- Framework: Flask
- Databases: 2 PostgreSQL separated for main data and for external APIs logs
- ORM: Peewee
- Jobs scheduler: APScheduler
- Frontend: Jinja2 and Bootstrap 4
- WSGI: Gunicorn
- Testing: Pytest and Coverage
- Logging: core - Python build-in logging, web - Flask logging
- Linter: Flake8
- Containerization: Docker
- Deployment: Azure
- CI/CD: GitHub Actions

**External APIs used (JSON and XML):**

- The Ukrainian State Bank PrivatBank: https://api.privatbank.ua/
- The Central Bank of Russian Federation: https://cbr.ru/development/sxml/
- Blockchain.info: https://www.blockchain.com/api
- Cryptonator: https://api.cryptonator.com/api/
- Coinmarketcap: https://coinmarketcap.com/api

**DBs structure:** https://drawsql.app/kpi-6/diagrams/golden-eye
![drawSQL-export-2022-07-23_15_32](https://user-images.githubusercontent.com/19497575/180607245-626eb016-33c5-4ea3-ab49-c11dc89b812e.png)