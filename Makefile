.PHONY: test test-api test-e2e test-all check-aws-credentials check-aws-profiles deploy clean

# Test commands
test: test-all

test-api:
	@echo "Running API tests..."
	@python3 -m pytest tests/api -v

test-e2e:
	@echo "Running end-to-end tests..."
	@python3 -m pytest tests/e2e -v

test-all:
	@echo "Running all tests..."
	@python3 -m pytest tests -v

# AWS commands
check-aws-credentials:
	@echo "Checking AWS credentials..."
	@aws sts get-caller-identity

check-aws-profiles:
	@echo "Available AWS profiles:"
	@aws configure list-profiles

# Deployment
deploy:
	@echo "Deploying infrastructure..."
	@cd infrastructure && cdk deploy

# Cleanup
clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "dist" -exec rm -rf {} +
	@find . -type d -name "build" -exec rm -rf {} +

# Help
help:
	@echo "Available commands:"
	@echo "  test-api        - Run API tests"
	@echo "  test-e2e        - Run end-to-end tests"
	@echo "  test-all        - Run all tests"
	@echo "  check-aws-credentials - Verify AWS credentials"
	@echo "  check-aws-profiles - List available AWS profiles"
	@echo "  deploy          - Deploy infrastructure"
	@echo "  clean           - Clean up Python cache files"
	@echo "  help            - Show this help message" 