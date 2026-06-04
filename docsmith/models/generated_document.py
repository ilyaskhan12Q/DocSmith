"""Generated document models — output of the documentation pipeline."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from docsmith.models.documentation_plan import DocumentType


class ReviewIssue(BaseModel):
    """An issue found during documentation review."""

    severity: str = Field(description="critical/warning/info")
    category: str = Field(description="Issue category (hallucination, missing, broken, etc.)")
    description: str = Field(description="What the issue is")
    suggestion: str = Field(default="", description="How to fix it")


class ReviewResult(BaseModel):
    """Result of the documentation review pass."""

    issues: list[ReviewIssue] = Field(default_factory=list, description="Issues found")
    passed: bool = Field(default=True, description="Whether the review passed")
    summary: str = Field(default="", description="Review summary")

    @property
    def critical_count(self) -> int:
        """Count critical issues."""
        return sum(1 for i in self.issues if i.severity == "critical")

    @property
    def warning_count(self) -> int:
        """Count warning issues."""
        return sum(1 for i in self.issues if i.severity == "warning")


class QualityScore(BaseModel):
    """Quality score for a generated document."""

    completeness: int = Field(default=0, ge=0, le=100, description="Completeness score")
    correctness: int = Field(default=0, ge=0, le=100, description="Correctness score")
    examples: int = Field(default=0, ge=0, le=100, description="Code examples quality")
    usability: int = Field(default=0, ge=0, le=100, description="Usability score")
    maintainability: int = Field(default=0, ge=0, le=100, description="Maintainability score")

    @property
    def overall(self) -> int:
        """Calculate weighted overall score."""
        weights = {
            "completeness": 0.25,
            "correctness": 0.30,
            "examples": 0.15,
            "usability": 0.20,
            "maintainability": 0.10,
        }
        return round(
            self.completeness * weights["completeness"]
            + self.correctness * weights["correctness"]
            + self.examples * weights["examples"]
            + self.usability * weights["usability"]
            + self.maintainability * weights["maintainability"]
        )


class GeneratedDocument(BaseModel):
    """A fully generated and reviewed document."""

    doc_type: DocumentType = Field(description="Type of document")
    filename: str = Field(description="Output filename")
    content: str = Field(default="", description="Generated markdown content")
    review: ReviewResult | None = Field(default=None, description="Review results")
    score: QualityScore | None = Field(default=None, description="Quality score")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    generation_time_seconds: float = Field(default=0.0, description="Time taken to generate")
    refined: bool = Field(default=False, description="Whether this was refined after review")

    @property
    def overall_score(self) -> int:
        """Get overall quality score."""
        return self.score.overall if self.score else 0
