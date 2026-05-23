#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip to ensure the latest version
pip install --upgrade pip

# Install/update packages from requirements.txt
pip install --upgrade -r requirements.txt
