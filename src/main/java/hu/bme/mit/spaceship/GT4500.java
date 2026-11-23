package hu.bme.mit.spaceship;

import java.time.Clock;
import java.util.ArrayList;
import java.util.List;

/**
* A simple spaceship with two proton torpedo stores and four lasers
*/
public class GT4500 implements SpaceShip {

  private static final int LASER_COUNT = 4;
  private static final int MAX_HEAT = 100;
  private static final int LOCK_AT = 90;
  private static final int UNLOCK_BELOW = 30;
  private static final int COOLING_PER_SECOND = 7;
  private static final int ENERGY_PER_LASER = 10;

  private TorpedoStore primaryTorpedoStore;
  private TorpedoStore secondaryTorpedoStore;

  private boolean wasPrimaryFiredLast = false;

  private final PowerCore core;
  private final Clock clock;

  private final int[] laserHeat = new int[LASER_COUNT];
  private final boolean[] laserLocked = new boolean[LASER_COUNT];
  private int nextLaser = 0;
  private long cooledUntil; // milliseconds

  public GT4500() {
    this(new TorpedoStore(10), new TorpedoStore(10), new Battery(1000), Clock.systemUTC());
  }

  /**
  * Creates a ship with the given parts
  * (e.g. to replace them with mocks in unit tests).
  *
  * @param primaryTorpedoStore the store fired first in SINGLE mode
  * @param secondaryTorpedoStore the other store
  * @param core supplies the energy of the lasers
  * @param clock measures the cooling time of the lasers
  */
  public GT4500(TorpedoStore primaryTorpedoStore, TorpedoStore secondaryTorpedoStore, PowerCore core, Clock clock) {
    this.primaryTorpedoStore = primaryTorpedoStore;
    this.secondaryTorpedoStore = secondaryTorpedoStore;
    this.core = core;
    this.clock = clock;
    this.cooledUntil = clock.millis();
  }

  /**
  * Tries to fire the four lasers of the ship, numbered 0 to 3.
  *
  * Heat: every laser starts at heat 0. Heat is always between 0 and 100; values outside are clamped.
  * Lockout: a laser locks when firing raises its heat to 90 or more, and unlocks
  * 			only after it has cooled below 30. A locked laser cannot fire.
  * Cooling: every laser, locked or not, loses 7 heat per full second elapsed since the ship was created.
  * 			Parts of a second don't cool yet, but they are not lost: they count towards the next full second.
  * 			If the clock goes backwards, nothing cools until it passes the last second already counted.
  * Order: lasers fire in round-robin order (0, 1, 2, 3, 0, ...), starting with laser 0.
  * 			The next one in line is the one after the last laser fired; locked lasers are skipped.
  * Energy: every laser fired costs 10 energy units.
  * 			The energy of all the lasers to fire is reserved with one call of {@link PowerCore#draw} before firing.
  * 			If the core refuses it, no laser fires and nothing heats up or moves on in the order.
  * 			If there is no laser to fire, draw is not called.
  *
  * @param firingMode how many lasers to fire
  * 	SINGLE: fires the next unlocked laser, if there is energy for it. Adds 25 heat to it.
  * 	ALL:	fires as many unlocked lasers as the available energy allows, in round-robin order.
  * 			Adds 15 heat to each laser fired.
  *
  * @return the number of lasers fired
  */
  @Override
  public int fireLaser(FiringMode firingMode) {
    coolDownLasers();

    boolean single = firingMode == FiringMode.SINGLE;
    List<Integer> chosen = chooseLasers(single ? 1 : LASER_COUNT);
    if (chosen.isEmpty() || !core.draw(chosen.size() * ENERGY_PER_LASER)) {
      return 0;
    }

    for (int laser : chosen) {
      heatUpLaser(laser, single ? 25 : 15);
      nextLaser = (laser + 1) % LASER_COUNT;
    }
    return chosen.size();
  }

  /**
  * @param laser number of the laser
  * @return the current heat of the laser
  */
  public int getLaserHeat(int laser) {
    coolDownLasers();
    return laserHeat[laser];
  }

  /**
  * @param laser number of the laser
  * @return whether the laser is currently locked
  */
  public boolean isLaserLocked(int laser) {
    coolDownLasers();
    return laserLocked[laser];
  }

  /**
  * Tries to fire the torpedo stores of the ship.
  *
  * @param firingMode how many torpedo bays to fire
  * 	SINGLE: fires only one of the bays.
  * 			- For the first time the primary store is fired.
  * 			- To give some cooling time to the torpedo stores, torpedo stores are fired alternating.
  * 			- But if the store next in line is empty, the ship tries to fire the other store.
  * 			- If the fired store reports a failure, the ship does not try to fire the other one.
  * 	ALL:	tries to fire both of the torpedo stores.
  *
  * @return whether at least one torpedo was fired successfully
  */
  @Override
  public boolean fireTorpedo(FiringMode firingMode) {

    boolean firingSuccess = false;

    switch (firingMode) {
      case SINGLE:
        if (wasPrimaryFiredLast) {
          // try to fire the secondary first
          if (! secondaryTorpedoStore.isEmpty()) {
            firingSuccess = secondaryTorpedoStore.fire(1);
            wasPrimaryFiredLast = false;
          }
          else {
            // although primary was fired last time, but the secondary is empty
            // thus try to fire primary again
            if (! primaryTorpedoStore.isEmpty()) {
              firingSuccess = primaryTorpedoStore.fire(1);
              wasPrimaryFiredLast = true;
            }

            // if both of the stores are empty, nothing can be done, return failure
          }
        }
        else {
          // try to fire the primary first
          if (! primaryTorpedoStore.isEmpty()) {
            firingSuccess = primaryTorpedoStore.fire(1);
            wasPrimaryFiredLast = true;
          }
          else {
            // although secondary was fired last time, but primary is empty
            // thus try to fire secondary again
            if (! secondaryTorpedoStore.isEmpty()) {
              firingSuccess = secondaryTorpedoStore.fire(1);
              wasPrimaryFiredLast = false;
            }

            // if both of the stores are empty, nothing can be done, return failure
          }
        }
        break;

      case ALL:
        // try to fire both of the torpedo stores
        boolean primarySuccess = false;
        boolean secondarySuccess = false;

        if (! primaryTorpedoStore.isEmpty()) {
          primarySuccess = primaryTorpedoStore.fire(1);
        }
        if (! secondaryTorpedoStore.isEmpty()) {
          secondarySuccess = secondaryTorpedoStore.fire(1);
        }

        firingSuccess = primarySuccess || secondarySuccess;
        break;
    }

    return firingSuccess;
  }

  private List<Integer> chooseLasers(int limit) {
    int affordable = Math.min(limit, core.available() / ENERGY_PER_LASER);
    List<Integer> chosen = new ArrayList<>();
    for (int i = 0; i < LASER_COUNT && chosen.size() < affordable; i++) {
      int laser = (nextLaser + i) % LASER_COUNT;
      if (!laserLocked[laser]) {
        chosen.add(laser);
      }
    }
    return chosen;
  }

  private void heatUpLaser(int laser, int amount) {
    laserHeat[laser] += amount;
    if (laserHeat[laser] > MAX_HEAT) {
      laserHeat[laser] = MAX_HEAT;
    }
    if (laserHeat[laser] >= LOCK_AT) {
      laserLocked[laser] = true;
    }
  }

  private void coolDownLasers() {
    long seconds = (clock.millis() - cooledUntil) / 1000;
    if (seconds <= 0) {
      return;
    }
    cooledUntil += seconds * 1000;

    for (int i = 0; i < LASER_COUNT; i++) {
      long cooled = laserHeat[i] - seconds * COOLING_PER_SECOND;
      laserHeat[i] = cooled < 0 ? 0 : (int) cooled;
      if (laserHeat[i] < UNLOCK_BELOW) {
        laserLocked[i] = false;
      }
    }
  }

}
