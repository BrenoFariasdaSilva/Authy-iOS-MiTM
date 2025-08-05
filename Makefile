# Variables
VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

# Main target that runs the scripts
all: run

# Main Scripts:
run: $(VENV)
	time $(PYTHON) ./main.py

# Setup Virtual Environment and Install Dependencies
$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

# Install the project dependencies
dependencies: $(VENV)

# Generate requirements.txt from the current venv
generate_requirements: $(VENV)
	$(PIP) freeze > requirements.txt

# Utility rule for cleaning the project
clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

.PHONY: run clean dependencies generate_requirements
