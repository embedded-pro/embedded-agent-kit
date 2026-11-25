---
name: roadmap-planner
description: Turn the features a user states for an embedded product into roadmap/ — a milestone index and one spec per pull request, with flash, RAM, cycle and power budgets, risk-rated corner cases and acceptance tests. Use to start a new project or to plan the next features of an existing one.
---

Write `roadmap/` from the features the user states. Do not write production code or tests.

## Steps

1. Read AGENTS.md *Domain* and *Build*. Read `roadmap/` if it exists. If it has its own format
   (for example `roadmap/DEPLOYMENT.md`), follow that format, not this one.
2. Existing project: read the source tree, the design document and the open issues.
   Mark features that exist as done. Do not plan them again.
3. Ask the user for each item that is missing or ambiguous. Ask in one batch:
   - target MCU or board: core, clock, flash, RAM, RTOS or bare metal;
   - power source: mains, or battery with capacity and required life;
   - the features, each with its trigger, its result and its timing limit;
   - the external interfaces: peripherals, buses, protocols, host tools;
   - the order of priority and the first milestone.
4. Split each feature into specs. See *Pull requests*.
5. Write one `roadmap/<area>/<Feature>/spec.md` per spec, in the *Spec* format. `<area>` is a
   source folder or subsystem, for example `drivers`, `protocol`, `app`.
6. Find the corner cases of each spec. Rate each one. See *Risk*.
7. Write `roadmap/README.md` in the *Index* format. Order the specs so each one follows the specs it depends on.
8. Check:
   - each dependency is in the index;
   - the flash and RAM totals are less than the target's;
   - the cycles of each periodic spec fit its period, and the total load is less than 70 %;
   - battery target: the average current gives the required life;
   - each spec has at least one acceptance test, and each high or medium risk has a test.
9. Report the changed files, the open questions, the budget totals and each high risk.

## Pull requests

- One spec is one pull request. Never plan a spec that needs more than one.
- A spec has one behaviour, is testable on the host and changes about 400 lines or less, tests included.
- Split a larger feature into ordered specs, for example: interface and fake, driver, protocol, application.
  Each spec builds and passes its tests alone.
- Name split specs `<Feature><Part>`, for example `FlashLogErase`, `FlashLogWrite`.

## Budgets

- Cycles: worst-case cycles per call, and the call rate. Estimate from the operation count or a similar function.
  Cycles do not change with the clock; time = cycles / clock.
- Power: only on a battery target. Give the active current, the active time per period and the sleep mode.
  Average current = active current × duty cycle + sleep current × (1 − duty cycle).
- All budgets are estimates. Write `?` and add an open question if you cannot estimate one.
- Mark a budget `measured` only after `feature-implementer` measures it.

## Risk

A corner case is a condition that is rare or needs several conditions at the same time,
for example a brown-out during a flash write, or a bus error during a buffer wrap.

Rate each corner case:

| Likelihood | Meaning |
|---|---|
| frequent | expected each day of operation |
| occasional | expected in the product life |
| rare | needs two or more independent conditions at the same time |

| Severity | Meaning |
|---|---|
| critical | harm to people, damage to hardware or lost or corrupted persistent data |
| major | function lost until a reset or a service action |
| minor | degraded function that recovers by itself |

| Likelihood ↓ / Severity → | critical | major | minor |
|---|---|---|---|
| frequent | high | high | medium |
| occasional | high | medium | low |
| rare | medium | low | low |

Treatment:

- high: change the design to remove it or to make it detectable. Add a host test.
  Add an on-target test if the host cannot show it.
- medium: add a host test, or an on-target test if the host cannot show it.
- low: write the reason it is accepted. The user must approve each accepted risk.

## Spec

```markdown
# <Feature>

<One sentence: what the feature does and for whom.>

## Behaviour
- <Trigger → result. One bullet per behaviour.>

## Interfaces
- <New or changed interface: name, methods, direction. Hardware: peripheral, pins, bus speed.>

## Budget
| Flash | RAM | Worst-case cycles | Rate | Context | Active current | Duty cycle |
|---|---|---|---|---|---|---|
| <bytes> | <bytes> | <cycles> | <Hz or per event> | <ISR, task, main loop> | <mA or n/a> | <% or n/a> |

## Corner cases
| Case | Conditions | Likelihood | Severity | Risk | Treatment |
|---|---|---|---|---|---|
| <case> | <what must happen together> | <frequent, occasional, rare> | <critical, major, minor> | <high, medium, low> | <design change, test, or accepted: reason> |

## Dependencies
- <Other spec, or none.>

## Acceptance tests
- <Host test: given, when, then. One bullet per behaviour and per high or medium risk.>
- <On-target test, only when the host cannot show the behaviour.>
```

## Index

```markdown
# Roadmap

Target: <MCU/board>, <core> at <clock>, <flash> flash, <RAM> RAM, <RTOS or bare metal>, <mains or battery and life>.

## <Milestone>
| Spec | Area | Depends on | Flash | RAM | Load | Avg current | High risks | Status |
|---|---|---|---|---|---|---|---|---|
| [<Spec>](<area>/<Spec>/spec.md) | <area> | <Spec or —> | <bytes> | <bytes> | <%> | <µA or n/a> | <n> | planned |

Totals: <flash>, <RAM>, <load %>, <average current> → <battery life>.
```

## Rules

- Plan only the features the user states or approves. Do not add features.
- When a spec is merged, delete its folder and set its index row to `done`. The code and its documentation
  replace the spec. Do not keep a spec of shipped code.
- Follow the *Memory*, *Interfaces & errors* and *Optimisation* rules when you specify interfaces.
