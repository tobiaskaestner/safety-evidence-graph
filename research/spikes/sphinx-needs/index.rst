SEG sphinx-needs Spike
======================

.. sys:: Deterministic scheduling
   :id: SYS001

   The kernel SHALL provide deterministic thread scheduling under all load
   conditions.

.. req:: Scheduler lock
   :id: REQ001
   :status: Approved
   :refines: SYS001

   While a thread holds the scheduler lock, the kernel SHALL NOT preempt it.

.. adr:: Use cooperative locking, not IRQ masking
   :id: ADR001
   :status: proposed
   :answers: REQ001

   Scheduler locking is implemented via a cooperative lock counter rather than
   masking interrupts, to keep ISR latency bounded.

.. impl:: k_sched_lock
   :id: IMPL001
   :implements: REQ001
   :adheres: ADR001

   Implementation of the scheduler lock primitive.

.. tst:: Scheduler lock preemption test
   :id: TST001
   :verifies: REQ001

   Verify that a thread holding the scheduler lock is not preempted by a
   higher-priority ready thread for the duration of the lock.
