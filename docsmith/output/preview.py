"""Preview mode — print generated docs to terminal."""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from docsmith.models.generated_document import GeneratedDocument

console = Console()


def preview_documents(documents: list[GeneratedDocument]) -> None:
    """Preview generated documents in the terminal.

    Args:
        documents: List of generated documents to preview.
    """
    for doc in documents:
        console.print()
        console.print(
            Panel(
                Markdown(doc.content),
                title=f"📄 {doc.filename}",
                subtitle=f"Score: {doc.overall_score}/100" if doc.score else None,
                border_style="cyan",
                padding=(1, 2),
            )
        )
        console.print()
