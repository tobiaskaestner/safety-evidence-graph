---
normative: true
references:
- type: file
  path: tests/test_scheduler.py
---
A thread holding the scheduler lock is not preempted by a higher-priority ready
thread for the duration of the lock (scheduler lock preemption test passes).
