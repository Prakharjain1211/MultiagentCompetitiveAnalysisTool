"""
Entry point for the Competitive Analysis Research Tool.

Parses CLI arguments, builds the LangGraph, invokes the research
pipeline, and outputs the final report with rich formatting.

Usage:
    python -m src.main "NVIDIA"
    python -m src.main "NVIDIA" --model gpt-4o-mini --output briefing.md
"""

import argparse
import os
import sys

# Ensure stdout can handle Unicode on Windows (avoids cp1252 errors from Rich).
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8" )

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.syntax import Syntax
from rich import print as rprint

from src.graph.graph_builder import build_research_graph
from src.graph.state import ResearchState
from src.utils.logger import setup_logger
from loguru import logger


console = Console()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments with company, model, and output fields.
    """
    parser = argparse.ArgumentParser(
        description="AI-powered competitive analysis research tool.",
    )
    parser.add_argument(
        "company",
        type=str,
        help="Company or topic to analyze (e.g. 'NVIDIA').",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional file path to save the final Markdown report.",
    )
    return parser.parse_args()


def print_header(company: str) -> None:
    """Print a styled header for the analysis session."""
    console.rule(f"[bold blue]Competitive Analysis: {company}[/]", style="blue")


def print_subtask_table(state: ResearchState) -> None:
    """Print the subtask breakdown in a formatted table."""
    table = Table(title="Research Subtasks", title_style="bold cyan")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Description", style="white")
    table.add_column("Search Query", style="green")
    table.add_column("Status", width=12)

    for st in state["subtasks"]:
        status_style = {
            "pending": "yellow",
            "in_progress": "blue",
            "done": "green",
            "failed": "red",
        }.get(st["status"], "white")
        table.add_row(
            str(st["id"]),
            st["description"],
            st["search_query"],
            f"[{status_style}]{st['status']}[/]",
        )

    console.print(table)
    console.print()


def print_execution_summary(state: ResearchState) -> None:
    """Print a summary of the execution including errors and notes."""
    console.print(Panel(
        f"[bold]Notes collected:[/] {len(state['notes'])}\n"
        f"[bold]Errors encountered:[/] {len(state['errors'])}",
        title="Execution Summary",
        border_style="cyan",
    ))

    if state["errors"]:
        console.print("[bold red]Errors:[/]")
        for err in state["errors"]:
            console.print(f"  - {err}")


def print_report(state: ResearchState) -> None:
    """Print the final Markdown report with syntax highlighting."""
    if not state["final_report"]:
        console.print("[yellow]No report was generated.[/]")
        return

    syntax = Syntax(state["final_report"], "markdown", theme="default", line_numbers=False)
    console.print(Panel(syntax, title="Final Briefing", border_style="green", expand=False))


def run() -> None:
    """Main entry point — parse args, build graph, execute, and display results."""
    args = parse_args()
    setup_logger()

    print_header(args.company)

    # Build the graph.
    with Progress(
        SpinnerColumn("line"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("[cyan]Building research graph...", total=None)
        graph = build_research_graph()

    # Initialise state.
    initial_state: ResearchState = {
        "original_query": args.company,
        "subtasks": [],
        "current_subtask_idx": 0,
        "notes": [],
        "retry_count": 0,
        "max_retries": 3,
        "final_report": "",
        "errors": [],
    }

    # Invoke the graph.
    with Progress(
        SpinnerColumn("line"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task_id = progress.add_task("[cyan]Researching...", total=None)
        try:
            final_state = graph.invoke(
                initial_state,
                config={"configurable": {"thread_id": "research-run-1"}},
            )
        except Exception as e:
            progress.stop()
            logger.error(f"Graph execution failed: {e}")
            console.print(f"\n[bold red]Error:[/] {e}")
            sys.exit(1)
        finally:
            progress.update(task_id, visible=False)

    # Display results.
    if final_state["subtasks"]:
        print_subtask_table(final_state)

    print_execution_summary(final_state)
    console.print()
    print_report(final_state)

    # Optionally save to file.
    if args.output and final_state["final_report"]:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(final_state["final_report"])
        console.print(f"\n[green]Report saved to:[/] {args.output}")


if __name__ == "__main__":
    run()
