# B: One-shot + coverage goal

## What to do

On Windows, use Command Prompt (cmd), not PowerShell.

1. Open your agent in the `se-lab-B` worktree, and only there. Start a **new conversation** in **agent mode**.
2. Copy the prompt below as it is and send it. Wait until the agent finishes. It may run only the check command.
3. Measure in the worktree: Windows `.\mvnw.cmd test -Pllm`, Linux `./mvnw test -Pllm`
4. Look at the result: Windows `py scripts/report.py`, Linux `python3 scripts/report.py`
5. Fill in a row of the shared sheet by hand, as strategy B (see [HANDOUT.md](../HANDOUT.md)).

## Prompt

```text
Write comprehensive unit tests for GT4500. Aim for 100% branch coverage.

The class is src/main/java/hu/bme/mit/spaceship/GT4500.java. Its specification is the Javadoc of GT4500.fireTorpedo; test against that. Write one JUnit 5 + Mockito test class named GT4500LlmTest in package hu.bme.mit.spaceship, in the file src/test/java/hu/bme/mit/spaceship/GT4500LlmTest.java. GT4500 has a constructor that takes its two TorpedoStore objects, so they can be mocked.

Rules:
- You may run the check command, which compiles and runs only GT4500LlmTest, to fix compile errors and failing tests:
  Windows: .\mvnw.cmd test -Pcheck
  Linux: ./mvnw test -Pcheck
- Do not run coverage, PIT or scripts/report.py, and do not read files under target/site/jacoco or target/pit-reports.
- Do not modify production code.
- If a test fails, decide from the Javadoc whether the test or the code is wrong. Never change an assertion just to make it pass. If you think the code is wrong, leave the test failing and say so.
```
