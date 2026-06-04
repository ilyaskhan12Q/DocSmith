"""Documentation plan models — what to generate and how to structure it."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Types of documentation that DocSmith can generate."""

    README = "README"
    CONTRIBUTING = "CONTRIBUTING"
    SECURITY = "SECURITY"
    LICENSE = "LICENSE"
    CHANGELOG = "CHANGELOG"
    ARCHITECTURE = "ARCHITECTURE"
    API_REFERENCE = "API_REFERENCE"
    DEVELOPMENT_GUIDE = "DEVELOPMENT_GUIDE"
    QUICKSTART = "QUICKSTART"


class Audience(str, Enum):
    """Target audience level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Tone(str, Enum):
    """Documentation tone."""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FUN = "fun"


class DocumentSection(BaseModel):
    """A planned section within a document."""

    title: str = Field(description="Section heading")
    description: str = Field(default="", description="What this section should cover")
    priority: int = Field(default=1, description="Priority (1=highest)")
    include_code_examples: bool = Field(default=False, description="Whether to include code")
    estimated_length: str = Field(default="medium", description="short/medium/long")


class DocumentSpec(BaseModel):
    """Specification for a single document to generate."""

    doc_type: DocumentType = Field(description="Type of document")
    filename: str = Field(description="Output filename (e.g., README.md)")
    sections: list[DocumentSection] = Field(default_factory=list, description="Planned sections")
    special_instructions: str = Field(default="", description="Extra instructions for generation")


class DocumentationPlan(BaseModel):
    """The complete plan for documentation generation.

    Created by the Planner, consumed by the Writer.
    """

    documents: list[DocumentSpec] = Field(default_factory=list, description="Documents to generate")
    audience: Audience = Field(default=Audience.INTERMEDIATE, description="Target audience")
    tone: Tone = Field(default=Tone.PROFESSIONAL, description="Writing tone")
    use_emojis: bool = Field(default=True, description="Include emojis in output")
    include_badges: bool = Field(default=True, description="Include shields.io badges")
    output_language: str = Field(default="english", description="Output language")

    @property
    def document_types(self) -> list[DocumentType]:
        """Get list of document types in the plan."""
        return [doc.doc_type for doc in self.documents]

    def get_spec(self, doc_type: DocumentType) -> DocumentSpec | None:
        """Get the spec for a specific document type."""
        for doc in self.documents:
            if doc.doc_type == doc_type:
                return doc
        return None
