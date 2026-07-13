# conftest.py — project-level pytest configuration
import pytest

# Suppress asyncio mode warning across entire project
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as requiring a live service (deselect with -m 'not integration')"
    )
