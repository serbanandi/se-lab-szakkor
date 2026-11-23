# Prompt strategies

| Letter | Name | What you do | Branch |
|---|---|---|---|
| [A](A-one-shot.md) | One-shot | One prompt: "Write comprehensive unit tests for GT4500." | `try/AD` |
| [B](B-coverage-goal.md) | One-shot + coverage goal | A + "Aim for 100% branch coverage." | `try/B` |
| [C](C-mutation-aware.md) | One-shot + mutation-aware | A + "The tests will be evaluated with PIT mutation testing." | `try/C` |
| [D](D-two-shot.md) | Two-shot | Prompt A, measure, then a second prompt with the surviving mutants fed back. | `try/AD` |
| [E](E-agent-with-tools.md) | Agent with tools | One prompt that names the tools; the agent iterates on its own. | `try/E` |

**A and D share one worktree.** D's first round is exactly A: send prompt A, measure and submit as A (`--strategy A`), then send the D follow-up, measure again and submit as D (`--strategy D`).

In A–D the agent may run only the **check command** (Windows `.\mvnw.cmd test -Pcheck`, Linux `./mvnw test -Pcheck`). **You** run the **measure command** (Windows `.\mvnw.cmd test -Pllm`, Linux `./mvnw test -Pllm`). Only in E may the agent measure, at most 5 times.

## The two questions only you can answer

Scroll through the agent's transcript before you submit:

- **Agent fixed failures** (`--fixed yes|no`): `yes` if the check command (in E, also the measure command) showed a compile error or a failing test and the agent then changed something to fix it. `no` if everything compiled and passed the first time.
- **Agent saw quality metrics** (`--saw-metrics yes|no`): `yes` if the agent ran the measure command, PIT or `report.py`, or read anything under `target/site/jacoco` or `target/pit-reports`. Expected for E, a rule break for A–D (submit it anyway). In D, reading the `survivors.txt` you made doesn't count.

## If the agent leaves a test failing

The agent may leave a test failing because it thinks the **code** is wrong. The measure command then fails, because PIT needs a green suite:

1. Note which test fails and why the agent thinks the code is wrong.
2. Mark the test `@Disabled` (import `org.junit.jupiter.api.Disabled`).
3. Measure and submit as usual, with the reason in `--notes "..."`.
