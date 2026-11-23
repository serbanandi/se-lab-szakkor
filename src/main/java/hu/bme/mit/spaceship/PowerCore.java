package hu.bme.mit.spaceship;

/**
* Energy source shared by the systems of the ship
*/
public interface PowerCore {

  /**
  * @return the energy units currently available
  */
  int available();

  /**
  * Reserves energy: either the whole amount or nothing.
  *
  * @param amount energy units to reserve
  * @return whether the energy was reserved
  */
  boolean draw(int amount);
}
