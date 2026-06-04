"""DocSmith CLI — AI-powered documentation engineer for GitHub repositories."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from docsmith import __version__

app = typer.Typer(
    name="docsmith",
    help=" AI-powered documentation engineer for GitHub repositories.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()

# ── Banner ──────────────────────────────────────────────────────────────────

BANNER = r"""
    ____             _____           _ __  __
   / __ \____  _____/ ___/____ ___  (_) /_/ /_
  / / / / __ \/ ___/\__ \/ __ `__ \/ / __/ __ \
 / /_/ / /_/ / /__ ___/ / / / / / / / /_/ / / /
/_____/\____/\___//____/_/ /_/ /_/_/\__/_/ /_/
"""


def _show_banner() -> None:
    """Display the DocSmith banner."""
    banner_text = Text(BANNER, style="bold cyan")
    console.print(banner_text)
    console.print(f"  [dim]v{__version__} — AI-powered documentation engineer[/dim]\n")


# ── Setup Wizard ────────────────────────────────────────────────────────────


def _run_setup_wizard() -> None:
    """Run the first-time setup wizard."""
    import questionary

    from docsmith.config.settings import AIProvider, DocSmithConfig, ProviderConfig
    from docsmith.config.storage import save_config

    console.print(
        Panel(
            "[bold]Welcome to DocSmith![/bold]\n\n"
            "Let's set up your AI provider.\n"
            "You can change this later with [cyan]docsmith config[/cyan].",
            border_style="cyan",
        )
    )

    # Provider selection
    provider_choice = questionary.select(
        "Select your AI provider:",
        choices=[
            questionary.Choice("Google Gemini (recommended)", value="gemini"),
            questionary.Choice("OpenAI (GPT-4o)", value="openai"),
            questionary.Choice("Anthropic (Claude)", value="anthropic"),
            questionary.Choice("Mistral AI", value="mistral"),
        ],
    ).ask()

    if not provider_choice:
        console.print("[red]Setup cancelled.[/red]")
        raise typer.Exit(1)

    provider = AIProvider(provider_choice)

    # API key
    api_key = questionary.password(f"Enter your {provider.value} API key:").ask()

    if not api_key:
        console.print("[red]API key is required.[/red]")
        raise typer.Exit(1)

    # GitHub token (optional)
    github_token = questionary.text(
        "GitHub token (optional, for higher rate limits):",
        default="",
    ).ask()

    # Save config
    config = DocSmithConfig(
        active_provider=provider,
        providers={
            provider.value: ProviderConfig(api_key=api_key),
        },
        github_token=github_token or "",
    )
    save_config(config)

    console.print("\n[green]✓ Configuration saved![/green]")
    console.print(f"[dim]Provider: {provider.value}[/dim]")
    console.print("[dim]You're ready to go. Run:[/dim]")
    console.print("[bold cyan]  docsmith generate <repo-url>[/bold cyan]\n")


# ── Interactive Questionnaire ───────────────────────────────────────────────


def _ask_generation_options() -> dict:
    """Run the interactive questionnaire for document generation options."""
    import questionary

    from docsmith.models.documentation_plan import Audience, DocumentType, Tone

    # Document types
    doc_choices = questionary.checkbox(
        "Select documents to generate:",
        choices=[
            questionary.Choice("README", value="README", checked=True),
            questionary.Choice("CONTRIBUTING", value="CONTRIBUTING", checked=True),
            questionary.Choice("SECURITY", value="SECURITY"),
            questionary.Choice("ARCHITECTURE", value="ARCHITECTURE", checked=True),
            questionary.Choice("API_REFERENCE", value="API_REFERENCE"),
            questionary.Choice("CHANGELOG", value="CHANGELOG"),
            questionary.Choice("DEVELOPMENT_GUIDE", value="DEVELOPMENT_GUIDE"),
            questionary.Choice("QUICKSTART", value="QUICKSTART"),
        ],
    ).ask()

    if not doc_choices:
        console.print("[red]No documents selected.[/red]")
        raise typer.Exit(1)

    # Audience
    audience = questionary.select(
        "Target audience:",
        choices=[
            questionary.Choice("Beginner", value="beginner"),
            questionary.Choice("Intermediate", value="intermediate"),
            questionary.Choice("Advanced", value="advanced"),
        ],
        default="intermediate",
    ).ask()

    # Tone
    tone = questionary.select(
        "Documentation tone:",
        choices=[
            questionary.Choice("Professional", value="professional"),
            questionary.Choice("Casual", value="casual"),
            questionary.Choice("Fun", value="fun"),
        ],
        default="professional",
    ).ask()

    # Options
    use_emojis = questionary.confirm("Include emojis?", default=True).ask()
    include_badges = questionary.confirm("Include shields.io badges?", default=True).ask()

    return {
        "doc_types": [DocumentType(d) for d in doc_choices],
        "audience": Audience(audience),
        "tone": Tone(tone),
        "use_emojis": use_emojis,
        "include_badges": include_badges,
    }


# ── Commands ────────────────────────────────────────────────────────────────


@app.command()
def generate(
    repo_url: str = typer.Argument(help="GitHub repository URL or owner/repo"),
    output: str = typer.Option("docsmith-output", "--output", "-o", help="Output directory"),
    preview: bool = typer.Option(
        False, "--preview", "-p", help="Preview in terminal instead of saving"
    ),
    skip_review: bool = typer.Option(False, "--skip-review", help="Skip the review pass"),
    quick: bool = typer.Option(
        False, "--quick", "-q", help="Quick mode: skip questionnaire, use defaults"
    ),
) -> None:
    """ Generate documentation for a GitHub repository."""
    from docsmith.ai.orchestrator import get_provider
    from docsmith.analysis.analyzer import analyze_repository
    from docsmith.config.storage import (
        config_exists,
        load_cached_context,
        load_config,
        save_cached_context,
    )
    from docsmith.generation.planner import create_plan
    from docsmith.generation.reviewer import review_document
    from docsmith.generation.scorer import score_document
    from docsmith.generation.writer import generate_all_documents
    from docsmith.github.fetcher import GitHubFetcher, parse_repo_url
    from docsmith.github.repository_context import build_repo_context
    from docsmith.models.documentation_plan import Audience, DocumentType, Tone
    from docsmith.output.filesystem import write_documents
    from docsmith.output.preview import preview_documents
    from docsmith.output.summary import display_summary

    _show_banner()

    # Check config
    if not config_exists():
        console.print("[yellow] No configuration found. Starting setup wizard...[/yellow]\n")
        _run_setup_wizard()

    config = load_config()
    if not config.is_configured:
        console.print("[red]✗ No API key configured.[/red]")
        console.print("[dim]Run: docsmith config[/dim]")
        raise typer.Exit(1)

    # Parse URL
    try:
        owner, repo = parse_repo_url(repo_url)
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold] Analyzing [cyan]{owner}/{repo}[/cyan]...[/bold]\n")

    # Check cache
    cached = load_cached_context(f"{owner}/{repo}")
    if cached and "_cached_at" in cached:
        console.print("[dim]Using cached analysis...[/dim]")
        from docsmith.models.repo_context import RepoContext

        cached.pop("_cached_at", None)
        ctx = RepoContext.model_validate(cached)
    else:
        # Fetch repository
        fetcher = GitHubFetcher(token=config.github_token)
        raw_data = fetcher.fetch_repository(owner, repo)

        if not raw_data.get("metadata"):
            console.print(f"[red]✗ Could not fetch repository: {owner}/{repo}[/red]")
            raise typer.Exit(1)

        # Build context
        ctx = build_repo_context(raw_data)

        # Run analysis
        ctx = analyze_repository(ctx)

        # Cache results
        if config.cache_enabled:
            save_cached_context(f"{owner}/{repo}", ctx.model_dump(mode="json"))

    # Show analysis summary
    console.print("\n[bold green]✓ Analysis complete[/bold green]")
    console.print(f"  Language: [cyan]{ctx.language.value}[/cyan]")
    console.print(f"  Framework: [cyan]{ctx.framework.value}[/cyan]")
    console.print(f"  Dependencies: [cyan]{len(ctx.dependencies)}[/cyan]")
    console.print(f"  Functions: [cyan]{len(ctx.functions)}[/cyan]")
    console.print(f"  Classes: [cyan]{len(ctx.classes)}[/cyan]")
    if ctx.api_endpoints:
        console.print(f"  API Endpoints: [cyan]{len(ctx.api_endpoints)}[/cyan]")
    if ctx.cli_commands:
        console.print(f"  CLI Commands: [cyan]{len(ctx.cli_commands)}[/cyan]")

    # Get generation options
    if quick:
        options = {
            "doc_types": [
                DocumentType.README,
                DocumentType.CONTRIBUTING,
                DocumentType.ARCHITECTURE,
            ],
            "audience": Audience.INTERMEDIATE,
            "tone": Tone.PROFESSIONAL,
            "use_emojis": True,
            "include_badges": True,
        }
    else:
        console.print()
        options = _ask_generation_options()

    # Create plan
    console.print("\n[bold] Creating documentation plan...[/bold]")
    plan = create_plan(ctx, **options)
    console.print(f"[green]✓ Plan created:[/green] {len(plan.documents)} documents")

    # Generate
    console.print("\n[bold]  Generating documentation...[/bold]")
    provider = get_provider(config)
    documents = generate_all_documents(provider, ctx, plan)

    # Review & Score
    if not skip_review:
        console.print("\n[bold] Reviewing documentation...[/bold]")
        for doc in documents:
            doc.review = review_document(doc, ctx)
            doc.score = score_document(doc, ctx)

            status = (
                "[green]✓ passed[/green]"
                if doc.review.passed
                else "[yellow] issues found[/yellow]"
            )
            console.print(f"  {doc.filename}: {status} (score: {doc.overall_score})")

    # Output
    if preview:
        preview_documents(documents)
    else:
        written = write_documents(documents, output)
        console.print(f"\n[green]✓ Written {len(written)} files to {output}/[/green]")

    # Summary
    display_summary(documents, output_dir="" if preview else output)


@app.command()
def analyze(
    repo_url: str = typer.Argument(help="GitHub repository URL or owner/repo"),
) -> None:
    """ Analyze a repository without generating docs."""
    from docsmith.analysis.analyzer import analyze_repository
    from docsmith.config.storage import load_config
    from docsmith.github.fetcher import GitHubFetcher, parse_repo_url
    from docsmith.github.repository_context import build_repo_context

    _show_banner()

    config = load_config()

    try:
        owner, repo = parse_repo_url(repo_url)
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold] Analyzing [cyan]{owner}/{repo}[/cyan]...[/bold]\n")

    fetcher = GitHubFetcher(token=config.github_token)
    raw_data = fetcher.fetch_repository(owner, repo)

    if not raw_data.get("metadata"):
        console.print("[red]✗ Could not fetch repository[/red]")
        raise typer.Exit(1)

    ctx = build_repo_context(raw_data)
    ctx = analyze_repository(ctx)

    # Display full analysis
    from rich.table import Table

    console.print(f"\n[bold green]✓ Analysis complete for {ctx.full_name}[/bold green]\n")

    table = Table(title="Repository Intelligence", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="white", min_width=20)
    table.add_column("Value", style="cyan")

    table.add_row("Name", ctx.full_name)
    table.add_row("Description", ctx.description or "—")
    table.add_row("Language", ctx.language.value)
    table.add_row("Framework", ctx.framework.value)
    table.add_row("Package Manager", ctx.package_manager.value)
    table.add_row("Dependencies", str(len(ctx.dependencies)))
    table.add_row("Functions", str(len(ctx.functions)))
    table.add_row("Classes", str(len(ctx.classes)))
    table.add_row("API Endpoints", str(len(ctx.api_endpoints)))
    table.add_row("CLI Commands", str(len(ctx.cli_commands)))
    table.add_row("Env Variables", str(len(ctx.env_variables)))
    table.add_row("Has Tests", "✓" if ctx.has_tests else "✗")
    table.add_row("Has CI", "✓" if ctx.has_ci else "✗")
    table.add_row("Has Docker", "✓" if ctx.has_docker else "✗")

    console.print(table)


@app.command()
def config() -> None:
    """  Configure DocSmith settings."""
    from docsmith.config.storage import config_exists

    _show_banner()

    if not config_exists():
        _run_setup_wizard()
    else:
        _run_setup_wizard()  # Re-run wizard for reconfiguration


@app.command()
def cache(
    action: str = typer.Argument(help="Action: clear"),
) -> None:
    """  Manage the analysis cache."""
    if action == "clear":
        from docsmith.config.storage import clear_cache

        count = clear_cache()
        console.print(f"[green]✓ Cleared {count} cached entries[/green]")
    else:
        console.print(f"[red]Unknown cache action: {action}[/red]")
        console.print("[dim]Available: clear[/dim]")


@app.command()
def version() -> None:
    """ Show DocSmith version."""
    console.print(f"DocSmith v{__version__}")


# ── Default command (run generate when URL is passed directly) ──────────────


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
) -> None:
    """ DocSmith — AI-powered documentation engineer."""
    if ctx.invoked_subcommand is None:
        _show_banner()
        console.print("Run [bold cyan]docsmith --help[/bold cyan] for usage.\n")


if __name__ == "__main__":
    app()
