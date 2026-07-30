# ScubaMob Testing Guide

## Test Stack

- pytest
- pytest-django
- pytest-cov
- Django test utilities
- `unittest.mock` or pytest monkeypatching for provider boundaries

## Test Categories

### Model Tests

Cover:

- defaults;
- constraints;
- relationships;
- string representations;
- privacy-related properties;
- state transitions.

### Service Tests

Cover:

- business operations;
- provider success;
- provider errors;
- timeout behavior;
- invalid response data;
- authorization-independent domain rules.

### API Tests

Cover:

- authentication;
- object ownership;
- connection-only access;
- blocked-user behavior;
- validation;
- status codes;
- response shapes.

### Migration Tests

Add migration tests when transforming or preserving existing data.

## External Calls

Tests must not access live WeatherAPI, Google Maps, S3, email services, or other remote systems.

Patch the symbol where it is used, not where it was originally defined.

Example:

```python
def test_service_uses_weather_data(mocker):
    mocker.patch(
        "scuba.divesites.services.weather.Weather.get_weather_data",
        return_value={"current": {"temp_c": 20}},
    )
```

Prefer injecting a provider or using a fake provider for newly designed code.

## Required Commands

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
pytest --cov
```

## MySQL Validation

When a task affects database compatibility:

- run tests against MySQL when available;
- report the MySQL version and configuration;
- never claim MySQL support based solely on SQLite passing;
- check index lengths, constraints, JSON behavior, defaults, and migrations.

## Test Quality Rules

- assert behavior, not implementation trivia;
- keep fixtures focused;
- use factories if fixture setup becomes repetitive;
- avoid tests that depend on execution order;
- freeze or control time when testing schedules and expiration;
- ensure permission tests include a different authenticated user;
- test anonymous access separately.
