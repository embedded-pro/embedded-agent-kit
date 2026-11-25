---
name: roadmap-planner
description: Turn the features a user states for an embedded product into roadmap/ — a milestone index and one spec per feature, with resource budgets and acceptance tests. Use to start a new project or to plan the next features of an existing one.
---

Write `roadmap/` from the features the user states. Do not write production code or tests.

## Steps

1. Read AGENTS.md *Domain* and *Build*. Read `roadmap/` if it exists. If it has its own format
   (for example `roadmap/DEPLOYMENT.md`), follow that format, not this one.
2. Existing project: read the source tree, the design document and the open issues.
   Mark features that exist as done. Do not plan them again.
3. Ask the user for each item that is missing or ambiguous. Ask in one batch:
   - target MCU or board, flash and RAM available, RTOS or bare metal;
   - the features, each with its trigger, its result and its timing limit;
   - the external interfaces: peripherals, buses, protocols, host tools;
   - the order of priority and the first milestone.
4. Split each feature until one spec is one pull request: one behaviour, testable on the host.
5. Write one `roadmap/<area>/<Feature>/spec.md` per feature, in the *Spec* format. `<area>` is a
   source folder or subsystem, for example `drivers`, `protocol`, `app`.
6. Write `roadmap/README.md` in the *Index* format. Order the features so each one follows the features it depends on.
7. Check: each dependency is in the index; the sum of the budgets is less than the target's flash and RAM;
   each spec has at least one acceptance test.
8. Report the changed files, the open questions and the budget totals.

## Spec

```markdown
# <Feature>

<One sentence: what the feature does and for whom.>

## Behaviour
- <Trigger → result. One bullet per behaviour.>

## Interfaces
- <New or changed interface: name, methods, direction. Hardware: peripheral, pins, bus speed.>

## Constraints
| Flash | RAM | Worst-case time | Context |
|---|---|---|---|
| <bytes> | <bytes> | <µs or ms> | <ISR, task, main loop> |

## Dependencies
- <Other feature spec, or none.>

## Acceptance tests
- <Host test: given, when, then. One bullet per behaviour.>
- <On-target test, only when the host cannot show the behaviour.>
```

## Index

```markdown
# Roadmap

Target: <MCU/board>, <flash> flash, <RAM> RAM, <RTOS or bare metal>.

## <Milestone>
| Feature | Area | Depends on | Flash | RAM | Status |
|---|---|---|---|---|---|
| [<Feature>](<area>/<Feature>/spec.md) | <area> | <Feature or —> | <bytes> | <bytes> | planned |
```

## Rules

- Plan only the features the user states or approves. Do not add features.
- Budgets are estimates. Write `?` and add an open question if you cannot estimate one.
- When a feature is merged, delete its folder and set its index row to `done`. The code and its documentation
  replace the spec. Do not keep a spec of shipped code.
- Follow the *Memory*, *Interfaces & errors* and *Optimisation* rules when you specify interfaces.
