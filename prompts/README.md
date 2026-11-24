# Prompt strategies

| Letter | Name | What you do | Branch |
|---|---|---|---|
| [A](A-one-shot.md) | One-shot | One prompt: "Write comprehensive unit tests for GT4500." | `try/AD` |
| [B](B-coverage-goal.md) | One-shot + coverage goal | A + "Aim for 100% branch coverage." | `try/B` |
| [C](C-mutation-aware.md) | One-shot + mutation-aware | A + "The tests will be evaluated with PIT mutation testing." | `try/C` |
| [D](D-two-shot.md) | Two-shot | Prompt A, measure, then a second prompt with the surviving mutants fed back. | `try/AD` |
| [E](E-agent-with-tools.md) | Agent with tools | One prompt that names the tools; the agent iterates on its own. | `try/E` |

A branch can have a suffix, e.g. `try/B-copilot`, if you try a strategy with several agents.

**A and D share one worktree.** D's first round is exactly A: send prompt A, measure and fill in a row as A, then send the D follow-up, measure again and fill in a row as D.

In A–D the agent may run only the **check command** (Windows `.\mvnw.cmd test -Pcheck`, Linux `./mvnw test -Pcheck`). **You** run the **measure command** (Windows `.\mvnw.cmd test -Pllm`, Linux `./mvnw test -Pllm`). Only in E may the agent measure, at most 3 times.

## The two questions only you can answer

Scroll through the agent's transcript before you fill in your row:

- **Agent fixed failures**: `yes` if the check command (in E, also the measure command) showed a compile error or a failing test and the agent then changed something to fix it. `no` if everything compiled and passed the first time.
- **Agent saw quality metrics**: `yes` if the agent ran the measure command, PIT or `report.py`, or read anything under `target/site/jacoco` or `target/pit-reports`. Expected for E, a rule break for A–D (fill in the row anyway). In D, reading the `survivors.txt` you made doesn't count.

## If the agent leaves a test failing

The agent may leave a test failing because it thinks the **code** is wrong. The measure command then fails, because PIT needs a green suite:

1. Note which test fails and why the agent thinks the code is wrong.
2. Mark the test `@Disabled` (import `org.junit.jupiter.api.Disabled`).
3. Measure and fill in the row as usual, with the reason in Notes.
