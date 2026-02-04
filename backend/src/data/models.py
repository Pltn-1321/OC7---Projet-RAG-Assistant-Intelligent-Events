"""Data models for events using Pydantic."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Coordinates(BaseModel):
    """Geographic coordinates."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")


class Location(BaseModel):
    """Event location information."""

    city: str = Field(..., min_length=1, description="City name")
    address: Optional[str] = Field(None, description="Street address")
    postal_code: Optional[str] = Field(None, description="Postal code")
    region: Optional[str] = Field(None, description="Region or department")
    country: str = Field("France", description="Country")
    coordinates: Optional[Coordinates] = Field(None, description="GPS coordinates")

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str) -> str:
        """Validate and clean city name."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("City name cannot be empty or whitespace-only")
        return cleaned.title()


class DateRange(BaseModel):
    """Event date range."""

    start: datetime = Field(..., description="Event start date and time")
    end: datetime = Field(..., description="Event end date and time")

    @field_validator("end")
    @classmethod
    def validate_end_after_start(cls, v: datetime, info) -> datetime:
        """Ensure end date is after start date."""
        if "start" in info.data and v < info.data["start"]:
            raise ValueError("End date must be after start date")
        return v

    @property
    def duration_hours(self) -> float:
        """Calculate event duration in hours."""
        delta = self.end - self.start
        return delta.total_seconds() / 3600


class Event(BaseModel):
    """Complete event model."""

    id: str = Field(..., min_length=1, description="Unique event identifier")
    title: str = Field(..., min_length=1, max_length=500, description="Event title")
    description: str = Field(..., description="Event description (can be HTML)")
    description_clean: Optional[str] = Field(None, description="Cleaned description (no HTML)")
    location: Location = Field(..., description="Event location")
    dates: DateRange = Field(..., description="Event date range")
    price: Optional[str] = Field(None, description="Event price or pricing information")
    category: str = Field("Événement", description="Event category")
    url: HttpUrl = Field(..., description="Event URL on Open Agenda")
    image_url: Optional[HttpUrl] = Field(None, description="Event image URL")
    organizer: Optional[str] = Field(None, description="Event organizer")
    tags: list[str] = Field(default_factory=list, description="Event tags")
    accessibility: Optional[dict[str, bool]] = Field(None, description="Accessibility information")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and clean title."""
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description."""
        if len(v.strip()) == 0:
            raise ValueError("Description cannot be empty")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Clean and validate tags."""
        return [tag.strip().lower() for tag in v if tag.strip()]

    @property
    def is_free(self) -> bool:
        """Check if event is free."""
        if not self.price:
            return False
        price_lower = self.price.lower()
        return any(
            word in price_lower for word in ["gratuit", "free", "libre", "0€", "0 €", "0 euros"]
        )

    @property
    def is_upcoming(self) -> bool:
        """Check if event is upcoming."""
        return self.dates.start > datetime.now()

    @property
    def is_past(self) -> bool:
        """Check if event is in the past."""
        return self.dates.end < datetime.now()

    @property
    def is_ongoing(self) -> bool:
        """Check if event is currently ongoing."""
        now = datetime.now()
        return self.dates.start <= now <= self.dates.end

    def to_search_text(self) -> str:
        """
        Convert event to searchable text for embedding.

        Returns:
            Formatted text containing all relevant event information
        """
        parts = [
            f"Titre: {self.title}",
            f"Description: {self.description_clean or self.description[:500]}",
            f"Catégorie: {self.category}",
            f"Lieu: {self.location.city}",
        ]

        if self.location.address:
            parts.append(f"Adresse: {self.location.address}")

        parts.append(f"Date: {self.dates.start.strftime('%d/%m/%Y %H:%M')}")

        if self.price:
            parts.append(f"Prix: {self.price}")

        if self.organizer:
            parts.append(f"Organisateur: {self.organizer}")

        if self.tags:
            parts.append(f"Tags: {', '.join(self.tags)}")

        return "\n".join(parts)

    def to_display_dict(self) -> dict:
        """
        Convert event to dictionary for display purposes.

        Returns:
            Dictionary with formatted event information
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description_clean or self.description,
            "city": self.location.city,
            "address": self.location.address,
            "date": self.dates.start.strftime("%d/%m/%Y à %H:%M"),
            "end_date": self.dates.end.strftime("%d/%m/%Y à %H:%M"),
            "price": self.price or "Non spécifié",
            "category": self.category,
            "url": str(self.url),
            "image_url": str(self.image_url) if self.image_url else None,
            "organizer": self.organizer,
            "tags": self.tags,
            "is_free": self.is_free,
            "is_upcoming": self.is_upcoming,
        }


class QueryResponse(BaseModel):
    """Response model for RAG queries."""

    answer: str = Field(..., description="Generated answer from LLM")
    sources: list[Event] = Field(..., description="Source events used for answer")
    latency: float = Field(..., ge=0, description="Query latency in seconds")
    query: str = Field(..., description="Original user query")
    top_k: int = Field(..., description="Number of sources retrieved")

    @property
    def sources_count(self) -> int:
        """Get number of source events."""
        return len(self.sources)

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "answer": self.answer,
            "sources": [event.to_display_dict() for event in self.sources],
            "latency": round(self.latency, 2),
            "query": self.query,
            "sources_count": self.sources_count,
        }


class EvaluationQuestion(BaseModel):
    """Model for evaluation test questions."""

    id: int = Field(..., description="Question ID")
    question: str = Field(..., min_length=3, description="Test question")
    expected_keywords: list[str] = Field(
        default_factory=list, description="Keywords expected in answer"
    )
    category: str = Field("general", description="Question category")
    expected_event_count: Optional[int] = Field(None, description="Expected number of events")
    notes: Optional[str] = Field(None, description="Additional notes")


class EvaluationResult(BaseModel):
    """Model for evaluation results."""

    question_id: int = Field(..., description="Question ID")
    question: str = Field(..., description="Test question")
    answer: str = Field(..., description="Generated answer")
    latency: float = Field(..., ge=0, description="Query latency")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score (0-1)")
    sources_count: int = Field(..., ge=0, description="Number of sources returned")
    keywords_found: int = Field(..., ge=0, description="Number of expected keywords found")
    keywords_total: int = Field(..., ge=0, description="Total expected keywords")
    passed: bool = Field(..., description="Whether test passed")

    @property
    def keyword_coverage(self) -> float:
        """Calculate keyword coverage percentage."""
        if self.keywords_total == 0:
            return 1.0
        return self.keywords_found / self.keywords_total
