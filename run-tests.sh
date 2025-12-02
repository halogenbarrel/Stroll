#!/bin/bash

# Script to run Django tests locally
# Usage: ./run-tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Django test environment...${NC}"

# Check if virtual environment exists
if [ ! -d "env_stroll" ]; then
    echo -e "${RED}Virtual environment 'env_stroll' not found. Please create it first.${NC}"
    exit 1
fi

# Activate virtual environment
source env_stroll/bin/activate

# Change to app directory
cd app

# Set Django settings if not already set
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-djangoproject.settings}

# Run Django check
echo -e "${YELLOW}Running Django system check...${NC}"
python manage.py check

# Run migrations
echo -e "${YELLOW}Running migrations...${NC}"
python manage.py migrate --verbosity=0

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
python manage.py test "$@"

echo -e "${GREEN}Tests completed successfully!${NC}"