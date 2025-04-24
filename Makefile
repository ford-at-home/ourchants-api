# Variables
REGION = us-east-1
PROJECT_ROOT = $(shell git rev-parse --show-toplevel)
PYTHONPATH = $(shell pwd):$(shell pwd)/infrastructure

# Build and Test
.PHONY: build test test-unit test-integration test-e2e
build: test
	@echo "🔨 Building project..."
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt

test: test-unit test-integration

test-unit:
	@echo "🧪 Running unit tests..."
	PYTHONPATH=$(PYTHONPATH) pytest tests/api -v

test-integration:
	@echo "🧪 Running integration tests..."
	PYTHONPATH=$(PYTHONPATH) pytest tests/integration -v

test-e2e:
	@echo "🧪 Running end-to-end tests..."
	PYTHONPATH=$(PYTHONPATH) pytest tests/e2e -v

# Environment Setup
.PHONY: setup-env
setup-env:
	@echo "🔧 Setting up environment..."
	@if [ ! -f .env ]; then \
		echo "# Environment variables for the Songs API" > .env; \
		echo "# This file contains configuration settings for the application" >> .env; \
		echo "" >> .env; \
		echo "# AWS Configuration" >> .env; \
		echo "AWS_REGION=$(REGION)" >> .env; \
		echo "DYNAMODB_TABLE_NAME=ourchants-songs" >> .env; \
		echo "S3_BUCKET=ourchants-songs" >> .env; \
		echo "" >> .env; \
		echo "# API Configuration" >> .env; \
		echo "API_VERSION=1.0" >> .env; \
		echo "API_STAGE=prod" >> .env; \
		echo "✅ Created .env file"; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Authentication Setup
.PHONY: auth
auth: setup-env
	@echo "🔐 Setting up GitHub Actions authentication..."
	@# Check for AWS credentials
	@if [ ! -f ~/.aws/credentials ]; then \
		echo "Error: AWS credentials not found. Please run 'aws configure' first."; \
		exit 1; \
	fi

	@# Get AWS credentials
	@AWS_ACCESS_KEY_ID=$$(aws configure get aws_access_key_id); \
	AWS_SECRET_ACCESS_KEY=$$(aws configure get aws_secret_access_key); \
	if [ -z "$$AWS_ACCESS_KEY_ID" ] || [ -z "$$AWS_SECRET_ACCESS_KEY" ]; then \
		echo "Error: Could not get AWS credentials from aws configure"; \
		exit 1; \
	fi

	@# Check if GitHub CLI is installed
	@if ! command -v gh &> /dev/null; then \
		echo "Error: GitHub CLI (gh) is not installed. Please install it first."; \
		exit 1; \
	fi

	@# Check if GitHub CLI is authenticated
	@if ! gh auth status &> /dev/null; then \
		echo "Error: GitHub CLI is not authenticated. Please run 'gh auth login' first."; \
		exit 1; \
	fi

	@echo "📝 Setting up GitHub secrets..."
	@echo "$$AWS_ACCESS_KEY_ID" | gh secret set AWS_ACCESS_KEY_ID || { echo "Error: Failed to set AWS_ACCESS_KEY_ID"; exit 1; }
	@echo "$$AWS_SECRET_ACCESS_KEY" | gh secret set AWS_SECRET_ACCESS_KEY || { echo "Error: Failed to set AWS_SECRET_ACCESS_KEY"; exit 1; }
	@echo "✅ GitHub secrets set successfully!"

	@# Deploy OIDC stack
	@echo "🔄 Deploying GitHub OIDC stack..."
	@cd infrastructure && ./deploy-cdk.sh GitHubOidcDeploymentRoleStack
	@echo "✅ OIDC stack deployed successfully!"

# Full Deployment
.PHONY: deploy
deploy: build setup-env
	@echo "🚀 Deploying to production..."
	@# Deploy application using deploy.sh
	@echo "🚀 Deploying application..."
	@chmod +x infrastructure/deploy.sh
	@./infrastructure/deploy.sh || (echo "Application deployment failed. Check the logs above for details." && exit 1)

	@# Deploy infrastructure using CDK
	@echo "🏗️  Deploying infrastructure..."
	@cd infrastructure && ./deploy-cdk.sh

	@echo "✅ Deployment complete!"

# Diagnostics
.PHONY: diagnose
diagnose:
	@mkdir -p logs
	@echo "📋 Running full network environment diagnosis..."
	@bash infrastructure/check_stack_env.sh | tee logs/env-profile-$(shell date +"%Y%m%d-%H%M%S").log

# Cleanup
.PHONY: clean
clean:
	rm -rf venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf infrastructure/.venv
	rm -rf infrastructure/cdk.out

# Help
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make build   - Build and install dependencies"
	@echo "  make test   - Run all tests"
	@echo "  make test-unit - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-e2e - Run end-to-end tests"
	@echo "  make deploy  - Full deployment (build, deploy, infrastructure)"
	@echo "  make auth    - Set up GitHub Actions authentication"
	@echo "  make diagnose - Run network diagnostics"
	@echo "  make clean   - Clean build files and dependencies"
	@echo "  make setup-env - Create .env file with default settings"
	@echo ""
	@echo "Variables:"
	@echo "  REGION     - AWS region (default: us-east-1)"
	@echo "  PYTHONPATH - Python path for tests (default: project root and infrastructure)" 