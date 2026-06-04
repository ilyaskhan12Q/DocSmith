"""Tests for the generation pipeline."""

from docsmith.generation.planner import create_plan
from docsmith.generation.reviewer import review_document
from docsmith.generation.scorer import score_document
from docsmith.models.documentation_plan import (
    Audience,
    DocumentType,
    Tone,
)
from docsmith.models.generated_document import GeneratedDocument
from docsmith.models.repo_context import (
    DependencyInfo,
    Framework,
    Language,
    PackageManager,
    RepoContext,
)


def _make_ctx() -> RepoContext:
    """Create a test RepoContext."""
    return RepoContext(
        name="test-project",
        full_name="user/test-project",
        description="A test project",
        language=Language.PYTHON,
        framework=Framework.FASTAPI,
        package_manager=PackageManager.PIP,
        dependencies=[
            DependencyInfo(name="fastapi"),
            DependencyInfo(name="uvicorn"),
        ],
        has_tests=True,
        has_ci=True,
    )


class TestPlanner:
    """Tests for documentation planner."""

    def test_create_readme_plan(self):
        ctx = _make_ctx()
        plan = create_plan(ctx, [DocumentType.README])
        assert len(plan.documents) == 1
        assert plan.documents[0].doc_type == DocumentType.README
        assert len(plan.documents[0].sections) > 3

    def test_create_multi_plan(self):
        ctx = _make_ctx()
        plan = create_plan(
            ctx,
            [DocumentType.README, DocumentType.CONTRIBUTING, DocumentType.ARCHITECTURE],
        )
        assert len(plan.documents) == 3

    def test_plan_options(self):
        ctx = _make_ctx()
        plan = create_plan(
            ctx,
            [DocumentType.README],
            audience=Audience.BEGINNER,
            tone=Tone.CASUAL,
            use_emojis=False,
        )
        assert plan.audience == Audience.BEGINNER
        assert plan.tone == Tone.CASUAL
        assert plan.use_emojis is False


class TestReviewer:
    """Tests for documentation reviewer."""

    def test_passes_good_doc(self):
        ctx = _make_ctx()
        doc = GeneratedDocument(
            doc_type=DocumentType.README,
            filename="README.md",
            content="# Test Project\n\nA great project.\n\n## Installation\n\npip install test\n\n## Usage\n\nRun it.\n"
            * 5,
        )
        result = review_document(doc, ctx)
        assert result.passed is True

    def test_catches_short_doc(self):
        ctx = _make_ctx()
        doc = GeneratedDocument(
            doc_type=DocumentType.README,
            filename="README.md",
            content="# Hello",
        )
        result = review_document(doc, ctx)
        assert result.passed is False
        assert result.critical_count > 0

    def test_catches_placeholder(self):
        ctx = _make_ctx()
        doc = GeneratedDocument(
            doc_type=DocumentType.README,
            filename="README.md",
            content="# Project\n\n[your-username] should install this.\n\n## Installation\n\n## Usage\n"
            * 10,
        )
        result = review_document(doc, ctx)
        assert any(i.category == "placeholder" for i in result.issues)

    def test_catches_wrong_package_manager(self):
        ctx = _make_ctx()  # Uses pip
        doc = GeneratedDocument(
            doc_type=DocumentType.README,
            filename="README.md",
            content="# Project\n\n## Installation\n\nnpm install test-project\n\n## Usage\n\nRun it.\n"
            * 5,
        )
        result = review_document(doc, ctx)
        assert any(i.category == "hallucination" for i in result.issues)


class TestScorer:
    """Tests for documentation scorer."""

    def test_score_good_doc(self):
        ctx = _make_ctx()
        doc = GeneratedDocument(
            doc_type=DocumentType.README,
            filename="README.md",
            content=(
                "# test-project\n\n"
                "A test project built with python and fastapi.\n\n"
                "## Overview\n\nThis project uses fastapi and uvicorn.\n\n"
                "## Installation\n\n```bash\npip install test-project\n```\n\n"
                "## Usage\n\n```python\nimport test_project\n```\n\n"
                "## API\n\n| Method | Path |\n|---|---|\n| GET | /health |\n\n"
                "## License\n\nMIT\n"
            ),
        )
        score = score_document(doc, ctx)
        assert score.overall > 50
        assert score.completeness > 50
        assert score.examples > 50

    def test_score_minimal_doc(self):
        ctx = _make_ctx()
        doc = GeneratedDocument(
            doc_type=DocumentType.README,
            filename="README.md",
            content="# Hello\n\nWorld.",
        )
        score = score_document(doc, ctx)
        assert score.overall < 80
