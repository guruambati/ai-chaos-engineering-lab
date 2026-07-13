#!/usr/bin/env python3
"""
AI Chaos Engineering — CLI runner.
Runs chaos scenarios, detects recovery, grades resilience.
"""
from __future__ import annotations

import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from src.injectors.faults import FaultConfig, FaultType, inject_fault
from src.detectors.recovery import ChaosReport, ResilienceScore

console = Console()
app = typer.Typer(help="AI Chaos Engineering Framework", add_completion=False)

GRADE_COLOR = {"A": "green", "B": "cyan", "C": "yellow", "D": "orange1", "F": "red"}
FAULT_EMOJI = {
    FaultType.MODEL_CRASH:      "💥",
    FaultType.TIMEOUT:          "⏱️",
    FaultType.TOOL_FAILURE:     "🔧",
    FaultType.CONTEXT_OVERFLOW: "📚",
    FaultType.MALFORMED_PROMPT: "☠️",
    FaultType.VECTOR_DB_DOWN:   "🗄️",
    FaultType.RATE_LIMIT:       "🚦",
    FaultType.NETWORK_FLAP:     "📡",
}

ALL_FAULTS = [
    FaultConfig(FaultType.MODEL_CRASH,      recovery_ms=500),
    FaultConfig(FaultType.TIMEOUT,          timeout_ms=1000, recovery_ms=200),
    FaultConfig(FaultType.TOOL_FAILURE,     recovery_ms=100),
    FaultConfig(FaultType.CONTEXT_OVERFLOW, recovery_ms=50),
    FaultConfig(FaultType.MALFORMED_PROMPT, recovery_ms=20),
    FaultConfig(FaultType.VECTOR_DB_DOWN,   recovery_ms=300),
    FaultConfig(FaultType.RATE_LIMIT,       recovery_ms=200),
    FaultConfig(FaultType.NETWORK_FLAP,     recovery_ms=500),
]


async def run_chaos_scenario(
    scenario_name: str,
    faults: list[FaultConfig],
    repetitions: int = 3,
) -> ChaosReport:
    report = ChaosReport(scenario_name=scenario_name)

    console.print(Panel(
        f"[bold red]⚡ CHAOS SCENARIO: {scenario_name}[/bold red]\n"
        f"Faults: {len(faults)} types × {repetitions} repetitions = "
        f"{len(faults) * repetitions} total injections",
        border_style="red",
    ))

    for fault_cfg in faults:
        emoji = FAULT_EMOJI.get(fault_cfg.fault_type, "🔥")
        console.print(f"\n  {emoji} Injecting [yellow]{fault_cfg.fault_type.value}[/yellow] "
                      f"({repetitions}×)...")

        for rep in range(repetitions):
            event = await inject_fault(fault_cfg)
            if event:
                report.events.append(event)
                icon = "✅" if event.recovered else "❌"
                rt = f"{event.recovery_time_ms:.0f}ms" if event.recovery_time_ms else "—"
                console.print(f"    [{rep+1}/{repetitions}] {icon} "
                              f"{'Recovered' if event.recovered else 'NOT recovered'} "
                              f"in {rt} — {(event.error_message or '')[:70]}")

    report.compute_scores()
    return report


def print_chaos_report(report: ChaosReport):
    t = Table(
        title=f"Chaos Report: {report.scenario_name}",
        box=box.ROUNDED, header_style="bold red",
    )
    for col in ["Fault", "Injected", "Recovered", "Rate", "Mean Recovery", "Grade"]:
        t.add_column(col, justify="right" if col not in ("Fault",) else "left")

    for s in report.scores:
        emoji = FAULT_EMOJI.get(s.fault_type, "🔥")
        gc = GRADE_COLOR.get(s.grade, "white")
        rt = f"{s.mean_recovery_ms:.0f}ms" if s.mean_recovery_ms else "—"
        t.add_row(
            f"{emoji} {s.fault_type.value}",
            str(s.total_injected), str(s.recovered),
            f"{s.recovery_rate_pct:.0f}%", rt,
            f"[{gc}][bold]{s.grade}[/bold][/{gc}]",
        )

    console.print(t)

    gc = GRADE_COLOR.get(report.overall_grade, "white")
    console.print(Panel(
        f"Overall Recovery Rate: [bold]{report.overall_recovery_rate:.1f}%[/bold]  "
        f"Grade: [{gc}][bold]{report.overall_grade}[/bold][/{gc}]  "
        f"Events: {len(report.events)}",
        border_style=gc,
    ))


@app.command()
def run(
    scenario: str = typer.Option("full", "--scenario", "-s",
        help="full | crash | timeout | network | prompts"),
    repetitions: int = typer.Option(3, "--reps", "-r"),
):
    """Run a chaos engineering scenario against an AI system."""
    scenarios = {
        "full":    ALL_FAULTS,
        "crash":   [ALL_FAULTS[0], ALL_FAULTS[1]],
        "timeout": [ALL_FAULTS[1], ALL_FAULTS[7]],
        "network": [ALL_FAULTS[7], ALL_FAULTS[5]],
        "prompts": [ALL_FAULTS[3], ALL_FAULTS[4]],
    }
    faults = scenarios.get(scenario, ALL_FAULTS)

    async def _run():
        report = await run_chaos_scenario(
            scenario_name=f"AI System — {scenario} chaos",
            faults=faults,
            repetitions=repetitions,
        )
        print_chaos_report(report)

    asyncio.run(_run())


if __name__ == "__main__":
    app()
