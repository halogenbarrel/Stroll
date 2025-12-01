# Testing Guide

This document explains how to run tests locally and in CI/CD pipelines.

## Local Testing

### Prerequisites
- Python 3.11+ installed
- Virtual environment set up (`env_stroll`)
- Dependencies installed (`pip install -r requirements.txt`)

### Running Tests

#### Basic Test Run
```bash
./run-tests.sh
```


#### Run Specific Tests
```bash
./run-tests.sh job_board.tests_forms
./run-tests.sh job_board.tests_views.JobBoardViewsTests.test_job_create_post_valid
```

#### Manual Test Run
```bash
# Activate virtual environment
source env_stroll/bin/activate

# Change to app directory
cd app

# Run tests
python manage.py test
```

## CI/CD Testing

### GitHub Actions Workflow

The project includes GitHub Actions workflows that run tests on pull requests and pushes to main branches.

#### Workflow Triggers
- Pull requests to `main`, `master`, or `devel` branches
- Direct pushes to `main`, `master`, or `devel` branches

#### Workflow Files
- `.github/workflows/tests.yml` - Full workflow with test execution
- `.github/workflows/tests-simple.yml` - Basic workflow

## Test Structure

### Forms Tests (`job_board/tests_forms.py`)
- `JobForm` validation and saving
- User-based dog filtering
- Form field validation

### Views Tests (`job_board/tests_views.py`)
- Authentication requirements
- Authorization and permission checks
- CRUD operations (Create, Read, Update, Delete)
- Error handling and redirects

### Test Data Setup
Tests use Django's `TestCase` with proper setup:
- Test users (owners and walkers)
- Test data (dogs, jobs)
- Proper cleanup between tests

## Writing New Tests

### Basic Test Structure
```python
from django.test import TestCase
from django.contrib.auth.models import User

class MyTests(TestCase):
    def setUp(self):
        # Create test data
        self.user = User.objects.create_user(username='test', password='test')

    def test_something(self):
        # Login if needed
        self.client.login(username='test', password='test')

        # Test your functionality
        response = self.client.get('/some-url/')
        self.assertEqual(response.status_code, 200)
```

### Testing Authenticated Views
```python
def test_authenticated_view(self):
    self.client.login(username='testuser', password='testpass')
    response = self.client.get('/protected-url/')
    self.assertEqual(response.status_code, 200)
```

### Testing Form Submissions
```python
def test_form_submission(self):
    self.client.login(username='testuser', password='testpass')
    data = {'field1': 'value1', 'field2': 'value2'}
    response = self.client.post('/form-url/', data)
    self.assertEqual(response.status_code, 302)  # Redirect after success
```

## Troubleshooting

### Common Issues

1. **Virtual Environment Issues**
   - Ensure `env_stroll` exists and is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **Database Issues**
   - Run migrations: `python manage.py migrate`
   - Reset test database: `python manage.py test --keepdb=false`


4. **CI/CD Failures**
   - Check GitHub Actions logs
   - Ensure all dependencies are in `requirements.txt`
   - Verify Django settings work in CI environment

### Debug Commands
```bash
# Verbose test output
python manage.py test --verbosity=2

# Keep test database for debugging
python manage.py test --keepdb

# Run specific test method
python manage.py test job_board.tests_forms.JobBoardFormsTests.test_job_form_valid

# Run tests in parallel for faster execution
python manage.py test --parallel auto
```
