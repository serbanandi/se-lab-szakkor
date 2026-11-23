package hu.bme.mit.spaceship;

import java.time.Clock;
import java.util.ArrayList;
import java.util.List;

/**
* The four lasers of a ship, numbered 0 to 3.
*
* <ul>
* <li>Heat: every laser starts at heat 0. Heat is always between 0 and 100; values outside are clamped.</li>
* <li>Lockout: a laser locks when firing raises its heat to 90 or more, and unlocks
*     only after it has cooled below 30. A locked laser cannot fire.</li>
* <li>Cooling: every laser, locked or not, loses 7 heat per full second elapsed.
*     Parts of a second don't cool yet, but they are not lost: they count towards the next full second.
*     If the clock goes backwards, nothing cools until it passes the last second already counted.</li>
* <li>Order: lasers fire in round-robin order (0, 1, 2, 3, 0, ...), starting with laser 0.
*     The next one in line is the one after the last laser fired; locked lasers are skipped.</li>
* <li>Energy: every laser fired costs 10 energy units.</li>
* </ul>
*/
public class LaserBank {

  public static final int LASERS = 4;

  private static final int MAX_HEAT = 100;
  private static final int LOCK_AT = 90;
  private static final int UNLOCK_BELOW = 30;
  private static final int COOLING_PER_SECOND = 7;
  private static final int ENERGY_PER_LASER = 10;

  private final PowerCore core;
  private final Clock clock;

  private final int[] heat = new int[LASERS];
  private final boolean[] locked = new boolean[LASERS];
  private int next = 0;
  private long cooledUntil; // milliseconds

  public LaserBank(PowerCore core, Clock clock) {
    this.core = core;
    this.clock = clock;
    this.cooledUntil = clock.millis();
  }

  /**
  * Fires lasers.
  *
  * @param firingMode
  * 	SINGLE: fires the next unlocked laser, if there is energy for it. Adds 25 heat to it.
  * 	ALL:	fires as many unlocked lasers as the available energy allows, in round-robin order.
  * 			Adds 15 heat to each laser fired.
  *
  * The energy of all the lasers to fire is reserved with one call of {@link PowerCore#draw} before firing.
  * If the core refuses it, no laser fires and nothing heats up or moves on in the order.
  * If there is no laser to fire, draw is not called.
  *
  * @return the number of lasers fired
  */
  public int fire(FiringMode firingMode) {
    coolDown();

    boolean single = firingMode == FiringMode.SINGLE;
    List<Integer> chosen = chooseLasers(single ? 1 : LASERS);
    if (chosen.isEmpty() || !core.draw(chosen.size() * ENERGY_PER_LASER)) {
      return 0;
    }

    for (int laser : chosen) {
      heatUp(laser, single ? 25 : 15);
      next = (laser + 1) % LASERS;
    }
    return chosen.size();
  }

  /**
  * @param laser number of the laser
  * @return the current heat of the laser
  */
  public int getHeat(int laser) {
    coolDown();
    return heat[laser];
  }

  /**
  * @param laser number of the laser
  * @return whether the laser is currently locked
  */
  public boolean isLocked(int laser) {
    coolDown();
    return locked[laser];
  }

  private List<Integer> chooseLasers(int limit) {
    int affordable = Math.min(limit, core.available() / ENERGY_PER_LASER);
    List<Integer> chosen = new ArrayList<>();
    for (int i = 0; i < LASERS && chosen.size() < affordable; i++) {
      int laser = (next + i) % LASERS;
      if (!locked[laser]) {
        chosen.add(laser);
      }
    }
    return chosen;
  }

  private void heatUp(int laser, int amount) {
    heat[laser] += amount;
    if (heat[laser] > MAX_HEAT) {
      heat[laser] = MAX_HEAT;
    }
    if (heat[laser] >= LOCK_AT) {
      locked[laser] = true;
    }
  }

  private void coolDown() {
    long seconds = (clock.millis() - cooledUntil) / 1000;
    if (seconds <= 0) {
      return;
    }
    cooledUntil += seconds * 1000;

    for (int i = 0; i < LASERS; i++) {
      long cooled = heat[i] - seconds * COOLING_PER_SECOND;
      heat[i] = cooled < 0 ? 0 : (int) cooled;
      if (heat[i] < UNLOCK_BELOW) {
        locked[i] = false;
      }
    }
  }
}
