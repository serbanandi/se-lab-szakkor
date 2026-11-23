# E: Agent with tools

## What to do

On Windows, use Command Prompt (cmd), not PowerShell.

1. Open your agent in the `se-lab-E` worktree, and only there. Start a **new conversation** in **agent mode**.
2. Copy the prompt below as it is and send it. Wait until the agent finishes. It may run the check command, the report script and at most 5 measure runs.
3. Measure in the worktree: Windows `.\mvnw.cmd test -Pllm`, Linux `./mvnw test -Pllm`
4. Look at the result: Windows `py scripts/report.py`, Linux `python3 scripts/report.py`
5. Fill in a row of the shared sheet by hand, as strategy E (see [HANDOUT.md](../HANDOUT.md)).

## Prompt

```text
Write comprehensive unit tests for GT4500. The goal is maximum branch coverage and maximum PIT mutation score for GT4500.

The class is src/main/java/hu/bme/mit/spaceship/GT4500.java. Its specification is the Javadoc of GT4500.fireTorpedo; test against that. Write one JUnit 5 + Mockito test class named GT4500LlmTest in package hu.bme.mit.spaceship, in the file src/test/java/hu/bme/mit/spaceship/GT4500LlmTest.java. GT4500 has a constructor that takes its two TorpedoStore objects, so they can be mocked.

Work in iterations: write the tests, measure, look at the report and the surviving mutants, improve the tests, and measure again.

Tools:
- Check command (compiles and runs only GT4500LlmTest, fast):
  Windows: .\mvnw.cmd test -Pcheck
  Linux: ./mvnw test -Pcheck
- Measure command (coverage and PIT for GT4500LlmTest; all tests must pass):
  Windows: .\mvnw.cmd test -Pllm
  Linux: ./mvnw test -Pllm
- Report of the last measure run:
  Windows: py scripts/report.py
  Linux: python3 scripts/report.py
- Surviving mutants of the last measure run:
  Windows: py scripts/report.py --survivors --with-source
  Linux: python3 scripts/report.py --survivors --with-source

Rules:
- Run the measure command at most 5 times.
- Do not modify production code; equivalent mutants may be impossible to kill, so say which ones you think they are and stop.
- If a test fails, decide from the Javadoc whether the test or the code is wrong. Never change an assertion just to make it pass. If you think the code is wrong, leave the test failing and say so.
```
