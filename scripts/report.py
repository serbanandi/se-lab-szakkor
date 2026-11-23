#!/usr/bin/env python3
"""Summarise the JaCoCo and PIT results of GT4500 (Python 3.9+, standard library only).

Run from the root of a worktree, after the measure command:
  Windows: py scripts/report.py        Linux: python3 scripts/report.py
"""
import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

JACOCO = Path("target/site/jacoco/jacoco.csv")
PIT = Path("target/pit-reports/mutations.xml")
PACKAGE = Path("hu/bme/mit/spaceship")
MAIN_SRC = Path("src/main/java") / PACKAGE
TEST_FILE = Path("src/test/java") / PACKAGE / "GT4500LlmTest.java"

MEASURE = ("Run the measure command first:\n"
           "  Windows: .\\mvnw.cmd test -Pllm\n"
           "  Linux:   ./mvnw test -Pllm")


class ReportError(Exception):
    """A problem the user can fix; printed without a stack trace."""


def percent(part, total):
    """Whole-number percentage, or None if there is nothing to measure."""
    return int(100 * part / total + 0.5) if total else None


def check_reports():
    for report in (JACOCO, PIT):
        if not report.is_file():
            raise ReportError(f"Missing report: {report.as_posix()}\n{MEASURE}")
    # A failing measure run leaves the reports of the previous run behind.
    csv_time, xml_time = JACOCO.stat().st_mtime, PIT.stat().st_mtime
    newest_source = max((f.stat().st_mtime for f in Path("src").rglob("*.java")), default=0)
    if newest_source > csv_time or csv_time > xml_time:
        raise ReportError("The reports are out of date: the code changed, or the last measure run failed.\n"
                          + MEASURE)


def read_coverage():
    """{class name: (line %, branch %)}"""
    with JACOCO.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    result = {}
    for row in rows:
        values = []
        for kind in ("LINE", "BRANCH"):
            covered, missed = int(row[kind + "_COVERED"]), int(row[kind + "_MISSED"])
            values.append(percent(covered, covered + missed))
        result[row["CLASS"]] = tuple(values)
    return result


def read_mutants(class_name):
    """The PIT mutants in the source file of the class, sorted by line."""
    mutants = []
    for m in ET.parse(PIT).getroot().iter("mutation"):
        if m.findtext("sourceFile") != class_name + ".java":
            continue
        mutants.append({
            "file": m.findtext("sourceFile"),
            "line": int(m.findtext("lineNumber")),
            "method": m.findtext("mutatedMethod"),
            "mutator": m.findtext("mutator").rsplit(".", 1)[-1].replace("Mutator", ""),
            "description": m.findtext("description"),
            "status": m.get("status"),
            "detected": m.get("detected") == "true",
        })
    return sorted(mutants, key=lambda x: (x["file"], x["line"], x["method"], x["mutator"]))


def mutation_stats(mutants):
    def count(status):
        return sum(m["status"] == status for m in mutants)

    detected = sum(m["detected"] for m in mutants)  # as in PIT, includes timed out mutants
    return {
        "score": percent(detected, len(mutants)),
        "killed": count("KILLED"), "survived": count("SURVIVED"),
        "no_coverage": count("NO_COVERAGE"), "timed_out": count("TIMED_OUT"), "total": len(mutants),
    }


def test_source():
    """The generated test class without comments, or None if there is none."""
    if not TEST_FILE.is_file():
        return None
    text = TEST_FILE.read_text(encoding="utf-8", errors="replace")
    # match string literals too, so that a // or /* inside them is not taken for a comment
    pattern = r'"""(?:\\.|[^\\])*?"""|"(?:\\.|[^"\\\n])*"|/\*.*?\*/|//[^\n]*'
    return re.sub(pattern, lambda m: '""' if m.group().startswith('"') else " ", text, flags=re.S)


def count_tests(source):
    return len(re.findall(r"@(?:Test|ParameterizedTest|RepeatedTest)\b", source))


def print_summary():
    coverage = read_coverage()

    def pct(value):
        return "n/a" if value is None else f"{value}%"

    for name in ("GT4500", "TorpedoStore"):
        line, branch = coverage.get(name, (None, None))
        s = mutation_stats(read_mutants(name))
        print(name)
        print(f"  Line coverage:   {pct(line)}")
        print(f"  Branch coverage: {pct(branch)}")
        print(f"  Mutation score:  {pct(s['score'])}")
        print(f"  Mutants: killed {s['killed']}, survived {s['survived']}, no coverage {s['no_coverage']}, "
              f"timed out {s['timed_out']}, total {s['total']}")
    source = test_source()
    if source is None:
        print(f"Tests in GT4500LlmTest: none ({TEST_FILE.as_posix()} does not exist)")
    else:
        print(f"Tests in GT4500LlmTest: {count_tests(source)}")
        print(f"Uses mocks: {'yes' if 'org.mockito' in source else 'no'}")


def print_survivors(with_source):
    sources = {}
    for m in read_mutants("GT4500"):
        if m["status"] not in ("SURVIVED", "NO_COVERAGE"):
            continue
        print(f"{m['file']}:{m['line']} {m['method']}  {m['mutator']}  {m['description']}  [{m['status']}]")
        if with_source:
            if m["file"] not in sources:
                sources[m["file"]] = (MAIN_SRC / m["file"]).read_text(encoding="utf-8").splitlines()
            lines = sources[m["file"]]
            print("    " + (lines[m["line"] - 1].strip() if m["line"] <= len(lines) else ""))


def parse_args():
    p = argparse.ArgumentParser(description="Summarise coverage and mutation testing results of GT4500.")
    p.add_argument("--survivors", action="store_true", help="list the GT4500 mutants that were not killed")
    p.add_argument("--with-source", action="store_true", help="with --survivors: add the mutated source line")
    return p.parse_args()


def main():
    if not sys.stdout.isatty():
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    check_reports()
    if args.survivors:
        print_survivors(args.with_source)
    else:
        print_summary()


if __name__ == "__main__":
    try:
        main()
    except ReportError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except (OSError, ET.ParseError, KeyError, ValueError) as e:
        print(f"Could not read the reports: {e}\n{MEASURE}", file=sys.stderr)
        sys.exit(1)
