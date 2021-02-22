imalive
=======

Check website is alive metrics with distributable tasks

App architecture based on [cookiecutter-faust](https://github.com/marcosschroh/cookiecutter-faust) package.


:License: MIT


Installation
------------

Install local requirements:

```bash
make install
```

Usage
------

If you do not have a cluster/postgre running locally you can use `docker-compose` to avoid several headaches.
By default the `KAFKA_BOOTSTRAP_SERVER` is `kafka://localhost:29092`.

```bash
make start-backend
```

Then, start the `Faust application`:

```bash
make start-app
```

Settings
--------

Settings are created based on [local-settings](https://github.com/drgarcia1986/simple-settings) package.


Basic Commands
--------------

* Start backend containers: `make start-backend`.
* Install requirements: `make install`
* Start Faust application: `make start-app`
* List topics: `make list-topics`
* List agents: `make list-agents`


Docker
------

The `Dockerfile` is based on  `python:3.9-slim`.


Run tests
---------

```sh
make install-test && make start-test
```

Lint code
---------

```sh
./scripts/lint
```

Type checks
-----------

Running type checks with mypy:

```sh
mypy imalive
```
