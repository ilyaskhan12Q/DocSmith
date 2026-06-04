"""Documentation scorer — evaluates quality of generated documentation."""

from __future__ import annotations

import re

from docsmith.models.generated_document import GeneratedDocument, QualityScore
from docsmith.models.repo_context import RepoContext


def score_document(doc: GeneratedDocument, ctx: RepoContext) -> QualityScore:
    """Score a generated document on multiple quality dimensions.

    Scores are 0–100 for each dimension:
    - completeness: Does it cover all planned sections?
    - correctness: Does it reference real repo content?
    - examples: Quality and quantity of code examples
    - usability: Is it well-structured and readable?
    - maintainability: Is it easy to keep updated?

    Args:
        doc: The generated document.
        ctx: Repository context for validation.

    Returns:
        QualityScore with dimensional scores.
    """
    content = doc.content

    return QualityScore(
        completeness=_score_completeness(content, doc),
        correctness=_score_correctness(content, ctx),
        examples=_score_examples(content),
        usability=_score_usability(content),
        maintainability=_score_maintainability(content),
    )


def _score_completeness(content: str, doc: GeneratedDocument) -> int:
    """Score based on section coverage and content length."""
    score = 50  # Base score

    # Length bonus
    length = len(content)
    if length > 500:
        score += 10
    if length > 1500:
        score += 10
    if length > 3000:
        score += 10

    # Header count
    headers = re.findall(r"^#{1,3}\s+.+", content, re.MULTILINE)
    if len(headers) >= 3:
        score += 5
    if len(headers) >= 5:
        score += 5
    if len(headers) >= 8:
        score += 5

    # Has introduction/overview
    if any(h in content.lower() for h in ["overview", "introduction", "about", "what is"]):
        score += 5

    return min(score, 100)


def _score_correctness(content: str, ctx: RepoContext) -> int:
    """Score based on references to real repository content."""
    score = 60  # Base score

    content_lower = content.lower()

    # References actual repo name
    if ctx.name.lower() in content_lower:
        score += 10

    # References actual language/framework
    if ctx.language.value in content_lower:
        score += 5
    if ctx.framework.value != "none" and ctx.framework.value in content_lower:
        score += 5

    # References actual dependencies
    dep_refs = sum(1 for d in ctx.dependencies[:10] if d.name.lower() in content_lower)
    score += min(dep_refs * 3, 15)

    # References actual files/paths
    file_refs = sum(1 for f in ctx.files if f.path in content)
    score += min(file_refs * 2, 10)

    return max(min(score, 100), 0)


def _score_examples(content: str) -> int:
    """Score based on code examples quality."""
    score = 40  # Base

    # Count code blocks
    code_blocks = re.findall(r"```\w*\n[\s\S]*?\n```", content)
    if len(code_blocks) >= 1:
        score += 15
    if len(code_blocks) >= 3:
        score += 15
    if len(code_blocks) >= 5:
        score += 10

    # Inline code references
    inline_code = re.findall(r"`[^`]+`", content)
    if len(inline_code) >= 5:
        score += 10
    if len(inline_code) >= 15:
        score += 10

    return min(score, 100)


def _score_usability(content: str) -> int:
    """Score based on structure and readability."""
    score = 50

    # Has table of contents or clear structure
    headers = re.findall(r"^#{1,3}\s+.+", content, re.MULTILINE)
    if len(headers) >= 4:
        score += 15

    # Uses lists
    lists = re.findall(r"^\s*[-*]\s+", content, re.MULTILINE)
    if len(lists) >= 3:
        score += 10

    # Has links
    links = re.findall(r"\[.+?\]\(.+?\)", content)
    if len(links) >= 2:
        score += 10

    # Has bold/emphasis
    if "**" in content or "__" in content:
        score += 5

    # Has tables
    if "|" in content and "---" in content:
        score += 10

    return min(score, 100)


def _score_maintainability(content: str) -> int:
    """Score based on how easy the doc is to maintain."""
    score = 70

    # Penalize hardcoded versions (they go stale)
    version_refs = re.findall(r"\d+\.\d+\.\d+", content)
    if len(version_refs) > 5:
        score -= 10

    # Penalize very long documents (harder to maintain)
    if len(content) > 10000:
        score -= 10

    # Bonus for modular structure (links to other docs)
    if re.search(r"\[.+?\]\(\./\w+", content):
        score += 10

    # Bonus for using relative paths
    if "./" in content:
        score += 5

    return max(min(score, 100), 0)
