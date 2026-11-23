package hu.bme.mit.spaceship;

/**
* Simple power core with a fixed amount of energy
*/
public class Battery implements PowerCore {

  private int energy;

  public Battery(int energy) {
    this.energy = energy;
  }

  @Override
  public int available() {
    return energy;
  }

  @Override
  public boolean draw(int amount) {
    if (amount > energy) {
      return false;
    }
    energy -= amount;
    return true;
  }
}
