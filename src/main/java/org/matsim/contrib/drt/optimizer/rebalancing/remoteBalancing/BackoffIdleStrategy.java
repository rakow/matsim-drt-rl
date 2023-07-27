package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import java.util.concurrent.locks.LockSupport;

/**
 * Adapted from <a href="https://github.com/real-logic/agrona/blob/master/agrona/src/main/java/org/agrona/concurrent/BackoffIdleStrategy.java">...</a>
 */
final class BackoffIdleStrategy {

	/**
	 * Default number of times the strategy will yield without work before going to next state.
	 */
	public static final long DEFAULT_MAX_YIELDS = 15L;
	/**
	 * Default minimum interval the strategy will park a thread.
	 */
	public static final long DEFAULT_MIN_PARK_PERIOD_NS = 1000L;
	/**
	 * Default maximum interval the strategy will park a thread.
	 */
	public static final long DEFAULT_MAX_PARK_PERIOD_NS = 1_000_000L;
	/**
	 * Denotes a non-idle state.
	 */
	private static final int NOT_IDLE = 0;
	/**
	 * Denotes a yielding state.
	 */
	private static final int YIELDING = 2;
	/**
	 * Denotes a parking state.
	 */
	private static final int PARKING = 3;
	/**
	 * Current state.
	 */
	private int state = NOT_IDLE;

	/**
	 * Number of yields.
	 */
	private long yields;

	/**
	 * Park period in nanoseconds.
	 */
	private long parkPeriodNs;


	/**
	 * Perform idle operation.
	 */
	void idle() {
		switch (state) {
			case NOT_IDLE:
				state = YIELDING;
				yields++;
				break;

			case YIELDING:
				if (++yields > DEFAULT_MAX_YIELDS) {
					state = PARKING;
					parkPeriodNs = DEFAULT_MIN_PARK_PERIOD_NS;
				} else {
					Thread.yield();
				}
				break;

			case PARKING:
				LockSupport.parkNanos(parkPeriodNs);
				parkPeriodNs = Math.min(parkPeriodNs << 1, DEFAULT_MAX_PARK_PERIOD_NS);
				break;
		}
	}

	/**
	 * Reset idling state.
	 */
	public void reset() {
		yields = 0;
		parkPeriodNs = DEFAULT_MIN_PARK_PERIOD_NS;
		state = NOT_IDLE;
	}

}
