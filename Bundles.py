import random
import sys
import math

import curses
from curses import wrapper

class Display:

  def __init__(self):
    pass

  def render(self, stdscr, inv):
    inv_display = self.get_inventory_display(inv)
    for i, line in enumerate(inv_display):
      stdscr.addstr(i + inv.y, inv.x, line)

    if inv.mouse_hold.max_stack != 0:
      stdscr.addstr(inv.my, inv.mx - 1, inv.mouse_hold.symbol[0])
      stdscr.addstr(inv.my + 1, inv.mx - 1, inv.mouse_hold.symbol[1])

    # self.render_bundle_tooltip()
    stdscr.refresh()

  def get_inventory_display(self, inv):
    output = []

    for i in range(len(inv.contents)):
      output.append(self.get_divider(inv, i))
      output.append(self.get_item_row1(inv.contents, i))
      output.append(self.get_item_row2(inv.contents, i))
      output.append(self.get_item_count_row(inv.contents, i))

    output.append(self.get_divider(inv, inv.height))

    return output
      
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
  
  def get_item_row1(self, contents, i):
    row = "|"

    for item in contents[i]:
      row += item.symbol[0] + "|"

    return row

  def get_item_row2(self, contents, i):
    row = "|"

    for item in contents[i]:
      row += item.symbol[1] + "|"

    return row
  

  def get_item_count_row(self, contents, i):
    count_row = "|"

    for item in contents[i]:
      count_str = str(item.count) if item.count > 0 else ""
      count_row += (" " * (len(item.symbol[0]) - len(count_str))) + count_str + "|"

    count_row += "\n"

    return count_row 


class Inventory:

  def __init__(self, x_in, y_in, w, h, cell_w):
    self.x = x_in
    self.y = y_in

    self.width = w
    self.height = h

    self.mx = 0
    self.my = 0

    self.cell_width = cell_w
    
    self.contents = []
    self.mouse_hold = Item("", 0, 0, ["     ","     "])

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

  def set_selected(self, mx, my):
    mouse_x = mx - self.x
    mouse_y = my - self.y

    cw = self.cell_width + 1
    ch = 4

    cell_x = mouse_x // cw
    cell_y = mouse_y // ch

    if 0 <= cell_x < self.width:
      self.select_x = cell_x

    if 0 <= cell_y < self.height:
      self.select_y = cell_y

    self.mx = mx
    self.my = my

  def select(self):
    temp = self.mouse_hold
    self.mouse_hold = self.contents[self.select_y][self.select_x]
    self.contents[self.select_y][self.select_x] = temp

  

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
    self.display = Display()
    self.stdscr = std_screen

    curses.mousemask(curses.ALL_MOUSE_EVENTS)

  def init_inventory(self):
    inv = Inventory(0, 0, 9, 3, 5)

    for i in range(4):
      inv.add(Item("Wood Plank", 20, 64, [" === "," === "]))

    inv.add(Bundle())

    return inv
  
  def run(self):
    self.display.render(self.stdscr, self.inv)

    while True:
      key = self.stdscr.getch()

      # q key to quit
      if key == ord('q'):
        break

      if key == curses.KEY_MOUSE:
        try:
          _, mx, my, _, bstate = curses.getmouse()

          self.inv.set_selected(mx, my)

          if bstate & curses.BUTTON1_PRESSED and self.inv.mouse_hold.max_stack == 0:
            self.inv.select()

          if bstate & curses.BUTTON1_RELEASED and self.inv.mouse_hold.max_stack != 0:
            self.inv.select()
          

        except curses.error:
          pass

        self.display.render(self.stdscr, self.inv)

      

      

  def end(self):
    curses.mousemask(0)


def main(stdscr):
  game = Game(stdscr)
  game.run()
  game.end()

wrapper(main)

