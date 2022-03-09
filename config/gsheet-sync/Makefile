DOCKERCMD=$(shell which docker)
DOCKERBUILD=$(DOCKERCMD) build
DOCKERPUSH=$(DOCKERCMD) push

REPO=tmaxcloudck
IMAGE=gsheet-sync
TAG=dev

build:
	@echo "building..."
	@$(DOCKERBUILD) . -t $(REPO)/$(IMAGE):$(TAG)

push:
	@echo "push $(REPO)/$(IMAGE):$(TAG)..."
	@$(DOCKERPUSH) $(REPO)/$(IMAGE):$(TAG)
run:
	@docker run --name sync -it --rm \
		-p 8080:8080 \
		-e SHEET_URL="https://docs.google.com/spreadsheets/d/1_KVOzzVlAl8VQ6y6I4y2NnsokjF-yE51uOXcZPyzDEU/edit#gid=0" \
		-e SHEET_IDX=0 \
		-e COL_NUM=1 \
		-e ROW_FROM=2 \
		-e REGISTRY_URL= \
		-e DOCKER_CRED= \
		-e QUAY_CRED= \
		-e NOTIFY_URL=http://<>/run \
		$(REPO)/$(IMAGE):$(TAG)