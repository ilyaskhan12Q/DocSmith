"""Documentation scorer — evaluates quality of generated documentation."""

from __future__ import annotations

import re

from docsmith.models.generated_document import GeneratedDocument, QualityScore
from docsmith.models.repo_context import RepoContext

COMPLETENESS_BASE_SCORE = 50
COMPLETENESS_LENGTH_BONUS_SHORT = 10
COMPLETENESS_LENGTH_THRESHOLD_SHORT = 500
COMPLETENESS_LENGTH_BONUS_MEDIUM = 10
COMPLETENESS_LENGTH_THRESHOLD_MEDIUM = 1500
COMPLETENESS_LENGTH_BONUS_LONG = 10
COMPLETENESS_LENGTH_THRESHOLD_LONG = 3000
COMPLETENESS_HEADERS_MIN_3 = 5
COMPLETENESS_HEADERS_MIN_5 = 5
COMPLETENESS_HEADERS_MIN_8 = 5
COMPLETENESS_OVERVIEW_BONUS = 5

CORRECTNESS_BASE_SCORE = 60
CORRECTNESS_NAME_BONUS = 10
CORRECTNESS_LANGUAGE_BONUS = 5
CORRECTNESS_FRAMEWORK_BONUS = 5
CORRECTNESS_DEP_BONUS_PER_REF = 3
CORRECTNESS_DEP_MAX_BONUS = 15
CORRECTNESS_DEP_SAMPLE_SIZE = 10
CORRECTNESS_FILE_BONUS_PER_REF = 2
CORRECTNESS_FILE_MAX_BONUS = 10

EXAMPLES_BASE_SCORE = 40
EXAMPLES_ONE_BLOCK_BONUS = 15
EXAMPLES_THREE_BLOCKS_BONUS = 15
EXAMPLES_FIVE_BLOCKS_BONUS = 10
EXAMPLES_INLINE_MIN_5_BONUS = 10
EXAMPLES_INLINE_MIN_15_BONUS = 10

USABILITY_BASE_SCORE = 50
USABILITY_HEADERS_BONUS = 15
USABILITY_HEADERS_MIN = 4
USABILITY_LISTS_BONUS = 10
USABILITY_LISTS_MIN = 3
USABILITY_LINKS_BONUS = 10
USABILITY_LINKS_MIN = 2
USABILITY_EMPHASIS_BONUS = 5
USABILITY_TABLES_BONUS = 10

MAINTAINABILITY_BASE_SCORE = 70
MAINTAINABILITY_VERSION_REFS_LIMIT = 5
MAINTAINABILITY_VERSION_PENALTY = 10
MAINTAINABILITY_LENGTH_LIMIT = 10_000
MAINTAINABILITY_LENGTH_PENALTY = 10
MAINTAINABILITY_RELATIVE_LINKS_BONUS = 10
MAINTAINABILITY_RELATIVE_PATH_BONUS = 5


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
    score = COMPLETENESS_BASE_SCORE

    length = len(content)
    if length > COMPLETENESS_LENGTH_THRESHOLD_SHORT:
        score += COMPLETENESS_LENGTH_BONUS_SHORT
    if length > COMPLETENESS_LENGTH_THRESHOLD_MEDIUM:
        score += COMPLETENESS_LENGTH_BONUS_MEDIUM
    if length > COMPLETENESS_LENGTH_THRESHOLD_LONG:
        score += COMPLETENESS_LENGTH_BONUS_LONG

    headers = re.findall(r"^#{1,3}\s+.+", content, re.MULTILINE)
    if len(headers) >= 3:
        score += COMPLETENESS_HEADERS_MIN_3
    if len(headers) >= 5:
        score += COMPLETENESS_HEADERS_MIN_5
    if len(headers) >= 8:
        score += COMPLETENESS_HEADERS_MIN_8

    if any(h in content.lower() for h in ["overview", "introduction", "about", "what is"]):
        score += COMPLETENESS_OVERVIEW_BONUS

    return min(score, 100)


def _score_correctness(content: str, ctx: RepoContext) -> int:
    """Score based on references to real repository content."""
    score = CORRECTNESS_BASE_SCORE

    content_lower = content.lower()

    if ctx.name.lower() in content_lower:
        score += CORRECTNESS_NAME_BONUS

    if ctx.language.value in content_lower:
        score += CORRECTNESS_LANGUAGE_BONUS
    if ctx.framework.value != "none" and ctx.framework.value in content_lower:
        score += CORRECTNESS_FRAMEWORK_BONUS

    dep_refs = sum(
        1 for d in ctx.dependencies[:CORRECTNESS_DEP_SAMPLE_SIZE] if d.name.lower() in content_lower
    )
    score += min(dep_refs * CORRECTNESS_DEP_BONUS_PER_REF, CORRECTNESS_DEP_MAX_BONUS)

    file_refs = sum(1 for f in ctx.files if f.path in content)
    score += min(file_refs * CORRECTNESS_FILE_BONUS_PER_REF, CORRECTNESS_FILE_MAX_BONUS)

    return max(min(score, 100), 0)


def _score_examples(content: str) -> int:
    """Score based on code examples quality."""
    score = EXAMPLES_BASE_SCORE

    code_blocks = re.findall(r"```\w*\n[\s\S]*?\n```", content)
    if len(code_blocks) >= 1:
        score += EXAMPLES_ONE_BLOCK_BONUS
    if len(code_blocks) >= 3:
        score += EXAMPLES_THREE_BLOCKS_BONUS
    if len(code_blocks) >= 5:
        score += EXAMPLES_FIVE_BLOCKS_BONUS

    inline_code = re.findall(r"`[^`]+`", content)
    if len(inline_code) >= 5:
        score += EXAMPLES_INLINE_MIN_5_BONUS
    if len(inline_code) >= 15:
        score += EXAMPLES_INLINE_MIN_15_BONUS

    return min(score, 100)


def _score_usability(content: str) -> int:
    """Score based on structure and readability."""
    score = USABILITY_BASE_SCORE

    headers = re.findall(r"^#{1,3}\s+.+", content, re.MULTILINE)
    if len(headers) >= USABILITY_HEADERS_MIN:
        score += USABILITY_HEADERS_BONUS

    lists = re.findall(r"^\s*[-*]\s+", content, re.MULTILINE)
    if len(lists) >= USABILITY_LISTS_MIN:
        score += USABILITY_LISTS_BONUS

    links = re.findall(r"\[.+?\]\(.+?\)", content)
    if len(links) >= USABILITY_LINKS_MIN:
        score += USABILITY_LINKS_BONUS

    if "**" in content or "__" in content:
        score += USABILITY_EMPHASIS_BONUS

    if "|" in content and "---" in content:
        score += USABILITY_TABLES_BONUS

    return min(score, 100)


def _score_maintainability(content: str) -> int:
    """Score based on how easy the doc is to maintain."""
    score = MAINTAINABILITY_BASE_SCORE

    version_refs = re.findall(r"\d+\.\d+\.\d+", content)
    if len(version_refs) > MAINTAINABILITY_VERSION_REFS_LIMIT:
        score -= MAINTAINABILITY_VERSION_PENALTY

    if len(content) > MAINTAINABILITY_LENGTH_LIMIT:
        score -= MAINTAINABILITY_LENGTH_PENALTY

    if re.search(r"\[.+?\]\(\./\w+", content):
        score += MAINTAINABILITY_RELATIVE_LINKS_BONUS

    if "./" in content:
        score += MAINTAINABILITY_RELATIVE_PATH_BONUS

    return max(min(score, 100), 0)
