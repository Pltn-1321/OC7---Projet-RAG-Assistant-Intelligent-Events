"""Pytest configuration and shared fixtures."""

import json
import os
from pathlib import Path
from typing import Generator

import pytest
from pydantic import HttpUrl

# Fix OpenMP library conflict on macOS (faiss + numpy/torch)
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

from src.data.models import Coordinates, DateRange, Event, Location


@pytest.fixture
def test_data_dir() -> Path:
    """Get test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_event() -> Event:
    """Create a sample event for testing."""
    from datetime import datetime, timedelta

    now = datetime.now()
    return Event(
        id="test-event-001",
        title="Concert de Jazz au Caveau",
        description="<p>Soirée jazz manouche avec Django Legacy Quartet</p>",
        description_clean="Soirée jazz manouche avec Django Legacy Quartet",
        location=Location(
            city="Paris",
            address="15 rue de la Huchette",
            postal_code="75005",
            region="Île-de-France",
            country="France",
            coordinates=Coordinates(lat=48.8534, lon=2.3488),
        ),
        dates=DateRange(
            start=now + timedelta(days=7),
            end=now + timedelta(days=7, hours=3),
        ),
        price="15€",
        category="Concert",
        url=HttpUrl("https://openagenda.com/event/test-001"),
        image_url=HttpUrl("https://example.com/image.jpg"),
        organizer="Caveau de la Huchette",
        tags=["jazz", "concert", "musique"],
    )


@pytest.fixture
def sample_events() -> list[Event]:
    """Create multiple sample events for testing."""
    from datetime import datetime, timedelta

    now = datetime.now()

    return [
        Event(
            id=f"event-{i}",
            title=f"Test Event {i}",
            description=f"Description for event {i}",
            description_clean=f"Description for event {i}",
            location=Location(
                city="Paris" if i % 2 == 0 else "Lyon",
                address=f"{i} rue de Test",
                postal_code="75001",
            ),
            dates=DateRange(
                start=now + timedelta(days=i),
                end=now + timedelta(days=i, hours=2),
            ),
            price="Gratuit" if i % 3 == 0 else f"{i * 5}€",
            category="Concert" if i % 2 == 0 else "Exposition",
            url=HttpUrl(f"https://openagenda.com/event/{i}"),
            tags=[f"tag{i}"],
        )
        for i in range(1, 11)
    ]


@pytest.fixture
def mock_env_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary .env file for testing."""
    env_file = tmp_path / ".env"
    env_content = """
MISTRAL_API_KEY=test_key_123
OPENAGENDA_API_KEY=test_agenda_key
LOG_LEVEL=DEBUG
INDEX_PATH=data/indexes/faiss_index
MAX_EVENTS=100
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=mistral-small-latest
LLM_TEMPERATURE=0.3
TOP_K_RESULTS=5
"""
    env_file.write_text(env_content)
    yield env_file
    env_file.unlink()


@pytest.fixture
def sample_test_questions(test_data_dir: Path) -> list[dict]:
    """Load sample test questions."""
    questions_file = test_data_dir / "test_questions.json"
    if questions_file.exists():
        with open(questions_file) as f:
            return json.load(f)
    return [
        {
            "id": 1,
            "question": "Quels concerts jazz ce weekend à Paris ?",
            "expected_keywords": ["concert", "jazz", "paris", "weekend"],
            "category": "recherche_simple",
        },
        {
            "id": 2,
            "question": "Événements gratuits pour enfants dimanche",
            "expected_keywords": ["gratuit", "enfants", "dimanche"],
            "category": "filtres_multiples",
        },
    ]


@pytest.fixture
def mock_faiss_index(tmp_path: Path) -> Path:
    """Create a mock FAISS index directory."""
    index_dir = tmp_path / "faiss_index"
    index_dir.mkdir(parents=True, exist_ok=True)
    return index_dir


# Markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line(
        "markers", "requires_api: marks tests that require API credentials"
    )
