# MITS Validator Docker Operations
# Usage: make <target> [VARIABLE=value]

# Default values
IMAGE ?= ghcr.io/open-mits/mits-validator
TAG ?= latest
PORT ?= 8000
REGISTRY ?= ghcr.io
REPO ?= open-mits/mits-validator

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help build run test smoke publish clean

# Default target
help: ## Show this help message
	@echo "$(GREEN)MITS Validator Docker Operations$(NC)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Environment variables:$(NC)"
	@echo "  IMAGE     Docker image name (default: $(IMAGE))"
	@echo "  TAG       Docker image tag (default: $(TAG))"
	@echo "  PORT      Host port to bind (default: $(PORT))"
	@echo "  REGISTRY  Container registry (default: $(REGISTRY))"
	@echo "  REPO      Repository name (default: $(REPO))"

build: ## Build the Docker image
	@echo "$(GREEN)Building Docker image: $(IMAGE):$(TAG)$(NC)"
	docker build -t $(IMAGE):$(TAG) .
	@echo "$(GREEN)Build completed successfully$(NC)"

run: ## Run the container locally
	@echo "$(GREEN)Starting container on port $(PORT)$(NC)"
	docker run --rm -p $(PORT):8000 \
		-e PORT=8000 \
		-e MAX_UPLOAD_BYTES=10485760 \
		-e LOG_LEVEL=INFO \
		$(IMAGE):$(TAG)

test: ## Run tests in container
	@echo "$(GREEN)Running tests in container$(NC)"
	docker run --rm \
		-v $(PWD)/tests:/app/tests:ro \
		-v $(PWD)/fixtures:/app/fixtures:ro \
		$(IMAGE):$(TAG) \
		python -m pytest tests/ -v

smoke: ## Run smoke tests against running container
	@echo "$(GREEN)Running smoke tests$(NC)"
	@./scripts/smoke-test.sh $(PORT)

publish: ## Publish image to registry
	@echo "$(GREEN)Publishing $(IMAGE):$(TAG) to $(REGISTRY)$(NC)"
	docker push $(IMAGE):$(TAG)
	@echo "$(GREEN)Published successfully$(NC)"

publish-tags: ## Publish with multiple tags (for releases)
	@echo "$(GREEN)Publishing with multiple tags$(NC)"
	@if [ -z "$(VERSION)" ]; then \
		echo "$(RED)Error: VERSION is required for publish-tags$(NC)"; \
		exit 1; \
	fi
	@docker tag $(IMAGE):$(TAG) $(IMAGE):$(VERSION)
	@docker tag $(IMAGE):$(TAG) $(IMAGE):$$(echo $(VERSION) | cut -d. -f1-2)
	@docker tag $(IMAGE):$(TAG) $(IMAGE):latest
	@docker push $(IMAGE):$(VERSION)
	@docker push $(IMAGE):$$(echo $(VERSION) | cut -d. -f1-2)
	@docker push $(IMAGE):latest
	@echo "$(GREEN)Published tags: $(VERSION), $$(echo $(VERSION) | cut -d. -f1-2), latest$(NC)"

clean: ## Clean up local images and containers
	@echo "$(GREEN)Cleaning up Docker resources$(NC)"
	@docker system prune -f
	@docker image prune -f
	@echo "$(GREEN)Cleanup completed$(NC)"

logs: ## Show container logs (if running)
	@echo "$(GREEN)Showing container logs$(NC)"
	@docker logs $$(docker ps -q --filter ancestor=$(IMAGE):$(TAG)) 2>/dev/null || echo "$(YELLOW)No running containers found$(NC)"

stop: ## Stop running containers
	@echo "$(GREEN)Stopping containers$(NC)"
	@docker stop $$(docker ps -q --filter ancestor=$(IMAGE):$(TAG)) 2>/dev/null || echo "$(YELLOW)No running containers found$(NC)"

# Development helpers
dev: ## Run in development mode with volume mounts
	@echo "$(GREEN)Starting development container$(NC)"
	docker run --rm -p $(PORT):8000 \
		-v $(PWD)/src:/app/src:ro \
		-v $(PWD)/rules:/app/rules:ro \
		-e LOG_LEVEL=DEBUG \
		-e PYTHONPATH=/app \
		$(IMAGE):$(TAG)

shell: ## Open shell in running container
	@echo "$(GREEN)Opening shell in container$(NC)"
	@docker exec -it $$(docker ps -q --filter ancestor=$(IMAGE):$(TAG)) /bin/bash || echo "$(RED)No running container found$(NC)"

# CI helpers
ci-build: ## Build for CI (with build args)
	@echo "$(GREEN)Building for CI$(NC)"
	docker build \
		--build-arg BUILDPLATFORM=linux/amd64 \
		--build-arg TARGETPLATFORM=linux/amd64 \
		-t $(IMAGE):$(TAG) .

ci-test: ## Run CI tests
	@echo "$(GREEN)Running CI tests$(NC)"
	@make smoke PORT=$(PORT)
