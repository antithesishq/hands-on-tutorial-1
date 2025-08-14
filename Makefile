#!make

# Docker or podman to run locally? Either works.
DOCKER=docker
#DOCKER=podman

PYTHON=python3

ANTITHESIS_ROOT = ./antithesis

DOCKERFILE_CONFIG = ${ANTITHESIS_ROOT}/Dockerfile.config
DOCKERFILE_SUT = ${ANTITHESIS_ROOT}/Dockerfile.sut

DOCKER_COMPOSE = ${ANTITHESIS_ROOT}/docker-compose.yaml
DOCKER_COMPOSE_ENV = ${ANTITHESIS_ROOT}/.env

## -----------------------------------------------------------------------------
##
## Python Virtual environment setup for local development
##

.PHONY: venv_setup venv_check

venv_setup:
	@ rm -rf .venv && ${PYTHON} -m venv .venv && . .venv/bin/activate && pip install .
	@ echo "☑️ Virtual environment created. Activate with:"
	@ echo "  . .venv/bin/activate "

venv_check:
	@ if [[ "${VIRTUAL_ENV}" == "" ]]; then echo "‼️ Python virtual environment not active, please run: 'make venv_setup' to create it"; exit 1; fi
	@ echo "✅ Virtual environment active"

## -----------------------------------------------------------------------------
##
## Local launch and tests
##

.PHONY: server client workload test test-server test-client test-e2e

server: venv_check
	${PYTHON} -m src.server --port 8888

client: venv_check
	${PYTHON} -m src.client --port 8888

workload: venv_check
	${PYTHON} -m src.workload --port 8888

test: venv_check test-server test-client test-e2e

test-server: venv_check
	${PYTHON} -m unittest discover -s tests -p test_server.py -v

test-client: venv_check
	${PYTHON} -m unittest discover -s tests -p test_client.py -v

test-e2e: venv_check
	${PYTHON} -m unittest discover -s tests -p test_e2e.py -v

## -----------------------------------------------------------------------------
##
## Local Docker build and smoke-testing
##
# Uncomment if needed to debug build:
# DOCKER_BUILD_FLAGS = --no-cache

#
# Check tasks
# Verify environment is sane
#
.PHONY: check check_docker_running check_directories

check: check_docker_running check_directories
	@ # Check that Docker is installed and running
	@ echo "✅ Ready to roll!"

check_docker_running:
	@ # Check that Docker is installed and running
	@ $(DOCKER) container ls >/dev/null
	@ echo "☑️ Docker running"

check_directories:
	@ echo "☑️ Directories and files found"

#
# Image build tasks
# Build local images
#
.PHONY: build

build: check $(DOCKERFILE_CONFIG) $(DOCKERFILE_SUT) $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ENV)
	COMPOSE_PROFILES=config $(DOCKER) compose -f $(DOCKER_COMPOSE) build
	@ echo "✅ Images built"

#
# Local run tasks
# Run the system locally
#
.PHONY: run stop

run: check stop build $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ENV)
	@ # Bring system up
	$(DOCKER) compose -f $(DOCKER_COMPOSE) up
	@ # After ctrl-c or error, bring system down
	$(DOCKER) compose -f $(DOCKER_COMPOSE) down

stop: check $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ENV)
	@ # Bring system down
	$(DOCKER) compose -f $(DOCKER_COMPOSE) down
	@ echo "☑️ Containers stopped"
