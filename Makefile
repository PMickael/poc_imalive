PARTITIONS=1
REPLICATION-FACTOR=1

# For local development
export WORKER_PORT=6066
export SIMPLE_SETTINGS=imalive.settings

PYTHON?=python3

# Installation
install:
	$(PYTHON) -m venv ./venv
	./venv/bin/pip install -U pip -r requirements/base.txt

install-test:
	$(PYTHON) -m venv ./venv
	./venv/bin/pip install -U pip -r requirements/test.txt

install-production:
	$(PYTHON) -m venv ./venv
	./venv/bin/pip install -U pip -r requirements/production.txt

bash:
	docker-compose run --user=$(shell id -u) ${service} bash

# Removes old containers, free's up some space
remove:
	# Try this if this fails: docker rm -f $(docker ps -a -q)
	docker-compose rm --force -v

start-backend:
	docker-compose up

# Kafka related
list-topics:
	docker-compose exec imalive_kafka kafka-topics --list --zookeeper imalive_zookeeper:32181

create-topic:
	docker-compose exec imalive_kafka kafka-topics --create --zookeeper imalive_zookeeper:32181 --replication-factor ${REPLICATION-FACTOR} --partitions ${PARTITIONS} --topic ${topic-name}

# Start the faust app
start-app:
	./scripts/run

start-test:
	./scripts/test

list-agents:
	PYTHONPATH=imalive venv/bin/faust -A app agents

# Build docker image
build:
	docker build -t imalive .

run:
	docker run --expose 6066 --env WORKER_PORT=${WORKER_PORT} --env SIMPLE_SETTINGS=${SIMPLE_SETTINGS} imalive
