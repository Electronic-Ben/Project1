import random
import os

import curses
from curses import wrapper

class Display:

  def __init__(self, std_screen):
    self.stdscr = std_screen

  def render(self, inv):
    print(self.get_inventory_display(inv))
    # self.render_bundle_tooltip()

  def get_inventory_display(self, inv):
    output = ""

    for i in range(len(inv.contents)):
      output += self.get_divider(inv, i)
      output += self.get_item_rows(inv.contents, i)
      output += self.get_item_count_row(inv.contents, i)

    output += self.get_divider(inv, inv.height)

    return output #HERE
      
  def get_divider(self, inv, y):
    divider = ''

    bar = "-" * (inv.cell_width)

    right_sec = "/" + bar
    left_sec = "\\" + bar
    norm_sec = "+" + bar

    if not (y == inv.select_y or y == inv.select_y + 1):
      return (norm_sec * inv.width) + norm_sec[0] + "\n"
    
    if y == inv.select_y + 1:
      right_sec = "\\" + bar
      left_sec = "/" + bar

    for i in range(inv.width):
      if i == inv.select_x:
        divider += right_sec
      elif i-1 == inv.select_x:
        divider += left_sec
      else:
        divider += norm_sec

    if i == inv.select_x:
      divider += left_sec[0] + "\n" #HERE
    else:
      divider += "+\n"

    return divider
  
  def get_item_rows(self, contents, i):
    row1 = "|"

    for item in contents[i]:
      item_rows += item.symbol[0] + "|"

    row2 = "|"

    for item in contents[i]:
      row2 += item.symbol[1] + "|"

    return row1, row2
  

  def get_item_count_row(self, contents, i):
    count_row = "|"

    for item in contents[i]:
      count_str = str(item.count) if item.count > 0 else ""
      count_row += (" " * (len(item.symbol[0]) - len(count_str))) + count_str + "|"

    count_row += "\n"

    return count_row 


class Inventory:

  def __init__(self, w, h, cell_w):
    self.width = w
    self.height = h
    self.cell_width = cell_w
    
    self.contents = []

    for i in range(self.height):
      row = []
      for j in range(self.width):
        row.append(Item("", 0, 0, ["     ","     "]))
      self.contents.append(row)

    self.select_x = 0
    self.select_y = 0

  def add(self, item):
    if isinstance(item, Item):
      x, y = self.get_next_open()
      if x != -1:
        self.contents[y][x] = item

  
  def get_next_open(self):
    for y, row in enumerate(self.contents):
      for x, item in enumerate(row):
        if item.max_stack == 0:
          return x, y
    return -1, -1
  

class Item:

  def __init__(self, name_in, count_in, max_in, symbol_in):
    self.name = name_in
    self.count = count_in
    self.max_stack = max_in
    self.symbol = symbol_in


class Bundle(Item):

  def __init__(self, contents_in = []):
    super().__init__("Bundle", 0, 64, ["  &  "," |_| "])
    
    self.selected = 0
    self.contents = contents_in


class Game:

  def __init__(self, std_screen):

    self.inv = self.init_inventory()
    self.display = Display(std_screen)

  def init_inventory(self):
    inv = Inventory(9, 3, 5)

    for i in range(4):
      inv.add(Item("Wood Plank", 20, 64, [" === "," === "]))

    inv.add(Bundle())

    return inv
  
  def run(self):
    self.display.render(self.inv)

def main(stdscr):
  game = Game()
  game.run()
  
  
  

wrapper(main)

