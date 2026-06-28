"""Documentation refiner — improves docs based on review feedback."""

from __future__ import annotations

from docsmith.ai.orchestrator import generate_with_retry
from docsmith.ai.providers.base import BaseProvider
from docsmith.generation.writer import clean_response
from docsmith.models.generated_document import GeneratedDocument


def refine_document(
    provider: BaseProvider,
    doc: GeneratedDocument,
) -> GeneratedDocument:
    """Refine a document based on review issues.

    Args:
        provider: AI provider for regeneration.
        doc: Document with review results.

    Returns:
        Refined document.
    """
    if not doc.review or not doc.review.issues:
        return doc

    issues_text = "\n".join(
        f"- [{i.severity}] {i.category}: {i.description}. {i.suggestion}" for i in doc.review.issues
    )

    prompt = f"""The following {doc.filename} has quality issues that need fixing.

## Current Document
{doc.content}

## Issues Found
{issues_text}

## Instructions
Fix all the issues listed above. Keep the overall structure intact.
Output the corrected Markdown only, no commentary."""

    system_prompt = (
        "You are a documentation quality reviewer. Fix the issues in the document "
        "while preserving the overall structure and tone."
    )

    refined_content = generate_with_retry(provider, prompt, system_prompt)
    doc.content = clean_response(refined_content)
    doc.refined = True

    return doc
