"""Tests unitaires pour les modeles Pydantic."""

from datetime import datetime, timedelta

import pytest
from pydantic import HttpUrl, ValidationError

from src.data.models import (
    Coordinates,
    DateRange,
    EvaluationQuestion,
    EvaluationResult,
    Event,
    Location,
    QueryResponse,
)


class TestCoordinates:
    """Tests pour le modele Coordinates."""

    def test_valid_coordinates(self):
        """Test avec des coordonnees valides."""
        coords = Coordinates(lat=48.8566, lon=2.3522)
        assert coords.lat == 48.8566
        assert coords.lon == 2.3522

    def test_boundary_latitude_positive(self):
        """Test avec latitude maximale (90)."""
        coords = Coordinates(lat=90.0, lon=0.0)
        assert coords.lat == 90.0

    def test_boundary_latitude_negative(self):
        """Test avec latitude minimale (-90)."""
        coords = Coordinates(lat=-90.0, lon=0.0)
        assert coords.lat == -90.0

    def test_boundary_longitude_positive(self):
        """Test avec longitude maximale (180)."""
        coords = Coordinates(lat=0.0, lon=180.0)
        assert coords.lon == 180.0

    def test_boundary_longitude_negative(self):
        """Test avec longitude minimale (-180)."""
        coords = Coordinates(lat=0.0, lon=-180.0)
        assert coords.lon == -180.0

    def test_invalid_latitude_too_high(self):
        """Test avec latitude invalide (> 90)."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(lat=91.0, lon=0.0)
        assert "lat" in str(exc_info.value)

    def test_invalid_latitude_too_low(self):
        """Test avec latitude invalide (< -90)."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(lat=-91.0, lon=0.0)
        assert "lat" in str(exc_info.value)

    def test_invalid_longitude_too_high(self):
        """Test avec longitude invalide (> 180)."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(lat=0.0, lon=181.0)
        assert "lon" in str(exc_info.value)

    def test_invalid_longitude_too_low(self):
        """Test avec longitude invalide (< -180)."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(lat=0.0, lon=-181.0)
        assert "lon" in str(exc_info.value)


class TestLocation:
    """Tests pour le modele Location."""

    def test_valid_location_minimal(self):
        """Test avec les champs minimaux requis."""
        loc = Location(city="Paris")
        assert loc.city == "Paris"
        assert loc.country == "France"  # valeur par defaut
        assert loc.address is None
        assert loc.postal_code is None

    def test_valid_location_complete(self):
        """Test avec tous les champs."""
        coords = Coordinates(lat=48.8566, lon=2.3522)
        loc = Location(
            city="Paris",
            address="1 rue de Rivoli",
            postal_code="75001",
            region="Ile-de-France",
            country="France",
            coordinates=coords,
        )
        assert loc.city == "Paris"
        assert loc.address == "1 rue de Rivoli"
        assert loc.coordinates.lat == 48.8566

    def test_city_validation_strips_whitespace(self):
        """Test que les espaces sont supprimes."""
        loc = Location(city="  paris  ")
        assert loc.city == "Paris"

    def test_city_validation_title_case(self):
        """Test que la ville est en title case."""
        loc = Location(city="marseille")
        assert loc.city == "Marseille"

    def test_city_validation_complex_name(self):
        """Test avec un nom de ville compose."""
        loc = Location(city="aix-en-provence")
        assert loc.city == "Aix-En-Provence"

    def test_empty_city_raises_error(self):
        """Test qu'une ville vide leve une erreur."""
        with pytest.raises(ValidationError) as exc_info:
            Location(city="")
        assert "city" in str(exc_info.value)

    def test_whitespace_only_city_raises_error(self):
        """Test qu'une ville avec uniquement des espaces leve une erreur."""
        with pytest.raises(ValidationError) as exc_info:
            Location(city="   ")
        # Apres strip(), la ville sera vide mais validee par le validator
        # Le min_length=1 devrait rejeter apres strip


class TestDateRange:
    """Tests pour le modele DateRange."""

    def test_valid_date_range(self):
        """Test avec une plage de dates valide."""
        start = datetime.now()
        end = start + timedelta(hours=2)
        dr = DateRange(start=start, end=end)
        assert dr.start == start
        assert dr.end == end

    def test_duration_hours_calculation(self):
        """Test du calcul de duree en heures."""
        start = datetime(2024, 1, 1, 10, 0)
        end = datetime(2024, 1, 1, 12, 30)
        dr = DateRange(start=start, end=end)
        assert dr.duration_hours == 2.5

    def test_duration_hours_multi_day(self):
        """Test du calcul de duree sur plusieurs jours."""
        start = datetime(2024, 1, 1, 10, 0)
        end = datetime(2024, 1, 3, 10, 0)
        dr = DateRange(start=start, end=end)
        assert dr.duration_hours == 48.0

    def test_end_equals_start(self):
        """Test avec fin egale au debut (duree 0)."""
        now = datetime.now()
        dr = DateRange(start=now, end=now)
        assert dr.duration_hours == 0.0

    def test_end_before_start_raises_error(self):
        """Test qu'une date de fin anterieure leve une erreur."""
        start = datetime.now()
        end = start - timedelta(hours=1)
        with pytest.raises(ValidationError) as exc_info:
            DateRange(start=start, end=end)
        assert "End date must be after start date" in str(exc_info.value)


class TestEvent:
    """Tests pour le modele Event."""

    def test_event_creation_from_fixture(self, sample_event):
        """Test de creation avec la fixture."""
        assert sample_event.id == "test-event-001"
        assert sample_event.title == "Concert de Jazz au Caveau"
        assert sample_event.location.city == "Paris"

    def test_is_free_property_gratuit(self, sample_event):
        """Test is_free avec 'Gratuit'."""
        sample_event.price = "Gratuit"
        assert sample_event.is_free is True

    def test_is_free_property_free(self, sample_event):
        """Test is_free avec 'Free'."""
        sample_event.price = "Free"
        assert sample_event.is_free is True

    def test_is_free_property_zero_euro(self, sample_event):
        """Test is_free avec '0 euros'."""
        sample_event.price = "0 euros"
        assert sample_event.is_free is True

    def test_is_free_property_paid(self, sample_event):
        """Test is_free avec un prix."""
        sample_event.price = "15 euros"
        assert sample_event.is_free is False

    def test_is_free_property_none(self, sample_event):
        """Test is_free avec prix None."""
        sample_event.price = None
        assert sample_event.is_free is False

    def test_is_upcoming_future_event(self, sample_event):
        """Test is_upcoming avec un evenement futur."""
        # La fixture cree un evenement dans 7 jours
        assert sample_event.is_upcoming is True

    def test_is_past_past_event(self):
        """Test is_past avec un evenement passe."""
        past_start = datetime.now() - timedelta(days=30)
        past_end = datetime.now() - timedelta(days=29)
        event = Event(
            id="past-event",
            title="Evenement passe",
            description="Description",
            location=Location(city="Paris"),
            dates=DateRange(start=past_start, end=past_end),
            url=HttpUrl("https://example.com"),
        )
        assert event.is_past is True
        assert event.is_upcoming is False

    def test_to_search_text_contains_required_fields(self, sample_event):
        """Test que to_search_text contient les champs importants."""
        text = sample_event.to_search_text()
        assert "Concert de Jazz" in text
        assert "Paris" in text
        assert "Titre:" in text
        assert "Description:" in text

    def test_to_search_text_with_price(self, sample_event):
        """Test que to_search_text inclut le prix."""
        text = sample_event.to_search_text()
        assert "Prix:" in text

    def test_to_search_text_with_tags(self, sample_event):
        """Test que to_search_text inclut les tags."""
        text = sample_event.to_search_text()
        assert "Tags:" in text
        assert "jazz" in text

    def test_to_display_dict_structure(self, sample_event):
        """Test la structure de to_display_dict."""
        display = sample_event.to_display_dict()
        assert "id" in display
        assert "title" in display
        assert "city" in display
        assert "date" in display
        assert "is_free" in display
        assert display["title"] == sample_event.title
        assert display["city"] == "Paris"

    def test_tags_validation_lowercase(self):
        """Test que les tags sont convertis en minuscules."""
        event = Event(
            id="test",
            title="Test Event",
            description="Description",
            location=Location(city="Paris"),
            dates=DateRange(
                start=datetime.now(),
                end=datetime.now() + timedelta(hours=1),
            ),
            url=HttpUrl("https://example.com"),
            tags=["JAZZ", "Concert", "MUSIQUE"],
        )
        assert event.tags == ["jazz", "concert", "musique"]

    def test_tags_validation_strips_whitespace(self):
        """Test que les tags sont nettoyes des espaces."""
        event = Event(
            id="test",
            title="Test Event",
            description="Description",
            location=Location(city="Paris"),
            dates=DateRange(
                start=datetime.now(),
                end=datetime.now() + timedelta(hours=1),
            ),
            url=HttpUrl("https://example.com"),
            tags=["  jazz  ", " concert "],
        )
        assert event.tags == ["jazz", "concert"]

    def test_title_validation_strips_whitespace(self):
        """Test que le titre est nettoye des espaces."""
        event = Event(
            id="test",
            title="  Test Event  ",
            description="Description",
            location=Location(city="Paris"),
            dates=DateRange(
                start=datetime.now(),
                end=datetime.now() + timedelta(hours=1),
            ),
            url=HttpUrl("https://example.com"),
        )
        assert event.title == "Test Event"

    def test_empty_description_raises_error(self):
        """Test qu'une description vide leve une erreur."""
        with pytest.raises(ValidationError) as exc_info:
            Event(
                id="test",
                title="Test",
                description="   ",
                location=Location(city="Paris"),
                dates=DateRange(
                    start=datetime.now(),
                    end=datetime.now() + timedelta(hours=1),
                ),
                url=HttpUrl("https://example.com"),
            )
        assert "Description cannot be empty" in str(exc_info.value)


class TestEvaluationQuestion:
    """Tests pour le modele EvaluationQuestion."""

    def test_valid_question(self):
        """Test avec une question valide."""
        q = EvaluationQuestion(
            id=1,
            question="Quels concerts jazz a Paris?",
            expected_keywords=["concert", "jazz", "paris"],
            category="recherche",
        )
        assert q.id == 1
        assert len(q.expected_keywords) == 3
        assert q.category == "recherche"

    def test_question_with_default_category(self):
        """Test avec la categorie par defaut."""
        q = EvaluationQuestion(
            id=1,
            question="Test question",
        )
        assert q.category == "general"
        assert q.expected_keywords == []

    def test_question_too_short(self):
        """Test qu'une question trop courte leve une erreur."""
        with pytest.raises(ValidationError) as exc_info:
            EvaluationQuestion(id=1, question="ab")
        assert "question" in str(exc_info.value)

    def test_question_with_notes(self):
        """Test avec des notes optionnelles."""
        q = EvaluationQuestion(
            id=1,
            question="Question test",
            notes="Note importante",
        )
        assert q.notes == "Note importante"


class TestEvaluationResult:
    """Tests pour le modele EvaluationResult."""

    def test_keyword_coverage_calculation(self):
        """Test du calcul de couverture des mots-cles."""
        result = EvaluationResult(
            question_id=1,
            question="Test question",
            answer="Test answer",
            latency=1.5,
            relevance_score=0.85,
            sources_count=3,
            keywords_found=2,
            keywords_total=4,
            passed=True,
        )
        assert result.keyword_coverage == 0.5

    def test_keyword_coverage_zero_total(self):
        """Test de couverture avec 0 mots-cles attendus."""
        result = EvaluationResult(
            question_id=1,
            question="Test",
            answer="Answer",
            latency=1.0,
            relevance_score=0.8,
            sources_count=2,
            keywords_found=0,
            keywords_total=0,
            passed=True,
        )
        assert result.keyword_coverage == 1.0

    def test_keyword_coverage_full(self):
        """Test de couverture complete."""
        result = EvaluationResult(
            question_id=1,
            question="Test",
            answer="Answer",
            latency=1.0,
            relevance_score=0.9,
            sources_count=5,
            keywords_found=3,
            keywords_total=3,
            passed=True,
        )
        assert result.keyword_coverage == 1.0

    def test_invalid_relevance_score_too_high(self):
        """Test qu'un score de pertinence > 1 leve une erreur."""
        with pytest.raises(ValidationError):
            EvaluationResult(
                question_id=1,
                question="Test",
                answer="Answer",
                latency=1.0,
                relevance_score=1.5,  # invalide
                sources_count=2,
                keywords_found=1,
                keywords_total=2,
                passed=True,
            )

    def test_invalid_negative_latency(self):
        """Test qu'une latence negative leve une erreur."""
        with pytest.raises(ValidationError):
            EvaluationResult(
                question_id=1,
                question="Test",
                answer="Answer",
                latency=-1.0,  # invalide
                relevance_score=0.8,
                sources_count=2,
                keywords_found=1,
                keywords_total=2,
                passed=True,
            )


class TestQueryResponse:
    """Tests pour le modele QueryResponse."""

    def test_sources_count_property(self, sample_events):
        """Test de la propriete sources_count."""
        response = QueryResponse(
            answer="Voici les evenements",
            sources=sample_events[:3],
            latency=1.5,
            query="concerts a paris",
            top_k=5,
        )
        assert response.sources_count == 3

    def test_to_dict_structure(self, sample_events):
        """Test de la structure de to_dict."""
        response = QueryResponse(
            answer="Voici les evenements",
            sources=sample_events[:2],
            latency=1.567,
            query="concerts",
            top_k=5,
        )
        result = response.to_dict()
        assert result["answer"] == "Voici les evenements"
        assert result["latency"] == 1.57  # arrondi
        assert result["sources_count"] == 2
        assert len(result["sources"]) == 2
