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
      output += self.get_divider(inv, i)
    output += self.get_divider(inv, inv.height)
      
  def get_divider(self, inv, y):
    divider = ''
    
    if not (y == inv.select_y or y+1 == inv.select_y):
      return " " * ((4*inv.width)+1)

    for i in range(inv.width):
      if i == inv.select_x:
        divider += '+---'
      elif i-1 == inv.select_x:
        divider += "+   "

    if i == inv.select_x:
      divider += "+\n"
    else:
      divider += " \n"

    return divider

    


class Inventory:

  def __init__(self, width, height):
    self.empty_item = Item("", 0, 0, ["   ","   "])

    self.contents = []

    for i in range(height):
      col = []
      for j in range(width):
        col.append(self.empty_item)
      self.contents.append(col)

    self.w = width
    self.h = height

    self.select_x = 0
    self.select_y = 0

  def add(self, item):
    if isinstance(item, Item) or isinstance(item, Bundle):
      self.contents.append(item)

class Bundle:

  symbol =  [" & ","|_|"] 

  def __init__(self, contents_in = []):
    self.name = "Bundle"
    self.contents = contents_in
    self.selected = 0
    self.max_stack = 64


class Item:

  def __init__(self, name_in, count_in, max_in, symbol_in):
    self.name = name_in
    self.count = count_in
    self.max_stack = max_in
    self.symbol = symbol_in

class Game:

  def __init__(self):

    self.inv = self.init_inventory()

  def init_inventory(self):
    inv = Inventory(9, 4)

    inv.add(Bundle())
    inv.add(Item("Wood Plank", 20, 64, ["===","==="]))

    return inv