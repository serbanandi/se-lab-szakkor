#!/usr/bin/env python3
"""Check that this computer is ready for the session (Python 3.9+, standard library only).

Run from the repository root:
  Windows: py scripts/check_setup.py        Linux: python3 scripts/check_setup.py
The last line is READY or NOT READY. The repository is left as it was found.
"""
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WINDOWS = os.name == "nt"
MVNW = Path("mvnw.cmd" if WINDOWS else "mvnw")
JACOCO = Path("target/site/jacoco")
PIT = Path("target/pit-reports")
PACKAGE = Path("hu/bme/mit/spaceship")
TEMP_TEST = Path("src/test/java") / PACKAGE / "GT4500LlmTest.java"
TEMP_CLASSES = Path("target/test-classes") / PACKAGE
TEMP_TEST_SOURCE = """package hu.bme.mit.spaceship;

import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

class GT4500LlmTest {
  @Test
  void temporaryTestOfCheckSetup() {
    assertTrue(true);
  }
}
"""

problems = 0


def ok(text):
    print("[OK]   " + text, flush=True)


def warn(text):
    print("[WARN] " + text, flush=True)


def fail(text, fix, output=""):
    global problems
    problems += 1
    print(f"[FAIL] {text} -> {fix}", flush=True)
    for line in output.splitlines():
        print("         " + line.rstrip())


def run(command, timeout=None):
    """(exit code, combined output); exit code None if the command could not be run."""
    try:
        # stdin is closed so that no child waits for input, e.g. after Ctrl+C on Windows
        p = subprocess.run([str(c) for c in command], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)
    return p.returncode, p.stdout.decode("utf-8", errors="replace")


def run_maven(*arguments):
    return run([MVNW.resolve(), "-B"] + list(arguments))


def maven_errors(output):
    """The part of the Maven output worth showing."""
    lines = [x for x in output.splitlines() if "ERROR" in x] or output.splitlines()
    return "\n".join(lines[:15])


def check_python():
    version = ".".join(str(x) for x in sys.version_info[:3])
    if sys.version_info >= (3, 9):
        ok(f"Python {version}")
    else:
        fail(f"Python {version} is too old", "install Python 3.9 or newer, see SETUP.md section 2")


def java_major(java):
    """(major version or None, first line of the output)"""
    _, output = run([java, "-version"], timeout=60)
    match = re.search(r'version "(\d+)(?:\.(\d+))?', output)
    if not match:
        return None, output.strip().splitlines()[0] if output.strip() else "no output"
    major = int(match.group(1))
    if major == 1 and match.group(2):  # "1.8.0" is Java 8
        major = int(match.group(2))
    return major, match.string[match.start():].splitlines()[0]


def check_java():
    java = shutil.which("java")
    if java is None:
        fail("java was not found on PATH", "install JDK 21+, see SETUP.md section 1")
        return False
    candidates = [("java on PATH", java)]
    home = os.environ.get("JAVA_HOME", "").strip()
    if home:  # the Maven wrapper prefers JAVA_HOME over PATH
        candidates.append(("JAVA_HOME", str(Path(home) / "bin" / "java")))
    for label, path in candidates:
        major, text = java_major(path)
        if major is None:
            fail(f"{label} ({path}) does not work: {text}", "reinstall the JDK or fix JAVA_HOME, see SETUP.md section 1")
            return False
        if major < 21:
            fail(f"{label} ({path}) is Java {major}", "Java 21+ is needed, see SETUP.md section 1")
            return False
        ok(f"{label}: Java {major} ({path})")
    return True


def check_git():
    git = shutil.which("git")
    if git is None:
        fail("git was not found on PATH", "install git 2.20+, see SETUP.md section 3")
        return False
    _, output = run([git, "--version"], timeout=60)
    match = re.search(r"(\d+)\.(\d+)", output)
    if not match or (int(match.group(1)), int(match.group(2))) < (2, 20):
        fail(f"git is too old ({output.strip()})", "install git 2.20+, see SETUP.md section 3")
        return False
    code, top = run([git, "rev-parse", "--show-toplevel"], timeout=60)
    if code != 0 or not Path(top.strip()).exists() or not os.path.samefile(top.strip(), "."):
        fail("the current directory is not the root of the repository",
             "cd into the cloned folder and run the check there, see SETUP.md section 5")
        return False
    ok(f"git {match.group(0)}, running in the repository root")
    return True


def check_wrapper():
    if not MVNW.is_file():
        fail(f"{MVNW} was not found", "run this from the repository root, see SETUP.md section 5")
        return False
    if not WINDOWS and not os.access(str(MVNW), os.X_OK):
        fail("mvnw is not executable", "run: chmod +x mvnw (SETUP.md, Troubleshooting)")
        return False
    ok(f"{MVNW} can be run")
    return True


def check_measure():
    print("       Running the build, coverage and PIT: this can take a few minutes the first time...", flush=True)
    for folder in (JACOCO, PIT):  # so that old reports can't hide a failure
        shutil.rmtree(str(folder), ignore_errors=True)
    start = time.monotonic()
    # the goals of `test -Pllm`, but on the starter tests
    code, output = run_maven("test", "org.pitest:pitest-maven:mutationCoverage")
    if code != 0:
        fail("the measure command failed", "see SETUP.md, Troubleshooting (Maven)", maven_errors(output))
        return False
    missing = [str(f) for f in (JACOCO / "jacoco.csv", PIT / "mutations.xml") if not f.is_file()]
    if missing:
        fail("the measure command wrote no " + ", ".join(missing), "see SETUP.md, Troubleshooting (Maven)")
        return False
    ok(f"measure command works ({time.monotonic() - start:.0f} s)")
    return True


def check_check_command():
    try:
        # written inside try, so it is removed however we leave
        TEMP_TEST.write_text(TEMP_TEST_SOURCE, encoding="utf-8")
        code, output = run_maven("test", "-Pcheck")
    finally:
        interrupt = signal.signal(signal.SIGINT, signal.SIG_IGN)
        if TEMP_TEST.exists():
            TEMP_TEST.unlink()
        for class_file in TEMP_CLASSES.glob("GT4500LlmTest*.class"):
            class_file.unlink()
        signal.signal(signal.SIGINT, interrupt)
    if code != 0:
        fail("the check command failed", "see SETUP.md, Troubleshooting (Maven)", maven_errors(output))
    else:
        ok("check command works")


def check_report():
    code, output = run([sys.executable, Path("scripts") / "report.py"], timeout=60)
    if code != 0 or not re.search(r"Mutation score:\s+\d+%", output):
        fail("scripts/report.py failed", "see SETUP.md, Troubleshooting (report)", output)
        return
    ok("report.py works; the starter tests on GT4500:")
    for line in output.split("TorpedoStore")[0].splitlines()[1:]:
        print("       " + line)


def check_worktree():
    git = shutil.which("git")
    base = Path(tempfile.mkdtemp(prefix="se-lab-check-"))
    tree = base / "worktree"
    try:
        code, output = run([git, "worktree", "add", "--detach", tree], timeout=120)
        has_pom = (tree / "pom.xml").is_file()
        removed, remove_output = run([git, "worktree", "remove", tree], timeout=120)
    finally:
        interrupt = signal.signal(signal.SIGINT, signal.SIG_IGN)
        shutil.rmtree(str(base), ignore_errors=True)
        run([git, "worktree", "prune"], timeout=60)
        signal.signal(signal.SIGINT, interrupt)
    if code != 0 or not has_pom:
        fail("git worktree does not work", "see SETUP.md section 3", output)
    elif removed != 0:
        fail("git worktree remove does not work", "see SETUP.md section 3", remove_output)
    else:
        ok("git worktrees work")


def check_harness():
    found = []
    claude = shutil.which("claude")
    if claude and run([claude, "--version"], timeout=60)[0] == 0:
        found.append("Claude Code")
    code = shutil.which("code")
    if code and run([code, "--version"], timeout=60)[0] == 0:
        extensions = run([code, "--list-extensions"], timeout=60)[1].lower().split()
        if "github.copilot" in extensions or "github.copilot-chat" in extensions:
            found.append("GitHub Copilot in VS Code")
    local = os.environ.get("LOCALAPPDATA")
    if shutil.which("antigravity") or (
            local and (Path(local) / "Programs" / "Antigravity" / "Antigravity.exe").is_file()):
        found.append("Google Antigravity")
    if found:
        ok("agent found: " + ", ".join(found) + " (check yourself that you are signed in)")
    else:
        warn("no agent found: make sure your harness is installed and signed in, see SETUP.md section 4")


def main():
    check_python()
    java = check_java()
    git = check_git()
    wrapper = check_wrapper()
    can_build = java and git and wrapper
    if not can_build:
        warn("skipped the build, check command and report: fix the problems above first")
    elif TEMP_TEST.exists():
        fail(f"{TEMP_TEST.as_posix()} already exists",
             "move it away and run the check in a clean clone, see SETUP.md section 5")
    else:
        measured = check_measure()
        check_check_command()
        if measured:
            check_report()
        else:
            warn("skipped report.py: there are no reports yet")
    if git:
        check_worktree()
    else:
        warn("skipped the worktree check: fix git first")
    check_harness()


if __name__ == "__main__":
    if not sys.stdout.isatty() and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    started = time.monotonic()
    try:
        main()
    except KeyboardInterrupt:
        fail("interrupted", "run the check again")
    print(f"Total time: {time.monotonic() - started:.0f} s")
    print("READY" if problems == 0 else f"NOT READY ({problems} problems)")
    sys.exit(0 if problems == 0 else 1)
