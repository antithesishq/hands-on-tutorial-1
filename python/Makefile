#!make

# Docker or podman to run locally? Either works.
DOCKER=docker
#DOCKER=podman

PYTHON=python3

CONFIG_IMAGE_ROOT = ./antithesis/config
DOCKERFILE_CONFIG = ./antithesis/Dockerfile

SUT_IMAGE_ROOT = .
DOCKERFILE_SUT = ${SUT_IMAGE_ROOT}/Dockerfile

DOCKER_COMPOSE = ${CONFIG_IMAGE_ROOT}/docker-compose.yml
DOCKER_COMPOSE_ENV = ${CONFIG_IMAGE_ROOT}/environment

IMAGES_PREFIX = tutorial-1
LOCAL_IMAGES_TAG = local


## -----------------------------------------------------------------------------
##
## Python Virtual environment setup for local development
##

.PHONY: venv_setup venv_check

venv_setup:
	@rm -rf .venv && ${PYTHON} -m venv .venv && . .venv/bin/activate && pip install .
	@echo "☑️ Virtual environment created. Activate with:"
	@echo "  . .venv/bin/activate "

venv_check:
	@if [[ "${VIRTUAL_ENV}" == "" ]]; then echo "‼️ Python virtual environment not active, please run: 'make venv_setup' to create it"; exit 1; fi
	@ echo "✅ Virtual environment active"

## -----------------------------------------------------------------------------
##
## Local launch and tests
##

.PHONY: server client test test-server test-client test-e2e

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
.PHONY: check check_docker_running check_directories check_environment

check: check_docker_running check_directories check_environment
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
.PHONY: build build_sut build_config build_workload

build: build_config build_sut build_workload
	@ echo "✅ Images built"

build_config: check $(CONFIG_IMAGE_ROOT) $(DOCKERFILE_CONFIG) $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ENV)
	$(DOCKER) build $(DOCKER_BUILD_FLAGS) $(CONFIG_IMAGE_ROOT) -f $(DOCKERFILE_CONFIG) -t $(IMAGES_PREFIX)-config:$(LOCAL_IMAGES_TAG)
	@ echo "☑️ Built Config image $(IMAGES_PREFIX)-config:$(LOCAL_IMAGES_TAG)"

build_sut: check $(SUT_IMAGE_ROOT) $(DOCKERFILE_SUT)
	$(DOCKER) build $(DOCKER_BUILD_FLAGS) $(SUT_IMAGE_ROOT) -f $(DOCKERFILE_SUT) -t $(IMAGES_PREFIX)-sut:$(LOCAL_IMAGES_TAG)
	@ echo "☑️ Built SUT image $(IMAGES_PREFIX)-sut:$(LOCAL_IMAGES_TAG)"

#
# Local run tasks
# Run the system locally
#
.PHONY: run stop

run: check stop build $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ENV)
	@ # Bring system up
	@ IMAGES_PREFIX=$(IMAGES_PREFIX) IMAGES_TAG=$(LOCAL_IMAGES_TAG) $(DOCKER) compose -f $(DOCKER_COMPOSE) --env-file $(DOCKER_COMPOSE_ENV) up
	@ # After ctrl-c or error, bring system down
	@ IMAGES_PREFIX=$(IMAGES_PREFIX) IMAGES_TAG=$(LOCAL_IMAGES_TAG) $(DOCKER) compose -f $(DOCKER_COMPOSE) --env-file $(DOCKER_COMPOSE_ENV) down

stop: check $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ENV)
	@ # Bring system down
	@ IMAGES_PREFIX=$(IMAGES_PREFIX) IMAGES_TAG=$(LOCAL_IMAGES_TAG) $(DOCKER) compose -f $(DOCKER_COMPOSE) --env-file $(DOCKER_COMPOSE_ENV) down
	@ echo "☑️ Containers stopped"
