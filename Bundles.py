import random
import os

class Display:

  def __init__(self):
    pass

  def render(self, inv):
    self.render_inventory(inv) #HERE
    self.render_bundle_tooltip()

  def render_inventory(self, inv):
    output = ""

    for i, item in enumerate(inv.contents):
      

class Inventory:

  def __init__(self, width, height):
    self.contents = []
    self.w = width
    self.h = height

  def add(self, item):
    if isinstance(item, Item) or isinstance(item, Bundle):
      self.contents.append(item)

class Bundle:

  symbol =  [" & ","|_|"] 

  def __init__(self, contents_in = []):
    self.name = "Bundle"
    self.contents = contents_in
    self.selected = 0


class Item:

  def __init__(self, name_in, count_in, max_in, symbol_in):
    self.name = name_in
    self.count = count_in
    self.max = max_in
    self.symbol = symbol_in

class Game:

  def __init__(self):
    self.inv = self.init_inventory()

  def init_inventory(self):
    inv = Inventory(9, 4)
    self.inv.add(Bundle())
    self.inv.add(Item("Wood Plank", 20, 64, ["===","==="]))
