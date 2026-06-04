"""Documentation writer — generates documents using AI providers."""

from __future__ import annotations

import time
from pathlib import Path

from jinja2 import Template
from rich.console import Console

from docsmith.ai.orchestrator import generate_with_retry
from docsmith.ai.providers.base import BaseProvider
from docsmith.models.documentation_plan import DocumentationPlan, DocumentSpec, DocumentType
from docsmith.models.generated_document import GeneratedDocument
from docsmith.models.repo_context import RepoContext

console = Console()

# Prompt template directory
PROMPTS_DIR = Path(__file__).parent.parent / "ai" / "prompts"

# Map document types to prompt template files
_TEMPLATE_MAP: dict[DocumentType, str] = {
    DocumentType.README: "readme.txt",
    DocumentType.CONTRIBUTING: "contributing.txt",
    DocumentType.SECURITY: "security.txt",
    DocumentType.ARCHITECTURE: "architecture.txt",
    DocumentType.API_REFERENCE: "api_reference.txt",
}

# System prompt for all documentation generation
SYSTEM_PROMPT = (
    "You are DocSmith, a world-class documentation engineer. "
    "You write clear, accurate, and well-structured documentation. "
    "You never hallucinate features or commands. "
    "You reference actual code, files, and architecture from the repository. "
    "Output only valid Markdown. No commentary or meta-text."
)


def generate_document(
    provider: BaseProvider,
    ctx: RepoContext,
    plan: DocumentationPlan,
    spec: DocumentSpec,
) -> GeneratedDocument:
    """Generate a single document using the AI provider.

    Args:
        provider: The AI provider to use.
        ctx: Repository context.
        plan: Documentation plan.
        spec: Document specification.

    Returns:
        Generated document.
    """
    start_time = time.time()

    # Build prompt
    prompt = _build_prompt(ctx, plan, spec)

    # Generate
    content = generate_with_retry(provider, prompt, SYSTEM_PROMPT)

    # Clean up the response
    content = _clean_response(content)

    elapsed = time.time() - start_time

    return GeneratedDocument(
        doc_type=spec.doc_type,
        filename=spec.filename,
        content=content,
        generation_time_seconds=round(elapsed, 2),
    )


def generate_all_documents(
    provider: BaseProvider,
    ctx: RepoContext,
    plan: DocumentationPlan,
) -> list[GeneratedDocument]:
    """Generate all documents in the plan.

    Args:
        provider: The AI provider to use.
        ctx: Repository context.
        plan: Documentation plan.

    Returns:
        List of generated documents.
    """
    documents = []

    for spec in plan.documents:
        console.print(f"\n[bold cyan] Generating {spec.filename}...[/bold cyan]")
        doc = generate_document(provider, ctx, plan, spec)
        documents.append(doc)
        console.print(
            f"[green]✓ {spec.filename}[/green] "
            f"[dim]({doc.generation_time_seconds:.1f}s, "
            f"{len(doc.content)} chars)[/dim]"
        )

    return documents


def _build_prompt(ctx: RepoContext, plan: DocumentationPlan, spec: DocumentSpec) -> str:
    """Build the full prompt for a document generation."""
    # Try to load template
    template_file = _TEMPLATE_MAP.get(spec.doc_type)
    if template_file:
        template_path = PROMPTS_DIR / template_file
        if template_path.exists():
            template_str = template_path.read_text(encoding="utf-8")
            template = Template(template_str)
            return template.render(
                repo=ctx,
                sections=spec.sections,
                tone=plan.tone.value,
                audience=plan.audience.value,
                use_emojis=plan.use_emojis,
                include_badges=plan.include_badges,
            )

    # Fallback: build a generic prompt
    return _build_generic_prompt(ctx, plan, spec)


def _build_generic_prompt(ctx: RepoContext, plan: DocumentationPlan, spec: DocumentSpec) -> str:
    """Build a generic prompt when no template is available."""
    sections_text = "\n".join(f"- {s.title}: {s.description}" for s in spec.sections)

    return f"""Generate a professional {spec.filename} for the repository "{ctx.name}".

Repository: {ctx.full_name}
Description: {ctx.description}
Language: {ctx.language.value}
Framework: {ctx.framework.value}

Planned sections:
{sections_text}

{spec.special_instructions}

Write in {plan.tone.value} tone for {plan.audience.value} audience.
{"Use emojis for section headers." if plan.use_emojis else ""}
Output valid Markdown only."""


def _clean_response(content: str) -> str:
    """Clean up AI response — remove markdown fences if wrapped."""
    content = content.strip()

    # Remove wrapping ```markdown ... ``` if present
    if content.startswith("```markdown"):
        content = content[len("```markdown") :].strip()
    if content.startswith("```md"):
        content = content[len("```md") :].strip()
    if content.startswith("```"):
        content = content[3:].strip()
    if content.endswith("```"):
        content = content[:-3].strip()

    return content
