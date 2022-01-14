package com.test.hserver.bean;

public class World implements Comparable<World> {

  private int id;

  private int randomNumber;

  public World(int id, int randomNumber) {
    this.id = id;
    this.randomNumber = randomNumber;
  }

  public int getId() {
    return id;
  }

  public int getRandomNumber() {
    return randomNumber;
  }

  @Override public int compareTo(World o) {
    return id - o.id;
  }


  public int getId() {
    return id;
  }

  public String getMessage() {
    return message;
  }
}