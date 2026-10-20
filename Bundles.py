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

    for i in range(len(inv.contents)): # HERE
      output += self.get_divider(inv, i)
      output += self.get_item_rows(inv.contents, i)
      output += self.get_item_count_row(inv.contents, i)

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
  
  def get_item_rows(self, contents, i):
    item_rows = "|"

    for item in contents[i]:
      item_rows += item.symbol[0] + "|"

    item_rows += "\n|"

    for item in contents[i]:
      item_rows += item.symbol[1] + "|"

    return item_rows
  

  def get_item_count_row(self, contents, i):
    count_row = "|"

    for item in contents[i]:
      count_str = str(item.count)
      count_row += (" " * (3 - len(count_str))) + count_str + "|"

    return count_row 


class Inventory:

  def __init__(self, w, h):
    self.width = w
    self.height = h
    
    self.contents = []

    for i in range(self.height):
      row = []
      for j in range(self.width):
        row.append(Item("", 0, 0, ["   ","   "]))
      self.contents.append(row)

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
    self.display = Display()

  def init_inventory(self):
    inv = Inventory(9, 4)

    inv.add(Item("Wood Plank", 20, 64, ["===","==="]))

    return inv
  
  def run(self):
    self.display.render(self.inv)

game = Game()
game.run()