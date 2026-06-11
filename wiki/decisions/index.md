# Decisions

Status: active
Last reviewed: YYYY-MM-DD

Use ADRs for durable decisions that constrain future implementation.

ADR files live under `wiki/decisions/<zone>/` (a product namespace, `platform`, or `general`), chosen with the implementation-sharing boundary rule from [CONCEPT.md](../../CONCEPT.md). ADR numbers are global across all zones — pick the next number as max existing in `wiki/decisions/*/adr-*.md` + 1. Each ADR carries a `Namespace:` field matching its zone.

## ADRs

Group entries by zone as ADRs accumulate.

### General

| ADR | Status | Title |
|---|---|---|
| [Template](adr-template.md) | template | ADR template |

### Platform

| ADR | Status | Title |
|---|---|---|

## When To Create An ADR

Create or update an ADR when a choice affects:

- architecture boundaries
- data ownership
- infrastructure or deployment strategy
- major dependencies
- security or privacy posture
- long-lived product or engineering constraints
- cross-repo contracts
