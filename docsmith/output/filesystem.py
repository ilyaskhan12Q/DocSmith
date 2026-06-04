"""Filesystem output — write generated docs to disk."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from docsmith.models.generated_document import GeneratedDocument

console = Console()


def write_documents(
    documents: list[GeneratedDocument],
    output_dir: str = "docsmith-output",
) -> list[Path]:
    """Write generated documents to the output directory.

    Args:
        documents: List of generated documents.
        output_dir: Target directory.

    Returns:
        List of written file paths.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []

    for doc in documents:
        filepath = out_path / doc.filename
        filepath.write_text(doc.content, encoding="utf-8")
        written.append(filepath)

    return written
