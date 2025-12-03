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

# Check if virtual environment exists (skip in CI)
if [ -d "env_stroll" ]; then
    # Activate virtual environment
    source env_stroll/bin/activate
elif [ -z "$CI" ]; then
    # Only require virtual env if not in CI
    echo -e "${RED}Virtual environment 'env_stroll' not found. Please create it first.${NC}"
    exit 1
else
    echo -e "${YELLOW}Skipping virtual environment activation (CI environment)${NC}"
fi

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

# Run Django unit tests
echo -e "${YELLOW}Running Django unit tests...${NC}"
python manage.py test "$@"

# Run Selenium tests in order
echo -e "${YELLOW}Running Selenium tests...${NC}"
echo -e "${YELLOW}Note: Make sure Django development server is running on http://localhost:8000${NC}"
cd ../SelTest

# Test order: accounts must be created first, then dogs, then jobs, then cleanup
SELENIUM_TESTS=(
    "test_ownerAccountCreation.py::TestOwnerAccountCreation::test_ownerAccountCreation"
    "test_walkerAccountCreation.py::TestWalkerAccountCreation::test_walkerAccountCreation"
    "test_accountediting.py::TestAccountediting::test_accountediting"
    "test_ownerDogCreation.py::TestOwnerDogCreation::test_ownerDogCreation"
    "test_dogediting.py::TestDogediting::test_dogediting"
    "test_ownerJobCreation.py::TestOwnerJobCreation::test_ownerJobCreation"
    "test_jobFiltering.py::TestJobFiltering::test_jobFiltering"
    "test_jobAcceptance.py::TestJobAcceptance::test_jobAcceptance"
    "test_jobDeletion.py::TestJobDeletion::test_jobDeletion"
    "test_ownerAccountDeletion.py::TestOwnerAccountDeletion::test_ownerAccountDeletion"
    "test_walkerAccountDeletion.py::TestWalkerAccountDeletion::test_walkerAccountDeletion"
)

SELENIUM_FAILED=0
for test in "${SELENIUM_TESTS[@]}"; do
    echo -e "${YELLOW}Running ${test}...${NC}"
    if pytest -v -s "$test"; then
        echo -e "${GREEN}${test} passed${NC}"
    else
        echo -e "${RED}${test} failed${NC}"
        SELENIUM_FAILED=1
    fi
done

if [ $SELENIUM_FAILED -eq 1 ]; then
    echo -e "${RED}Some Selenium tests failed${NC}"
    exit 1
fi

echo -e "${GREEN}All tests completed successfully!${NC}"