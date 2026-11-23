# Handout: LLM-based unit test generation

> **On Windows, use Command Prompt (cmd), not PowerShell.** In VS Code, pick *Command Prompt* in the terminal's drop-down.

## Before the session
You should have done [SETUP.md](SETUP.md) and seen `READY`. If you haven't, run the self-check now (Windows `py scripts/check_setup.py`, Linux `python3 scripts/check_setup.py`).

## The task

Let an agent write unit tests for the `GT4500` spaceship in `src/test/java/hu/bme/mit/spaceship/GT4500LlmTest.java`. The specification is the Javadoc of `GT4500.fireTorpedo` and `GT4500.fireLaser`. **Coverage** is the share of lines or branches the tests execute. **Mutation score** is the share of small artificial bugs (mutants) that make at least one test fail.

Your task will be to evaluate different mutation-guided test generation strategies. First, you'll generate tests with a simple prompt, evaluate, and improve them based on mutation feedback. The strategies are explained in [prompts/README.md](prompts/README.md).

We'll all document our results in a shared sheet. This will let us compare strategies and see how well the agents did, how different models, prompts and harnesses were influenced by the mutation feedback, allowing us to draw conclusions about the effectiveness of each approach. The sheet is [here](https://bmeedu-my.sharepoint.com/:x:/g/personal/serban_andrada_edu_bme_hu/cQrB7qv3PQc2SbqQv1jTUG_VEgUCHyDE7fYm360i-tG0JlbuCQK).

### Creating git worktrees

Git worktrees are separate checkouts of the same repository. Each strategy gets its own worktree, so the agents don't interfere with each other. The worktrees share the Maven cache, so dependencies aren't downloaded again.

Create the worktrees you'll use from the main clone:

```
git worktree add ../se-lab-AD -b try/AD
git worktree add ../se-lab-B -b try/B
git worktree add ../se-lab-C -b try/C
git worktree add ../se-lab-E -b try/E
```

feel free to try each strategy with multiple agents. Give each of them their own worktree by adding a suffix to the branch:

```
git worktree add ../se-lab-B/copilot -b try/B-copilot
```

### Starting agent sessions
Open the agent in the created worktree:

| Agent | How |
|---|---|
| Claude Code | Windows `cd ..\se-lab-B`, Linux `cd ../se-lab-B`, then `claude` |
| VS Code + Copilot | Windows `code ..\se-lab-B`, Linux `code ../se-lab-B`; use agent mode in the new window |
| Antigravity | open the `se-lab-B` folder as the workspace |

Start a **new agent conversation** for each strategy, so nothing carries over. (D is the exception: it continues A's conversation.) Run the measure and report commands from inside the worktree.

### Running a test generation strategy

1. In the agent opened in the worktree, paste the prompt from `prompts/<X>.md`. Wait until it finishes.
2. Evaluate tests with mutation testing:
    - Windows `.\mvnw.cmd test -Pllm`
    - Linux `./mvnw test -Pllm`
3. Parse the report: 
    - Windows `py scripts/report.py`
    - Linux `python3 scripts/report.py`

### Documenting results

Fill in one row of the [shared sheet](https://bmeedu-my.sharepoint.com/:x:/g/personal/serban_andrada_edu_bme_hu/cQrB7qv3PQc2SbqQv1jTUG_VEgUCHyDE7fYm360i-tG0JlbuCQK).

## Cleaning up

From the main clone:

```
git worktree list
git worktree remove ../se-lab-B
git branch -D try/B
```

To keep a result, commit it in the worktree first, and don't delete its branch. If you didn't commit, git refuses to remove the worktree: add `--force` to throw the tests away.

## Troubleshooting

- **`./mvnw: Permission denied`** (Linux): `chmod +x mvnw`.
- **Wrong Java:** `java -version` must say 21 or newer; `JAVA_HOME`, if set, must too.
- **`py` or `python`?** Windows `py`, Linux `python3`.
- **The agent asks to run a command in A–D:** allow only the check command (Windows `.\mvnw.cmd test -Pcheck`, Linux `./mvnw test -Pcheck`).
- **The agent changed production code:** `git diff src/main` shows it. Discard the attempt: remove the worktree with `--force`, delete its branch and start again.
- **The measure command fails because a test fails:** see [prompts/README.md](prompts/README.md#if-the-agent-leaves-a-test-failing).

## At-home bonus tasks

### The oracle problem

`planted-bug` is another version of the ship. Run strategy E on it and see whether any generated test fails. Don't add a row to the shared sheet.

```
git worktree add --no-track ../se-lab-bonus -b try/bonus origin/planted-bug
```

What you might encounter here is that the agent happily geenrates a passing test suite for this buggy ship, because it doesn't know this isn't the correct behavior. This is the oracle problem: the agent doesn't know what the correct behavior is, so it can't tell whether a test is right or wrong. It might detect the bug though. In this case, try palying around with other bugs in the ship, and see if the agent can detect them. If it can't, you have a real oracle problem. An interesting approach would be to do this for the mutants that tended to survive PIT testing and see if the agent can detect them. This is a good way to test the agent's ability to reason about the code and its behavior.

### Other mutation operators

A mutation score only tells you about the kinds of bugs PIT was asked to plant. The session uses the `STRONGER` group. You can measure the same tests again with another group:

- Windows: `.\mvnw.cmd test -Pllm -Dpit.mutators=ALL`
- Linux: `./mvnw test -Pllm -Dpit.mutators=ALL`

Try `DEFAULTS` (fewer mutants), `ALL` (many more), or a list such as `NEGATE_CONDITIONALS,VOID_METHOD_CALLS`; the [PIT documentation](https://pitest.org/quickstart/mutators/) describes them. Then run `report.py --survivors --with-source` and think about:

- Does 100% with one group stay 100% with another? What does that say about the score?
- Which survivors show a missing test, and which are equivalent mutants that no test can kill?
- Does the ranking of the strategies change?

Scores from different groups aren't comparable. **In the session, keep the default**, and don't add these results to the shared sheet.
