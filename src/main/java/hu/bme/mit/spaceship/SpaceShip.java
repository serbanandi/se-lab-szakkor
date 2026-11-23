package hu.bme.mit.spaceship;

/**
* Defines basic spaceship functionality
* (collects just the most important ones currently)
*/
public interface SpaceShip {

  /**
  * Fires the laser or lasers of the ship
  *
  * @param firingMode how many lasers to fire
  * @return the number of lasers fired
  */
  public int fireLaser(FiringMode firingMode);

  /**
  * Fires the torpedo stores of the ship
  *
  * @param firingMode how many torpedo stores to fire
  * @return whether the fire command was successful
  */
  public boolean fireTorpedo(FiringMode firingMode);
}
