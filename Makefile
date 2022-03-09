DOCKERCMD=$(shell which docker)
DOCKERBUILD=$(DOCKERCMD) build
DOCKERPUSH=$(DOCKERCMD) push

REPO=tmaxcloudck
IMAGE=regarchiver
TAG=dev

build:
	@echo "building..."
	@$(DOCKERBUILD) . -t $(REPO)/$(IMAGE):$(TAG)

push:
	@echo "push $(REPO)/$(IMAGE):$(TAG)..."
	@$(DOCKERPUSH) $(REPO)/$(IMAGE):$(TAG)

run:
	@docker run --name exporter -it --rm \
		-p 3000:3000 \
		-e TAR_PATH=/tmp/archiving \
		-e UPLOAD_SCP_PATH= \
		-e UPLOAD_SCP_PASS= \
		$(REPO)/$(IMAGE):$(TAG)