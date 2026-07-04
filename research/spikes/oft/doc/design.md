# Design Decisions (ADR analogue)

### Use cooperative locking, not IRQ masking
`dsn~cooperative-locking~1`
Status: approved

Scheduler locking is implemented via a cooperative lock counter rather than
masking interrupts, to keep ISR latency bounded.

Covers:
- req~scheduler-lock~1

Needs: impl
