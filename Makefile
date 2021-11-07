.PHONY: install install-dev dev build run push release release-multi deploy

DOCKER_REPOSITERY=dixneuf19
IMAGE_NAME=fip-slack-bot
IMAGE_TAG=$(shell git rev-parse --short HEAD)
DOCKER_IMAGE_PATH=$(DOCKER_REPOSITERY)/$(IMAGE_NAME):$(IMAGE_TAG)
APP_NAME=fip-slack-bot
KUBE_NAMESPACE=fip
TARGET_PLATFORMS = "linux/amd64,linux/arm64,linux/386"

install:
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt

dev:
	PYTHONPATH=. python fip_slack_bot/main.py

format:
	black .

check-format:
	black --check .

test:
	PYTHONPATH=. pytest tests

build:
	docker build -t $(DOCKER_IMAGE_PATH) .

build-multi:
	docker buildx build --platform "${TARGET_PLATFORMS}" -t $(DOCKER_IMAGE_PATH) .


run: build
	docker run -p 3000:3000 --env-file=.env $(DOCKER_IMAGE_PATH)

push:
	docker push $(DOCKER_IMAGE_PATH)

release: build push

release-multi:
	docker buildx build --platform "${TARGET_PLATFORMS}" -t $(DOCKER_IMAGE_PATH) . --push

deploy:
	helm upgrade -i ${APP_NAME} dixneuf19/base-helm-chart -f values.yaml --set image.tag=${IMAGE_TAG}

secret:
	kubectl create secret generic fip-slack-bot --from-env-file=.env

kube-credentials:
	NAMESPACE=${KUBE_NAMESPACE} ./scripts/generate-kubeconfig.sh
