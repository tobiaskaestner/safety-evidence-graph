# Test Specifications

### Scheduler lock preemption test
`utest~scheduler-lock-test~1`

Verify that a thread holding the scheduler lock is not preempted by a
higher-priority ready thread for the duration of the lock.

Covers:
- req~scheduler-lock~1
