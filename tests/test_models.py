"""Tests for Pydantic data models."""

from docsmith.models.documentation_plan import (
    Audience,
    DocumentationPlan,
    DocumentSection,
    DocumentSpec,
    DocumentType,
    Tone,
)
from docsmith.models.generated_document import (
    GeneratedDocument,
    QualityScore,
    ReviewIssue,
    ReviewResult,
)
from docsmith.models.repo_context import (
    APIEndpoint,
    ClassInfo,
    CLICommand,
    DependencyInfo,
    Framework,
    FunctionInfo,
    Language,
    PackageManager,
    RepoContext,
)


class TestRepoContext:
    """Tests for RepoContext model."""

    def test_create_minimal(self):
        ctx = RepoContext(name="test-repo")
        assert ctx.name == "test-repo"
        assert ctx.language == Language.OTHER
        assert ctx.framework == Framework.NONE
        assert ctx.dependencies == []

    def test_create_full(self):
        ctx = RepoContext(
            name="my-api",
            full_name="user/my-api",
            description="A cool API",
            language=Language.PYTHON,
            framework=Framework.FASTAPI,
            package_manager=PackageManager.PIP,
            dependencies=[DependencyInfo(name="fastapi", version=">=0.100")],
            functions=[FunctionInfo(name="main", module="app.py")],
            classes=[ClassInfo(name="App", module="app.py")],
            api_endpoints=[APIEndpoint(method="GET", path="/health")],
            cli_commands=[CLICommand(name="serve")],
            has_tests=True,
            has_ci=True,
        )
        assert ctx.full_name == "user/my-api"
        assert len(ctx.dependencies) == 1
        assert ctx.has_tests is True

    def test_summary(self):
        ctx = RepoContext(
            name="test",
            language=Language.PYTHON,
            framework=Framework.FASTAPI,
        )
        summary = ctx.summary()
        assert "test" in summary
        assert "python" in summary
        assert "fastapi" in summary


class TestDocumentationPlan:
    """Tests for DocumentationPlan model."""

    def test_create_plan(self):
        plan = DocumentationPlan(
            documents=[
                DocumentSpec(
                    doc_type=DocumentType.README,
                    filename="README.md",
                    sections=[
                        DocumentSection(title="Intro", description="Introduction"),
                    ],
                )
            ],
            audience=Audience.INTERMEDIATE,
            tone=Tone.PROFESSIONAL,
        )
        assert len(plan.documents) == 1
        assert plan.document_types == [DocumentType.README]

    def test_get_spec(self):
        spec = DocumentSpec(doc_type=DocumentType.README, filename="README.md")
        plan = DocumentationPlan(documents=[spec])
        assert plan.get_spec(DocumentType.README) == spec
        assert plan.get_spec(DocumentType.SECURITY) is None


class TestQualityScore:
    """Tests for QualityScore model."""

    def test_overall_score(self):
        score = QualityScore(
            completeness=90,
            correctness=85,
            examples=80,
            usability=88,
            maintainability=92,
        )
        # Weighted: 90*0.25 + 85*0.30 + 80*0.15 + 88*0.20 + 92*0.10
        # = 22.5 + 25.5 + 12.0 + 17.6 + 9.2 = 86.8 ≈ 87
        assert score.overall == 87

    def test_perfect_score(self):
        score = QualityScore(
            completeness=100,
            correctness=100,
            examples=100,
            usability=100,
            maintainability=100,
        )
        assert score.overall == 100


class TestReviewResult:
    """Tests for ReviewResult model."""

    def test_counts(self):
        result = ReviewResult(
            issues=[
                ReviewIssue(
                    severity="critical", category="hallucination", description="Fake feature"
                ),
                ReviewIssue(
                    severity="warning", category="missing", description="No install section"
                ),
                ReviewIssue(severity="warning", category="placeholder", description="Found [TODO]"),
                ReviewIssue(
                    severity="info", category="style", description="Could use more examples"
                ),
            ],
            passed=False,
        )
        assert result.critical_count == 1
        assert result.warning_count == 2


class TestGeneratedDocument:
    """Tests for GeneratedDocument model."""

    def test_overall_score_property(self):
        doc = GeneratedDocument(
            doc_type=DocumentType.README,
            filename="README.md",
            content="# Hello",
            score=QualityScore(
                completeness=80,
                correctness=90,
                examples=70,
                usability=85,
                maintainability=75,
            ),
        )
        assert doc.overall_score > 0

    def test_no_score(self):
        doc = GeneratedDocument(
            doc_type=DocumentType.README,
            filename="README.md",
            content="# Hello",
        )
        assert doc.overall_score == 0
