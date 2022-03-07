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
	@docker run -it --rm -v `pwd`/results:/results $(REPO)/$(IMAGE):$(TAG)