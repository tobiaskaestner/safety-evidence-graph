# Software Requirements

### Scheduler lock
`req~scheduler-lock~1`

While a thread holds the scheduler lock, the kernel shall not preempt it.

Rationale:
Preemption during critical sections would violate the timing guarantees
required by the deterministic scheduling system requirement.

Covers:
- sys~deterministic-scheduling~1

Needs: dsn, impl, utest
