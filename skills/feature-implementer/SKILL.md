---
name: feature-implementer
description: Implement one feature spec from roadmap/ as production code, tests, documentation and CMake, then update the roadmap. Use to deliver a feature that roadmap-planner planned in an embedded product.
---

Implement one feature from `roadmap/<area>/<Feature>/spec.md`.

## Steps

1. Read `roadmap/README.md` and the spec. Read only the specs it lists under *Dependencies*.
   Stop and tell the user if a dependency is not `done`.
2. Ask the user for each item that is ambiguous or marked `?` in the spec. Do not guess.
3. Follow the *Workflow* in AGENTS.md. Write one failing test per *Acceptance tests* bullet, then the code.
   Implement the *Interfaces* as the spec gives them.
4. Write exactly the tests the spec lists. Add a test only for an unhappy flow the code adds.
5. Run the *Build* commands. Fix until build and tests pass.
6. Measure flash and RAM (for example with `size` or the map file) where the target build exists.
   Report each value that is more than its budget. Do not change the budget.
7. Write the feature documentation. The code and its documentation replace the spec.
8. Delete `roadmap/<area>/<Feature>/`. Set its `roadmap/README.md` row to `done` and write the measured flash and RAM.
9. Report changed files, test pass/fail and measured against budgeted flash and RAM.

## Rules

- Implement one feature per pull request. Do not start the next feature.
- Do not change the spec's behaviour. If the spec is wrong or incomplete, stop and ask the user.
- On-target acceptance tests: write the procedure in the report. Do not mark them passed.
