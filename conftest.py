import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

@pytest.fixture(scope="session")
def test_data_dir():
    """Директория с тестовыми данными"""
    return os.path.join(os.path.dirname(__file__), "data")

@pytest.fixture
def clean_data_dir(test_data_dir):
    """Очистка тестовых данных перед тестами"""
    import shutil
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir, exist_ok=True)
    yield
    # Не удаляем после тестов для анализа