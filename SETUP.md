# Setup (before the session)

Takes about 20 minutes, mostly downloads. **On Windows, use Command Prompt (cmd)** for every command, not PowerShell. Open a new window after installing something, so that PATH is up to date.

## 1. JDK 21 or newer

- Windows: `winget install EclipseAdoptium.Temurin.21.JDK`
- Linux (Debian/Ubuntu): `sudo apt install openjdk-21-jdk`. Other distros: install the OpenJDK 21+ package of your distro.

Check with `java -version`. The Maven wrapper (`mvnw`) needs `java` on PATH or `JAVA_HOME` set; if `JAVA_HOME` is set, it must also point to a JDK 21+.

## 2. Python 3.9 or newer

- Windows: `winget install Python.Python.3.12`. Check with `py --version`. Use `py`, which always works: plain `python` may open the Microsoft Store instead (you can turn that off under Settings → App execution aliases).
- Linux: usually installed already. Check with `python3 --version`.

## 3. git 2.20 or newer (for worktrees)

- Windows: `winget install Git.Git`
- Linux (Debian/Ubuntu): `sudo apt install git`. Other distros: use your package manager.

## 4. One agent, signed in, with agent mode working

Pick **one** (same steps on Windows and Linux):

- **GitHub Copilot in VS Code**: install [VS Code](https://code.visualstudio.com/), sign in with GitHub, and check that agent mode is available in the Chat view. Students can get Copilot free through the [GitHub Student Developer Pack](https://education.github.com/pack).
- **Google Antigravity**: install [Antigravity](https://antigravity.google/) and sign in with a Google account.
- **Claude Code**: follow the [official install instructions](https://code.claude.com/docs/en/setup) and sign in. It needs a Claude subscription or API credits.

**Try it:** open an empty test folder, and ask the agent to create a file there and then change it. This shows login, quota and region problems now and not during the session.

## 5. Clone the repository

```
git clone <REPO_URL>
cd se-lab-szakkor
```

## 6. Run the self-check

- Windows: `py scripts/check_setup.py`
- Linux: `python3 scripts/check_setup.py`

The first run downloads everything the session needs. Fix what it reports and run it again until the last line is `READY`. If it still fails, email <INSTRUCTOR_EMAIL> with the full output.

## Troubleshooting

| The check says | Do this |
|---|---|
| `Python ... is too old` | Section 2. On Windows, run the check with `py`. |
| `java was not found on PATH` | Section 1, then open a new terminal. |
| `... is Java 17` (or other old version), `... does not work` | Section 1. Put JDK 21+ first on PATH, and make `JAVA_HOME` point to it or unset it. |
| `git was not found on PATH`, `git is too old` | Section 3, then open a new terminal. |
| `the current directory is not the root of the repository`, `mvnw was not found` | `cd` into the cloned `se-lab-szakkor` folder. |
| `mvnw is not executable` (Linux) | `chmod +x mvnw` |
| `GT4500LlmTest.java already exists` | Move the file away, or run the check in a clean clone. |
| `the measure command failed` / `wrote no ...`, `the check command failed` **(Maven)** | Check your internet connection (VPN, proxy), then run the check again. For compile errors, see section 1 and make sure `git status` shows no changes. |
| `scripts/report.py failed` **(report)** | Make sure `git status` shows no changes, then run the check again. |
| `git worktree does not work`, `git worktree remove does not work` | Section 3. Check that you can write to your temporary folder. |
| `no agent found` (warning only) | Section 4. If your agent is installed and signed in, ignore it. |
| `interrupted` | Run the check again and let it finish. |
