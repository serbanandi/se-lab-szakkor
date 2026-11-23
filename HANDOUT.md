# Handout: LLM-based unit test generation

**On Windows, use Command Prompt (cmd), not PowerShell.** In VS Code, pick *Command Prompt* in the terminal's drop-down.

**Before the session:** you should have done [SETUP.md](SETUP.md) and seen `READY`. If you haven't, run the self-check now (Windows `py scripts/check_setup.py`, Linux `python3 scripts/check_setup.py`).

## The task

Let an agent write unit tests for the `GT4500` spaceship in `src/test/java/hu/bme/mit/spaceship/GT4500LlmTest.java`. The specification is the Javadoc of `GT4500.fireTorpedo`. **Coverage** is the share of lines or branches the tests execute. **Mutation score** is the share of small artificial bugs (mutants) that make at least one test fail.

## Your 15 minutes

Everyone does **A + D** in one worktree, then **one** of **B, C or E**: count off 1–3 (1 = B, 2 = C, 3 = E). If there's time, do another one. The strategies are explained in [prompts/README.md](prompts/README.md).

## One worktree per strategy

Create the worktrees you'll use **at the start**, from the main clone (same on both systems):

```
git worktree add ../se-lab-AD -b try/AD
git worktree add ../se-lab-B -b try/B
```

(Use `C` or `E` in place of `B` if that's your number.) Each worktree is a separate checkout of `main` with its own files and build output, so your attempts can't contaminate each other. The Maven cache is shared, so nothing is downloaded again.

**Open the agent in that folder, and only that folder:**

| Agent | How |
|---|---|
| Claude Code | Windows `cd ..\se-lab-B`, Linux `cd ../se-lab-B`, then `claude` |
| VS Code + Copilot | Windows `code ..\se-lab-B`, Linux `code ../se-lab-B`; use agent mode in the new window |
| Antigravity | open the `se-lab-B` folder as the workspace |

⚠ An agent opened in the main clone or in another worktree edits the wrong files. **Check the folder name before sending a prompt.**

Start a **new agent conversation** for each strategy, so nothing carries over. (D is the exception: it continues A's conversation.) Run the measure and report commands from inside the worktree.

## The loop for each strategy

1. Open the agent in the worktree and paste the prompt from `prompts/<X>.md`. Wait until it finishes.
2. Measure: Windows `.\mvnw.cmd test -Pllm`, Linux `./mvnw test -Pllm`
3. Look: Windows `py scripts/report.py`, Linux `python3 scripts/report.py`
4. Print your row (below) and paste it into the [shared sheet](<SHARED_SHEET_LINK>).

## Submitting

Once, save who you are (harness: `GitHub Copilot`, `Google Antigravity`, `Claude Code` or `Other`):

- Windows: `py scripts/report.py --save --name "Your Name" --harness "Claude Code" --model "model name"`
- Linux: `python3 scripts/report.py --save --name "Your Name" --harness "Claude Code" --model "model name"`

Then, for each strategy, in its worktree:

- Windows: `py scripts/report.py --row --fixed no --saw-metrics no`
- Linux: `python3 scripts/report.py --row --fixed no --saw-metrics no`

In `se-lab-AD`, add `--strategy A` or `--strategy D`. Answer `--fixed` and `--saw-metrics` from the transcript ([how](prompts/README.md#the-two-questions-only-you-can-answer)). If you sent more prompts than planned, add `--rounds N`. Anything surprising: `--notes "..."`. Click the **first empty cell of column A** in `Results` and paste.

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
- **The whole row lands in one cell:** the terminal turned the tabs into spaces. Add `> row.txt` to the `--row` command, open `row.txt` in an editor and copy from there.

## At-home bonus

`planted-bug` is another version of the ship. Run strategy E on it and see whether any generated test fails. Don't add a row to the shared sheet.

```
git worktree add --no-track ../se-lab-bonus -b try/bonus origin/planted-bug
```
