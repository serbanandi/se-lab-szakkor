# SE Spaceship: LLM test generation demo

A small Java project for experimenting with **LLM-based unit test generation**, **code coverage** and **mutation testing**.
It is based on the sample application of the [Software Engineering](http://www.mit.bme.hu/oktatas/targyak/vimiab04) course at BME MIT.

## Getting started

You need **Java 21+**. Maven is optional: the Maven wrapper (`./mvnw`, or `mvnw.cmd` on Windows) downloads it for you.
Alternatively, open the repository in **GitHub Codespaces** / a VS Code **Dev Container**, where everything is preinstalled.

| What | Command | Report |
|---|---|---|
| Build | `./mvnw compile` | |
| Run tests + coverage | `./mvnw test` | `target/site/jacoco/index.html` |
| Mutation testing | `./mvnw test-compile org.pitest:pitest-maven:mutationCoverage` | `target/pit-reports/index.html` (and `mutations.xml`) |

Tip: `mutations.xml` lists every surviving mutant in a machine-readable form, so it can be pasted into an LLM prompt.

Dependencies already configured: JUnit 5, Mockito (incl. `mockito-junit-jupiter`), JaCoCo, PIT (with the JUnit 5 plugin).

## Overview

The project represents an alpha version of a spaceship.

- The ship (`SpaceShip` interface) can fire one or more lasers or torpedoes.
- We have only one spaceship as of now (`GT4500`).
- Two firing modes (`FiringMode`) are supported: firing only one or all instances of a given weapon type.
- Lasers are not yet implemented, but the torpedo stores are ready (`TorpedoStore`).
- The rules for firing torpedoes are in the Javadoc comment of `GT4500.fireTorpedo`: this is the **specification** to test against.
- `GT4500` has a constructor that takes its two `TorpedoStore`s, so they can be replaced by Mockito mocks in unit tests.
- `TorpedoStore` can randomly fail to fire; set the `IVT_RATE` environment variable (0.0 to 1.0) to control the failure rate (default: 0.0).
- `GT4500Test` contains two starter tests. They pass and cover a good part of the code, but they are not proper unit tests (no isolation), and they check very little. Run PIT to see how little.
