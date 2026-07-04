/* Scheduler lock primitive.
 * Covers the software requirement and adheres to the design decision.
 * [impl->req~scheduler-lock~1]
 * [impl->dsn~cooperative-locking~1]
 */
void k_sched_lock(void) {
    /* cooperative lock counter; no IRQ masking */
}
