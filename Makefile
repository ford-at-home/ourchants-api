.PHONY: setup test test-unit test-integration test-e2e deploy

# Create and set up virtual environment
setup:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Activating virtual environment and installing dependencies..."
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt

# Run tests
test: test-unit test-integration

test-unit:
	PYTHONPATH=$(shell pwd):$(shell pwd)/infrastructure pytest tests/api -v

test-integration:
	PYTHONPATH=$(shell pwd):$(shell pwd)/infrastructure pytest tests/integration -v

test-e2e:
	PYTHONPATH=$(shell pwd):$(shell pwd)/infrastructure pytest tests/e2e -v

# Deploy the application
deploy: setup
	@echo "Deploying application..."
	@chmod +x infrastructure/deploy.sh
	@./infrastructure/deploy.sh || (echo "Deployment failed. Check the logs above for details." && exit 1) 