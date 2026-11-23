# SE Spaceship: LLM test generation demo

**Before the session:** follow [SETUP.md](SETUP.md) until the self-check says `READY`.

**During the session:** follow [HANDOUT.md](HANDOUT.md).

A small Java project for experimenting with **LLM-based unit test generation**, **code coverage** and **mutation testing**.
It is based on the sample application of the [Software Engineering](http://www.mit.bme.hu/oktatas/targyak/vimiab04) course at BME MIT.

## Getting started

You need **Java 21+**. Maven is optional: the Maven wrapper (`./mvnw`, or `mvnw.cmd` on Windows) downloads it for you.

| What | Command | Report |
|---|---|---|
| Build | `./mvnw compile` | |
| Run tests + coverage | `./mvnw test` | `target/site/jacoco/index.html` |
| Coverage + PIT, only the generated tests | `./mvnw test -Pllm` | both reports |
| Run only the generated tests | `./mvnw test -Pcheck` | |
| Mutation testing | `./mvnw test-compile org.pitest:pitest-maven:mutationCoverage` | `target/pit-reports/index.html` (and `mutations.xml`) |

The generated tests go in `src/test/java/hu/bme/mit/spaceship/GT4500LlmTest.java`. On Windows, use Command Prompt and write `.\mvnw.cmd` in place of `./mvnw`.
PIT uses the `STRONGER` group of mutation operators (`pit.mutators` in `pom.xml`). To try others at home, see [HANDOUT.md](HANDOUT.md#at-home-try-other-mutation-operators).
`scripts/report.py` summarises the results and lists the surviving mutants. The prompts are in [prompts/](prompts/README.md).

Dependencies already configured: JUnit 5, Mockito (incl. `mockito-junit-jupiter`), JaCoCo, PIT (with the JUnit 5 plugin).

## Overview

The project represents an alpha version of a spaceship.

- The ship (`SpaceShip` interface) can fire one or more lasers or torpedoes.
- We have only one spaceship as of now (`GT4500`).
- Two firing modes (`FiringMode`) are supported: firing only one or all instances of a given weapon type.
- Lasers are not yet implemented, but the torpedo stores are ready (`TorpedoStore`).
- The rules for firing torpedoes are in the Javadoc comment of `GT4500.fireTorpedo`: this is the **specification** to test against.
- `GT4500` has a constructor that takes its two `TorpedoStore`s, so unit tests can replace them with Mockito mocks; the no-argument constructor creates two real stores.
- `TorpedoStore` can randomly fail to fire; set the `IVT_RATE` environment variable (0.0 to 1.0) to control the failure rate (default: 0.0).
- `GT4500Test` contains two starter tests. They pass and cover a good part of the code, but they are not proper unit tests (no isolation), and they check very little. Run PIT to see how little.
