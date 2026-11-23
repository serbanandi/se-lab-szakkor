# D: Two-shot

Round 1 is strategy A, so this continues in the same `se-lab-AD` worktree and the same conversation.
On Windows, use Command Prompt (cmd), not PowerShell: PowerShell would write `survivors.txt` in an encoding some agents can't read.

## What to do

1. Send the round 1 prompt (exactly A's prompt), measure and fill in its row as A, following [A-one-shot.md](A-one-shot.md). Already done? Go on.
2. **After** filling in A's row, write the surviving mutants to a file in the worktree:
   - Windows: `py scripts/report.py --survivors --with-source > survivors.txt`
   - Linux: `python3 scripts/report.py --survivors --with-source > survivors.txt`
3. Send the round 2 prompt and wait until the agent finishes.
4. Measure again: Windows `.\mvnw.cmd test -Pllm`, Linux `./mvnw test -Pllm`
5. Fill in a row of the shared sheet by hand, as strategy D (see [HANDOUT.md](../HANDOUT.md)). "Agent fixed failures" and "Agent saw quality metrics" cover both rounds. Reading `survivors.txt` is part of the strategy, so it doesn't count as seeing metrics.

## Prompt, round 1

```text
Write comprehensive unit tests for GT4500.

The class is src/main/java/hu/bme/mit/spaceship/GT4500.java. Its specification is the Javadoc of GT4500.fireTorpedo; test against that. Write one JUnit 5 + Mockito test class named GT4500LlmTest in package hu.bme.mit.spaceship, in the file src/test/java/hu/bme/mit/spaceship/GT4500LlmTest.java. GT4500 has a constructor that takes its two TorpedoStore objects, so they can be mocked.

Rules:
- You may run the check command, which compiles and runs only GT4500LlmTest, to fix compile errors and failing tests:
  Windows: .\mvnw.cmd test -Pcheck
  Linux: ./mvnw test -Pcheck
- Do not run coverage, PIT or scripts/report.py, and do not read files under target/site/jacoco or target/pit-reports.
- Do not modify production code.
- If a test fails, decide from the Javadoc whether the test or the code is wrong. Never change an assertion just to make it pass. If you think the code is wrong, leave the test failing and say so.
```

## Prompt, round 2

```text
The mutants listed in survivors.txt survived PIT mutation testing. Add or strengthen tests in GT4500LlmTest to kill them. Don't delete passing tests. Still test against the Javadoc of fireTorpedo.

Rules:
- You may run the check command, which compiles and runs only GT4500LlmTest, to fix compile errors and failing tests:
  Windows: .\mvnw.cmd test -Pcheck
  Linux: ./mvnw test -Pcheck
- Do not run coverage, PIT or scripts/report.py, and do not read files under target/site/jacoco or target/pit-reports.
- Do not modify production code.
- If a test fails, decide from the Javadoc whether the test or the code is wrong. Never change an assertion just to make it pass. If you think the code is wrong, leave the test failing and say so.
```
