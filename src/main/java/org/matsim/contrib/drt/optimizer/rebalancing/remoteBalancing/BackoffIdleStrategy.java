package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import java.util.concurrent.locks.LockSupport;

/**
 * Parks the threads with increasing number of nanoseconds.
 */
final class BackoffIdleStrategy {

	/**
	 * Default minimum interval the strategy will park a thread.
	 */
	public static final long DEFAULT_MIN_PARK_PERIOD_NS = 1000L;
	/**
	 * Default maximum interval the strategy will park a thread.
	 */
	public static final long DEFAULT_MAX_PARK_PERIOD_NS = 1_000_000L;

	/**
	 * Park period in nanoseconds.
	 */
	private long parkPeriodNs;


	/**
	 * Perform idle operation.
	 */
	void idle() {
		LockSupport.parkNanos(parkPeriodNs);
		parkPeriodNs = Math.min(parkPeriodNs << 1, DEFAULT_MAX_PARK_PERIOD_NS);
	}

	/**
	 * Reset idling state.
	 */
	void reset() {
		parkPeriodNs = DEFAULT_MIN_PARK_PERIOD_NS;
	}

}
