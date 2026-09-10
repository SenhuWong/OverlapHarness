#!/usr/bin/env python3
"""Validate the 100-step NACA0012 pitching smoke run."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


BAD_STATE = re.compile(
    r"has\s+nan|nan\s+detected|detected\s+nan|non[- ]finite|bad[-_ ]state|"
    r"\b(?:rho|pressure|energy|state)\s*[=:]\s*(?:nan|[-+]?inf(?:inity)?)\b",
    re.IGNORECASE,
)
STEP = re.compile(
    r"^STEP\s*=\s*(\d+)\s+TIME\s*=\s*([-+0-9.eE]+)\s+DT\s*=\s*([-+0-9.eE]+)",
    re.MULTILINE,
)


def read_force_history(path: Path) -> list[list[float]]:
    rows: list[list[float]] = []
    for line_number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        text = line.strip().strip("\x00")
        if not text:
            continue
        fields = text.split()
        if len(fields) < 3:
            raise ValueError(f"{path}:{line_number}: expected at least 3 columns")
        try:
            rows.append([float(value) for value in fields])
        except ValueError as error:
            raise ValueError(f"{path}:{line_number}: non-numeric force row") from error
    return rows


def criterion(identifier: str, passed: bool, value, unit, operator: str, threshold, evidence):
    return {
        "id": identifier,
        "required": True,
        "status": "PASS" if passed else "FAIL",
        "value": value,
        "unit": unit,
        "operator": operator,
        "threshold": threshold,
        "evidence": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--expected-steps", type=int, default=100)
    parser.add_argument("--expected-final-time", type=float, default=0.1)
    parser.add_argument("--expected-dt", type=float, default=0.001)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    force_candidates = [
        run_dir / "raw/unstruct/ClCdDualParallelv_0",
        run_dir / "unstruct_output/ClCdDualParallelv_0",
        run_dir / "ClCdDualParallelv_0",
    ]
    force_path = next((path for path in force_candidates if path.is_file()), force_candidates[0])
    exit_path = run_dir / "logs/run.exitcode"
    stdout_path = run_dir / "logs/stdout.log"
    stderr_path = run_dir / "logs/stderr.log"

    try:
        exit_code = int(exit_path.read_text().strip())
    except (OSError, ValueError):
        exit_code = None

    stdout_text = stdout_path.read_text(errors="replace") if stdout_path.is_file() else ""
    step_matches = STEP.findall(stdout_text)
    if step_matches:
        final_step = int(step_matches[-1][0])
        solver_final_time = float(step_matches[-1][1])
        solver_final_dt = float(step_matches[-1][2])
    else:
        final_step = None
        solver_final_time = None
        solver_final_dt = None

    force_error = None
    try:
        rows = read_force_history(force_path)
    except (OSError, ValueError) as error:
        rows = []
        force_error = str(error)

    # The coupled driver writes force coefficients at the beginning of each
    # physical step.  A 100-step run therefore records t=0 through t=0.099,
    # while the solver completion line reports STEP=100 and TIME=0.1.
    expected_samples = args.expected_steps
    expected_force_final_time = (args.expected_steps - 1) * args.expected_dt
    finite = bool(rows) and all(math.isfinite(value) for row in rows for value in row)
    times = [row[0] for row in rows]
    monotonic = bool(times) and all(b > a for a, b in zip(times, times[1:]))
    time_range_ok = (
        monotonic
        and math.isclose(times[0], 0.0, rel_tol=0.0, abs_tol=1.0e-10)
        and math.isclose(times[-1], expected_force_final_time, rel_tol=0.0, abs_tol=1.0e-10)
    )

    log_matches: list[dict[str, object]] = []
    for log_path in (stdout_path, stderr_path):
        if not log_path.is_file():
            continue
        for line_number, line in enumerate(log_path.read_text(errors="replace").splitlines(), 1):
            if BAD_STATE.search(line):
                log_matches.append(
                    {"path": str(log_path.relative_to(run_dir)), "line": line_number, "text": line[:500]}
                )

    metrics: list[dict[str, object]] = [
        {"id": "process-exit-code", "value": exit_code, "unit": None},
        {"id": "solver-final-step", "value": final_step, "unit": "steps"},
        {"id": "solver-final-time", "value": solver_final_time, "unit": "nondimensional time"},
        {"id": "solver-final-dt", "value": solver_final_dt, "unit": "nondimensional time"},
        {"id": "force-history-samples", "value": len(rows), "unit": "rows"},
        {"id": "accepted-physical-steps", "value": final_step, "unit": "steps"},
        {"id": "force-history-initial-time", "value": times[0] if times else None, "unit": "nondimensional time"},
        {"id": "force-history-final-time", "value": times[-1] if times else None, "unit": "nondimensional time"},
        {"id": "bad-state-log-matches", "value": len(log_matches), "unit": "lines"},
    ]
    if rows and finite:
        metrics.extend(
            [
                {"id": "cl-min", "value": min(row[1] for row in rows), "unit": None},
                {"id": "cl-max", "value": max(row[1] for row in rows), "unit": None},
                {"id": "cd-min", "value": min(row[2] for row in rows), "unit": None},
                {"id": "cd-max", "value": max(row[2] for row in rows), "unit": None},
            ]
        )

    reference_path = run_dir / "inputs/reference/historical-clcd-first-100.tsv"
    if rows and finite and reference_path.is_file():
        reference = read_force_history(reference_path)
        count = min(len(rows), len(reference))
        if count:
            metrics.extend(
                [
                    {
                        "id": "advisory-historical-cl-max-abs-delta",
                        "value": max(abs(rows[i][1] - reference[i][1]) for i in range(count)),
                        "unit": None,
                    },
                    {
                        "id": "advisory-historical-cd-max-abs-delta",
                        "value": max(abs(rows[i][2] - reference[i][2]) for i in range(count)),
                        "unit": None,
                    },
                ]
            )

    criteria = [
        criterion("execution-exit-zero", exit_code == 0, exit_code, None, "==", 0, ["logs/run.exitcode"]),
        criterion(
            "accepted-physical-steps",
            final_step == args.expected_steps,
            final_step,
            "steps",
            "==",
            args.expected_steps,
            ["logs/stdout.log"],
        ),
        criterion(
            "solver-final-time",
            solver_final_time is not None
            and math.isclose(solver_final_time, args.expected_final_time, rel_tol=0.0, abs_tol=1.0e-10),
            solver_final_time,
            "nondimensional time",
            "== within abs_tol",
            {"expected": args.expected_final_time, "abs_tol": 1.0e-10},
            ["logs/stdout.log"],
        ),
        criterion(
            "force-history-sample-count",
            len(rows) == expected_samples,
            len(rows),
            "rows",
            "==",
            expected_samples,
            [str(force_path.relative_to(run_dir))] if force_path.exists() else [],
        ),
        criterion(
            "force-history-time-range",
            time_range_ok,
            {"initial": times[0] if times else None, "final": times[-1] if times else None},
            "nondimensional time",
            "initial == 0 and final == expected within abs_tol",
            {"expected_final": expected_force_final_time, "abs_tol": 1.0e-10},
            [str(force_path.relative_to(run_dir))] if force_path.exists() else [],
        ),
        criterion(
            "force-history-finite",
            finite,
            {"finite": finite, "parse_error": force_error},
            None,
            "all finite",
            True,
            [str(force_path.relative_to(run_dir))] if force_path.exists() else [],
        ),
        criterion(
            "no-reported-nonfinite-state",
            not log_matches,
            len(log_matches),
            "matching lines",
            "==",
            0,
            ["logs/stdout.log", "logs/stderr.log"],
        ),
    ]
    outcome = "PASS" if all(item["status"] == "PASS" for item in criteria) else "FAIL"
    metrics_doc = {"schema_version": 1, "metrics": metrics, "diagnostics": {"bad_state_matches": log_matches}}
    verdict_doc = {
        "schema_version": 1,
        "outcome": outcome,
        "criteria_definition": {"path": "inputs/README.md", "sha256": None},
        "criteria": criteria,
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics_doc, indent=2) + "\n")
    (run_dir / "verdict.json").write_text(json.dumps(verdict_doc, indent=2) + "\n")
    print(json.dumps({"outcome": outcome, "metrics": metrics}, indent=2))
    return 0 if outcome == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
