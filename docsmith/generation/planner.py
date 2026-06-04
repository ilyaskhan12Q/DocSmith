"""Documentation planner — creates structured plans before generation."""

from __future__ import annotations

from docsmith.models.documentation_plan import (
    Audience,
    DocumentationPlan,
    DocumentSection,
    DocumentSpec,
    DocumentType,
    Tone,
)
from docsmith.models.repo_context import RepoContext


def create_plan(
    ctx: RepoContext,
    doc_types: list[DocumentType],
    audience: Audience = Audience.INTERMEDIATE,
    tone: Tone = Tone.PROFESSIONAL,
    use_emojis: bool = True,
    include_badges: bool = True,
) -> DocumentationPlan:
    """Create a documentation plan based on repository analysis.

    The planner decides what sections each document should have,
    based on what was discovered during analysis.

    Args:
        ctx: Analyzed repository context.
        doc_types: Types of documents to generate.
        audience: Target audience level.
        tone: Writing tone.
        use_emojis: Whether to use emojis.
        include_badges: Whether to include badges.

    Returns:
        A DocumentationPlan ready for the writer.
    """
    documents = []

    for doc_type in doc_types:
        spec = _plan_document(ctx, doc_type)
        if spec:
            documents.append(spec)

    return DocumentationPlan(
        documents=documents,
        audience=audience,
        tone=tone,
        use_emojis=use_emojis,
        include_badges=include_badges,
    )


def _plan_document(ctx: RepoContext, doc_type: DocumentType) -> DocumentSpec | None:
    """Plan a single document based on repository context."""
    match doc_type:
        case DocumentType.README:
            return _plan_readme(ctx)
        case DocumentType.CONTRIBUTING:
            return _plan_contributing(ctx)
        case DocumentType.SECURITY:
            return _plan_security(ctx)
        case DocumentType.ARCHITECTURE:
            return _plan_architecture(ctx)
        case DocumentType.API_REFERENCE:
            return _plan_api_reference(ctx)
        case DocumentType.CHANGELOG:
            return _plan_changelog(ctx)
        case DocumentType.DEVELOPMENT_GUIDE:
            return _plan_dev_guide(ctx)
        case DocumentType.QUICKSTART:
            return _plan_quickstart(ctx)
        case _:
            return None


def _plan_readme(ctx: RepoContext) -> DocumentSpec:
    """Plan README.md sections."""
    sections = [
        DocumentSection(
            title="Header & Badges", description="Project name, badges, one-liner", priority=1
        ),
        DocumentSection(
            title="Introduction", description="What the project does and why", priority=1
        ),
        DocumentSection(title="Features", description="Key features list", priority=1),
        DocumentSection(
            title="Installation",
            description="How to install",
            priority=1,
            include_code_examples=True,
        ),
        DocumentSection(
            title="Quick Start",
            description="Minimal usage example",
            priority=1,
            include_code_examples=True,
        ),
    ]

    if ctx.api_endpoints:
        sections.append(
            DocumentSection(
                title="API Reference",
                description="Key endpoints",
                priority=2,
                include_code_examples=True,
            )
        )

    if ctx.cli_commands:
        sections.append(
            DocumentSection(
                title="CLI Usage",
                description="Available commands",
                priority=2,
                include_code_examples=True,
            )
        )

    if ctx.env_variables:
        sections.append(
            DocumentSection(title="Configuration", description="Environment variables", priority=2)
        )

    sections.extend(
        [
            DocumentSection(
                title="Usage Examples",
                description="Real-world usage examples",
                priority=2,
                include_code_examples=True,
            ),
            DocumentSection(
                title="Development", description="Dev setup and contributing", priority=3
            ),
        ]
    )

    if ctx.has_docs_folder:
        sections.append(
            DocumentSection(title="Documentation", description="Link to full docs", priority=3)
        )

    sections.extend(
        [
            DocumentSection(title="Roadmap", description="Future plans", priority=3),
            DocumentSection(title="License", description="License info", priority=3),
        ]
    )

    return DocumentSpec(
        doc_type=DocumentType.README,
        filename="README.md",
        sections=sections,
    )


def _plan_contributing(ctx: RepoContext) -> DocumentSpec:
    sections = [
        DocumentSection(title="Code of Conduct", description="Behavior expectations", priority=1),
        DocumentSection(
            title="Getting Started", description="How to start contributing", priority=1
        ),
        DocumentSection(
            title="Development Setup",
            description="Local dev environment",
            priority=1,
            include_code_examples=True,
        ),
        DocumentSection(
            title="Making Changes", description="Branch, commit, PR workflow", priority=1
        ),
        DocumentSection(title="Code Style", description="Formatting and linting rules", priority=2),
    ]
    if ctx.has_tests:
        sections.append(
            DocumentSection(
                title="Testing",
                description="How to run tests",
                priority=2,
                include_code_examples=True,
            )
        )
    sections.append(
        DocumentSection(title="Submitting PRs", description="PR process and checklist", priority=2)
    )
    return DocumentSpec(
        doc_type=DocumentType.CONTRIBUTING, filename="CONTRIBUTING.md", sections=sections
    )


def _plan_security(ctx: RepoContext) -> DocumentSpec:
    return DocumentSpec(
        doc_type=DocumentType.SECURITY,
        filename="SECURITY.md",
        sections=[
            DocumentSection(title="Security Policy", description="Supported versions", priority=1),
            DocumentSection(
                title="Reporting a Vulnerability", description="How to report", priority=1
            ),
            DocumentSection(
                title="Disclosure Policy", description="Disclosure timeline", priority=2
            ),
        ],
    )


def _plan_architecture(ctx: RepoContext) -> DocumentSpec:
    sections = [
        DocumentSection(title="System Overview", description="High-level architecture", priority=1),
        DocumentSection(
            title="Folder Structure", description="Directory layout explained", priority=1
        ),
        DocumentSection(
            title="Core Components", description="Key modules and their roles", priority=1
        ),
    ]
    if ctx.api_endpoints:
        sections.append(
            DocumentSection(
                title="Request Flow", description="How requests are processed", priority=2
            )
        )
    if ctx.dependencies:
        sections.append(
            DocumentSection(title="Dependency Graph", description="Key dependencies", priority=2)
        )
    sections.append(
        DocumentSection(
            title="Design Decisions", description="Why things are built this way", priority=3
        )
    )
    return DocumentSpec(
        doc_type=DocumentType.ARCHITECTURE, filename="ARCHITECTURE.md", sections=sections
    )


def _plan_api_reference(ctx: RepoContext) -> DocumentSpec:
    sections = []
    if ctx.api_endpoints:
        sections.append(
            DocumentSection(
                title="REST API",
                description="All API endpoints",
                priority=1,
                include_code_examples=True,
            )
        )
    if ctx.cli_commands:
        sections.append(
            DocumentSection(
                title="CLI Reference",
                description="All CLI commands",
                priority=1,
                include_code_examples=True,
            )
        )
    if ctx.classes:
        sections.append(DocumentSection(title="Classes", description="Public classes", priority=2))
    if ctx.functions:
        sections.append(
            DocumentSection(title="Functions", description="Public functions", priority=2)
        )
    if not sections:
        sections.append(
            DocumentSection(title="API Overview", description="Available interfaces", priority=1)
        )
    return DocumentSpec(
        doc_type=DocumentType.API_REFERENCE, filename="API_REFERENCE.md", sections=sections
    )


def _plan_changelog(ctx: RepoContext) -> DocumentSpec:
    return DocumentSpec(
        doc_type=DocumentType.CHANGELOG,
        filename="CHANGELOG.md",
        sections=[
            DocumentSection(
                title="Recent Changes", description="Based on commit history", priority=1
            )
        ],
        special_instructions="Generate from actual commit history. Do not invent releases.",
    )


def _plan_dev_guide(ctx: RepoContext) -> DocumentSpec:
    return DocumentSpec(
        doc_type=DocumentType.DEVELOPMENT_GUIDE,
        filename="DEVELOPMENT_GUIDE.md",
        sections=[
            DocumentSection(title="Prerequisites", description="Required tools", priority=1),
            DocumentSection(
                title="Setup",
                description="Dev environment setup",
                priority=1,
                include_code_examples=True,
            ),
            DocumentSection(title="Project Structure", description="Codebase overview", priority=2),
            DocumentSection(
                title="Testing", description="How to test", priority=2, include_code_examples=True
            ),
            DocumentSection(title="Debugging", description="Common issues", priority=3),
        ],
    )


def _plan_quickstart(ctx: RepoContext) -> DocumentSpec:
    return DocumentSpec(
        doc_type=DocumentType.QUICKSTART,
        filename="QUICKSTART.md",
        sections=[
            DocumentSection(
                title="Installation",
                description="Get it installed",
                priority=1,
                include_code_examples=True,
            ),
            DocumentSection(
                title="First Steps",
                description="Minimal working example",
                priority=1,
                include_code_examples=True,
            ),
            DocumentSection(title="Next Steps", description="Where to go from here", priority=2),
        ],
    )
