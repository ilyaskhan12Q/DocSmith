"""Summary display — show generation results and quality scores."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from docsmith.models.generated_document import GeneratedDocument

console = Console()


def display_summary(documents: list[GeneratedDocument], output_dir: str = "") -> None:
    """Display a summary table of all generated documents.

    Args:
        documents: List of generated documents.
        output_dir: Output directory path (for display).
    """
    console.print()
    console.print("[bold] Documentation Report[/bold]")
    console.print()

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Document", style="white", min_width=20)
    table.add_column("Score", justify="center", min_width=8)
    table.add_column("Issues", justify="center", min_width=8)
    table.add_column("Time", justify="right", min_width=8)
    table.add_column("Status", justify="center", min_width=10)

    total_score = 0
    scored_count = 0

    for doc in documents:
        score = doc.overall_score
        score_str = f"{score}/100" if doc.score else "—"

        # Color the score
        if score >= 90:
            score_display = f"[bold green]{score_str}[/bold green]"
        elif score >= 70:
            score_display = f"[yellow]{score_str}[/yellow]"
        elif score > 0:
            score_display = f"[red]{score_str}[/red]"
        else:
            score_display = score_str

        # Issues
        if doc.review:
            issues_str = f"{doc.review.critical_count}C / {doc.review.warning_count}W"
        else:
            issues_str = "—"

        # Time
        time_str = f"{doc.generation_time_seconds:.1f}s"

        # Status
        if doc.refined:
            status = "[cyan]Refined[/cyan]"
        elif doc.review and doc.review.passed:
            status = "[green]✓ Passed[/green]"
        elif doc.review:
            status = "[yellow] Issues[/yellow]"
        else:
            status = "[dim]Generated[/dim]"

        table.add_row(doc.filename, score_display, issues_str, time_str, status)

        if doc.score:
            total_score += score
            scored_count += 1

    # Overall score
    if scored_count > 0:
        overall = total_score // scored_count
        if overall >= 90:
            overall_style = "bold green"
        elif overall >= 70:
            overall_style = "yellow"
        else:
            overall_style = "red"

        table.add_section()
        table.add_row(
            "[bold]Overall[/bold]",
            f"[{overall_style}]{overall}/100[/{overall_style}]",
            "",
            "",
            "",
        )

    console.print(table)

    if output_dir:
        console.print(f"\n[dim] Output: {output_dir}/[/dim]")

    console.print()
