"""
cli.py — NetWatcher command-line interface.

Architecture reasoning:
  Typer gives us:  typed arguments, auto-help generation, sub-commands
  Rich gives us:   tables, colors, panels, progress bars, spinners

  This is the "face" of the product. Every recruiter who clones this will
  run it first — it needs to look elite immediately.

  Commands:
    scan     — run a network scan (local or custom target)
    report   — open the last HTML report
    history  — show scan history from SQLite
    check    — preflight: verify nmap installed
"""

import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Add project root to path so relative imports work from CLI entry point
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.text import Text

app     = typer.Typer(help="🛡 NetWatcher — Home Network Vulnerability Scanner", add_completion=False)
console = Console()


# ─── Banner ───────────────────────────────────────────────────────────────────

def _banner() -> None:
    console.print(Panel.fit(
        "[bold white]🛡  NetWatcher[/bold white]  [dim]v1.0.0[/dim]\n"
        "[dim]Home Network Vulnerability Scanner[/dim]\n"
        "[dim]────────────────────────────────────[/dim]\n"
        "[dim]Developer : [/dim][link=https://github.com/Akshay-core]Akshay[/link]  "
        "[dim]· Portfolio : [/dim][link=https://akshay.fruvvi.com]akshay.fruvvi.com[/link]",
        border_style="bright_blue",
        padding=(0, 2),
    ))


# ─── scan ─────────────────────────────────────────────────────────────────────

@app.command()
def scan(
    target:  Optional[str] = typer.Option(None,  "--target", "-t", help="Target IP or CIDR, e.g. 192.168.1.0/24"),
    local:   bool          = typer.Option(False, "--local",  "-l", help="Auto-detect and scan local subnet"),
    report:  bool          = typer.Option(True,              help="Generate HTML report after scan"),
    verbose: bool          = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    open_report: bool      = typer.Option(False, "--open",   help="Open HTML report in browser after generation"),
) -> None:
    """Scan a network target for open ports and vulnerabilities."""
    _banner()

    # ── Verbose logging ────────────────────────────────────────────────────
    if verbose:
        from utils.logger import set_global_level
        set_global_level(logging.DEBUG)

    # ── Preflight: nmap check ──────────────────────────────────────────────
    from utils.helpers import check_nmap_installed, get_local_subnet
    if not check_nmap_installed():
        console.print("[bold red]✗ Nmap is not installed.[/bold red]")
        console.print("  Linux/Mac: [yellow]sudo apt install nmap[/yellow]  OR  [yellow]brew install nmap[/yellow]")
        console.print("  Windows  : https://nmap.org/download.html")
        raise typer.Exit(1)

    # ── Resolve target ─────────────────────────────────────────────────────
    if local:
        target = get_local_subnet()
        console.print(f"[dim]Auto-detected local subnet:[/dim] [cyan]{target}[/cyan]")
    elif not target:
        console.print("[red]Provide --target or use --local[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold]Target:[/bold] [cyan]{target}[/cyan]")
    console.print("[dim]Running Nmap scan … this may take 1–3 minutes[/dim]\n")

    # ── Scan ───────────────────────────────────────────────────────────────
    from netwatcher.scanner import scan_network
    from engine.fingerprint import fingerprint_devices
    from engine.risk_engine import score_devices, network_summary
    from data.db import save_scan
    from reports.generator import generate_html_report
    from ai.analyzer import run_ai_analysis
    from utils.helpers import open_file_in_browser

    devices = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        t1 = progress.add_task("[cyan]Discovering hosts…", total=None)
        try:
            devices = scan_network(target)
        except RuntimeError as e:
            console.print(f"[red]Scan error: {e}[/red]")
            raise typer.Exit(1)
        progress.update(t1, description=f"[green]Found {len(devices)} hosts[/green]")

        progress.add_task("[cyan]Fingerprinting devices…", total=None)
        devices = fingerprint_devices(devices)

        progress.add_task("[cyan]Running risk analysis…", total=None)
        devices = score_devices(devices)

    if not devices:
        console.print("\n[yellow]⚠ No live hosts found. Check the target range or run with sudo.[/yellow]")
        raise typer.Exit(0)

    # ── Print results table ────────────────────────────────────────────────
    _print_results_table(devices)

    # ── Network summary ────────────────────────────────────────────────────
    summary = network_summary(devices)
    _print_summary(summary)

    # ── AI analysis ────────────────────────────────────────────────────────
    ai_result = None
    if report:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                      transient=True, console=console) as prog:
            t_ai = prog.add_task("[cyan]Running AI analysis…", total=None)
            ai_result = run_ai_analysis(devices, summary, target)
            model_str = ai_result["model_used"] or "rule-based"
            prog.update(t_ai, description=f"[green]AI analysis done ({model_str})[/green]")

    # ── Save to DB ─────────────────────────────────────────────────────────
    scan_id = save_scan(target, devices, summary)

    # ── Generate report ────────────────────────────────────────────────────
    if report:
        report_path = generate_html_report(devices, summary, target, scan_id, ai_result)
        console.print(f"\n[green]✓ Report saved:[/green] [dim]{report_path}[/dim]")
        if open_report:
            open_file_in_browser(report_path)
            console.print("[dim]Opening in browser…[/dim]")

    console.print(f"\n[dim]Scan ID #{scan_id} saved to history.[/dim]")


# ─── report ───────────────────────────────────────────────────────────────────

@app.command()
def report(
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open in browser"),
) -> None:
    """Open the most recent HTML report."""
    from netwatcher.config import REPORTS_DIR
    from utils.helpers import open_file_in_browser

    reports = sorted(REPORTS_DIR.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not reports:
        console.print("[yellow]No reports found. Run [bold]scan[/bold] first.[/yellow]")
        raise typer.Exit(1)

    latest = reports[0]
    console.print(f"[green]Latest report:[/green] {latest}")
    if open_browser:
        open_file_in_browser(latest)


# ─── history ──────────────────────────────────────────────────────────────────

@app.command()
def history(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of recent scans to show"),
) -> None:
    """Show scan history from the local database."""
    from data.db import get_scan_history

    scans = get_scan_history(limit)
    if not scans:
        console.print("[yellow]No scan history found.[/yellow]")
        raise typer.Exit(0)

    table = Table(
        title="Scan History",
        border_style="bright_blue",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("ID",      style="dim", width=5)
    table.add_column("Target",  style="cyan")
    table.add_column("Date",    style="white")
    table.add_column("Hosts",   justify="right")
    table.add_column("Avg Risk", justify="right")

    for s in scans:
        score = s["avg_score"]
        color = "red" if score >= 75 else "yellow" if score >= 50 else "blue" if score >= 25 else "green"
        table.add_row(
            str(s["id"]),
            s["target"],
            s["started_at"],
            str(s["host_count"]),
            f"[{color}]{score}/100[/{color}]",
        )

    console.print(table)


# ─── check ────────────────────────────────────────────────────────────────────

@app.command()
def check() -> None:
    """Verify environment: nmap, Python version, dependencies."""
    from utils.helpers import check_nmap_installed

    console.print("\n[bold]NetWatcher Preflight Check[/bold]\n")

    nmap_ok = check_nmap_installed()
    py_ok   = sys.version_info >= (3, 8)

    _row("Python 3.8+",    py_ok,   f"Python {sys.version.split()[0]}")
    _row("Nmap installed", nmap_ok, "nmap binary found" if nmap_ok else "NOT FOUND — install nmap")

    # Check Python packages
    for pkg in ["nmap", "typer", "rich", "jinja2"]:
        try:
            __import__(pkg)
            _row(f"  pip: {pkg}", True, "installed")
        except ImportError:
            _row(f"  pip: {pkg}", False, "missing — run: pip install -r requirements.txt")

    console.print()


# ─── Private helpers ──────────────────────────────────────────────────────────

def _row(label: str, ok: bool, detail: str) -> None:
    icon = "[green]✓[/green]" if ok else "[red]✗[/red]"
    console.print(f"  {icon}  {label:<22} [dim]{detail}[/dim]")


def _print_results_table(devices) -> None:
    table = Table(
        title=f"Scan Results — {len(devices)} hosts",
        border_style="bright_blue",
        header_style="bold cyan",
        show_lines=False,
    )
    table.add_column("IP",          style="cyan",  min_width=15)
    table.add_column("Hostname",    style="white", min_width=14)
    table.add_column("Type",        style="dim",   min_width=10)
    table.add_column("Ports",       justify="right", width=6)
    table.add_column("Risk Score",  justify="right", min_width=12)
    table.add_column("Level",       min_width=10)

    for d in devices:
        level = d.risk_level
        score = d.risk_score
        color_map = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "bright_blue", "LOW": "green"}
        c = color_map.get(level, "white")
        table.add_row(
            d.ip,
            d.hostname[:16],
            d.device_type,
            str(len(d.ports)),
            f"[{c}]{score}/100[/{c}]",
            f"[bold {c}]{level}[/bold {c}]",
        )

    console.print()
    console.print(table)


def _print_summary(summary: dict) -> None:
    level = summary["level"]
    score = summary["overall_score"]
    color_map = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "bright_blue", "LOW": "green"}
    c = color_map.get(level, "white")

    console.print(Panel(
        f"[bold white]NETWORK SECURITY SCORE:[/bold white] [bold {c}]{score}/100  {level} RISK[/bold {c}]\n"
        f"Devices: {summary['total_devices']}  "
        f"[red]Critical: {summary['critical']}[/red]  "
        f"[yellow]High: {summary['high']}[/yellow]  "
        f"[bright_blue]Medium: {summary['medium']}[/bright_blue]  "
        f"[green]Low: {summary['low']}[/green]",
        border_style=c,
        padding=(0, 2),
    ))


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
