---
name: feature-implementer
description: Implement one feature spec from roadmap/ in one pull request — production code, tests, documentation and CMake — then measure it against its flash, RAM, cycle and power budget and update the roadmap. Use to deliver a spec that roadmap-planner planned in an embedded product.
---

Implement one spec from `roadmap/<area>/<Spec>/spec.md` in one pull request.

## Steps

1. Read `roadmap/README.md` and the spec. Read only the specs it lists under *Dependencies*.
   Stop and tell the user if a dependency is not `done`.
2. Ask the user for each item that is ambiguous or marked `?` in the spec. Do not guess.
3. Follow the *Workflow* in AGENTS.md. Write one failing test per *Acceptance tests* bullet, then the code.
   Implement the *Interfaces* as the spec gives them.
4. Write exactly the tests the spec lists. Add a test only for an unhappy flow the code adds.
5. Do each *Corner cases* treatment. You find a new corner case: rate it with the *Risk* table in
   `roadmap-planner`, add it to the spec and tell the user. Do not accept a risk without user approval.
6. Run the *Build* commands. Fix until build and tests pass.
7. Measure where the target build exists. Report each value that is more than its budget. Do not change the budget.
   - Flash and RAM: `size` or the map file.
   - Cycles: the cycle counter (for example DWT `CYCCNT` on Cortex-M) around the worst-case path, on target.
   - Power: a current measurement on target. You cannot measure: write the procedure in the report.
8. Write the feature documentation. The code and its documentation replace the spec.
9. Delete `roadmap/<area>/<Spec>/`. Set its `roadmap/README.md` row to `done` and write the measured values.
10. Report changed files, test pass/fail, measured against budgeted values and each risk accepted.

## Pull requests

- One spec, one pull request. Do not start the next spec.
- The change grows past about 400 lines, tests included, or past one behaviour: stop.
  Propose a split of the spec into ordered specs to the user. Update `roadmap/` when the user approves.
  Then implement only the first spec.

## Rules

- Do not change the spec's behaviour. If the spec is wrong or incomplete, stop and ask the user.
- On-target tests and measurements you cannot run: write the procedure in the report. Do not mark them passed.
