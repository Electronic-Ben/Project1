import math

# import curses library to comtrol terminal
import curses
from curses import wrapper

# Display class: in charge of rendering 
class Display:

  # No member varriables
  def __init__(self):
    pass

  # render function draws inventory to standard screen (stdscr) using curses addstr()
  def render(self, stdscr, inv):
    inv_display = self.get_inventory_display(inv)
    for i, line in enumerate(inv_display):
      stdscr.addstr(i + inv.y, inv.x, line)

    stdscr.addstr(len(inv_display) + inv.y, 0, "Selected Slot: " + inv.contents[inv.select_y][inv.select_x].name + (" " * 20))
    stdscr.addstr(len(inv_display) + inv.y + 1, 0, "Holding: " + inv.mouse_hold.name + (" " * 20))
    
    # draw a floating item at the mouse if it is holding an item
    if not inv.mouse_hold.is_empty():
      item_width = len(inv.mouse_hold.symbol[0])
      item_height = 3

      inv_left = inv.x + 1
      inv_right = inv.x + inv.width * (inv.cell_width + 1)
      inv_top = inv.y + 1
      inv_bottom = inv.y + inv.height * 4

      draw_x = inv.mx - 2
      draw_y = inv.my - 1

      # clamp drawing to inv bounds
      draw_x = max(inv_left, min(draw_x, inv_right - item_width))
      draw_y = max(inv_top, min(draw_y, inv_bottom - item_height))

      stdscr.addstr(draw_y, draw_x, inv.mouse_hold.symbol[0])
      stdscr.addstr(draw_y + 1, draw_x, inv.mouse_hold.symbol[1])
      stdscr.addstr(draw_y + 2, draw_x, inv.mouse_hold.get_count_str())

    # push changes to the screen
    stdscr.refresh()

  # get a list of lines to represent the inventory
  def get_inventory_display(self, inv):
    output = []

    for i in range(len(inv.contents)):
      output.append(self.get_divider(inv, i))
      output.append(self.get_item_row1(inv.contents, i))
      output.append(self.get_item_row2(inv.contents, i))
      output.append(self.get_item_count_row(inv.contents, i))

    output.append(self.get_divider(inv, inv.height))

    return output
      
  # get the line between inventory spaces, highlight the selected slot
  def get_divider(self, inv, y):
    divider = ''

    bar = "-" * (inv.cell_width)

    right_sec = "/" + bar
    left_sec = "\\" + bar
    norm_sec = "+" + bar

    if not (y == inv.select_y or y == inv.select_y + 1):
      return (norm_sec * inv.width) + norm_sec[0]
    
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
      divider += left_sec[0]
    else:
      divider += "+"

    return divider
  
  # get a string that is the top item row using the contents of the inventory and the y position
  def get_item_row1(self, contents, i):
    row = "|"

    for item in contents[i]:
      row += item.symbol[0] + "|"

    return row

  # get a string that is the bottom item row using the contents of the inventory and the y position
  def get_item_row2(self, contents, i):
    row = "|"

    for item in contents[i]:
      row += item.symbol[1] + "|"

    return row
  
  # get a string that is the row holding the number of items in each stack
  def get_item_count_row(self, contents, i):
    count_row = "|"

    for item in contents[i]:
      count_row += item.get_count_str() + "|"

    count_row += "\n"

    return count_row 

# Inventory class: in charge of managing the items in the inventory
class Inventory:

  # member varriables are position, size, cell size, and internal item storage
  def __init__(self, x_in, y_in, w, h, cell_w):
    self.x = x_in
    self.y = y_in

    self.width = w
    self.height = h

    self.mx = 0
    self.my = 0

    self.cell_width = cell_w
    
    self.contents = []
    self.mouse_hold = Item()

    # inventory starts filled with "empty" items
    for i in range(self.height):
      row = []
      for j in range(self.width):
        row.append(Item())
      self.contents.append(row)

    self.select_x = 0
    self.select_y = 0

  # add an item to the inventory only if it is and item and the inventory is not full
  def add(self, item):
    if isinstance(item, Item):
      x, y = self.get_next_open()
      if x != -1:
        self.contents[y][x] = item

  # get the next open slot in the inventory to add to it easily
  def get_next_open(self):
    for y, row in enumerate(self.contents):
      for x, item in enumerate(row):
        if item.is_empty():
          return x, y
    return -1, -1

  # set the selected slot (select_x, select_y) based on mouse position provided by curses
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

  # change inventory state and mouse_hold when user left clicks
  # various combinations of empty, item, and bundle are checked for inventory and mouse_hold to determine output
  def left_select(self):
    inv_item = self.contents[self.select_y][self.select_x]

    # add item to bundle if bundle is selected, destroy added item if count == 0 
    if inv_item.is_bundle():
      if inv_item.add(self.mouse_hold):
        self.mouse_hold = Item()
        return
    elif self.mouse_hold.is_bundle():
      if self.mouse_hold.add(inv_item):
        self.contents[self.select_y][self.select_x] = Item()
        return

    # combine simular item stacks, destroying empty stacks if needed
    if inv_item.name == self.mouse_hold.name and inv_item.count != inv_item.max_stack and not inv_item.is_bundle():
      if inv_item.combine(self.mouse_hold):
        self.mouse_hold = Item()
        return

    # swap items if no other effect happens
    temp = self.mouse_hold
    self.mouse_hold = inv_item
    self.contents[self.select_y][self.select_x] = temp

  # same as left select, some different functionality with bundles
  def right_select(self):
    inv_item = self.contents[self.select_y][self.select_x]

    # drop item from bundle if holding it over an empty slot
    if self.mouse_hold.is_bundle() and inv_item.is_empty():
      dropped = self.mouse_hold.drop_item(0)
      if dropped:
        self.contents[self.select_y][self.select_x] = dropped
        return

    # take item from bundle if mouse is empty
    if inv_item.is_bundle() and self.mouse_hold.is_empty():
      dropped = inv_item.drop_item(0)
      if dropped:
        self.mouse_hold = dropped
        return

    # combine stacks
    if inv_item.name == self.mouse_hold.name and inv_item.count != inv_item.max_stack and not inv_item.is_bundle():
      if inv_item.combine(self.mouse_hold):
        self.mouse_hold = Item()
      return

    # split stacks
    if self.mouse_hold.is_empty() and (not inv_item.is_empty()) and (not inv_item.is_bundle()):
      new_item_count = math.floor(inv_item.count / 2)
      if new_item_count > 0:
        inv_item.remove(new_item_count)
        self.mouse_hold = Item(inv_item.name, new_item_count, inv_item.max_stack, inv_item.value, inv_item.symbol)
        return

    # swap if no other actions trigger
    temp = self.mouse_hold
    self.mouse_hold = inv_item
    self.contents[self.select_y][self.select_x] = temp

  
# item class: represents item stack
class Item:

  # class varriables are name, number of items, max stack, item symbol, and value
  def __init__(self, name_in = "", count_in = 0, max_in = 0, val = 1, symbol_in = ["     ", "     "]):
    self.name = name_in
    self.count = count_in
    self.max_stack = max_in
    self.symbol = symbol_in
    self.value = val

  # empty items have max_stack == 0
  def is_empty(self):
    return self.max_stack == 0

  # get the string to represent the count
  def get_count_str(self):
    count_str = str(self.count) if self.count > 0 else ""
    return (" " * (len(self.symbol[0]) - len(count_str) - 1)) + count_str + " "

  # check if an item is a bundle 
  def is_bundle(self):
    return False

  def add(self, x):
    if x + self.count <= self.max_stack:
      self.count += x
      return True
    return False

  def remove(self, x):
    if self.count - x >= 0:
      self.count -= x
      return True
    return False

  def combine(self, other):
    max_add = min(self.max_stack - self.count, other.count)
    self.add(max_add)
    other.remove(max_add)
    return other.count == 0


class Bundle(Item):

  def __init__(self, contents_in = []):
    super().__init__("Bundle", 0, 64, 64, ["  &  "," |_| "])
    
    self.selected = 0
    self.contents = contents_in

  def get_count_str(self):
    return (" " if self.count < 10 else "") + str(self.count) + "/" + str(self.max_stack)

  def is_bundle(self):
    return True

  def add(self, item):
    if not item.is_empty():
      bundle_space = math.floor((self.max_stack - self.count) / item.value)
      if bundle_space <= 0:
        return False
      amount = min(bundle_space, item.count)
      for c in self.contents:
        if c.name == item.name:
          
          item_space = c.max_stack - c.count
          amount = min(amount, item_space)

          c.add(amount)
          item.remove(amount)
          self.count += amount * item.value

          return item.count == 0
          
      if self.count < self.max_stack and not item.is_bundle():
        self.contents.insert(0, Item(item.name, amount, item.max_stack, item.value, item.symbol))
        self.count += amount * item.value
        item.remove(amount)
        return item.count == 0
        
    return False

  def drop_item(self, index):
    if len(self.contents) > index:
      self.count -= self.contents[index].count * self.contents[index].value
      return self.contents.pop(index)
    return False


class Game:

  def __init__(self, std_screen):
    self.inv = self.init_inventory()
    self.display = Display()
    self.stdscr = std_screen
    self.right_dragging = False

    curses.curs_set(0)
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

  def init_inventory(self):
    inv = Inventory(0, 0, 9, 3, 5)
    
    inv.add(Item("Wood Plank", 20, 64, 1, [" === "," === "]))
    inv.add(Item("Wood Plank", 32, 64, 1, [" === "," === "]))
    inv.add(Item("Diamond", 10, 64, 1, [" /‾\\ "," \\_/ "]))
    inv.add(Item("Wood Plank", 54, 64, 1, [" === "," === "]))
    inv.add(Item("Iron Ingot", 23, 64, 1, ["  /‾/"," /_/ "]))
    inv.add(Item("Torch", 63, 64, 1, ["  o  ","  |  "]))
    inv.add(Item("Firework Rockets", 44, 64, 1, ["  /\\ ","  || "]))
    inv.add(Item("Empty Bucket", 7, 16, 4, [" | | "," \\_/ "]))
    inv.add(Item("Elytra", 1, 1, 64, ["/‾V‾\\","|/ \\|"]))

    inv.add(Bundle())
    inv.add(Bundle())
    inv.add(Bundle())

    return inv
  
  def run(self):
    self.stdscr.clear()
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

          if bstate & curses.BUTTON1_PRESSED or bstate & curses.BUTTON1_CLICKED:
            self.inv.left_select()
          elif bstate & curses.BUTTON1_RELEASED and not self.inv.mouse_hold.is_empty():
            self.inv.left_select()

          if bstate & curses.BUTTON3_PRESSED:
            self.right_dragging = True
          elif bstate & curses.BUTTON3_RELEASED:
            if self.right_dragging:
              self.inv.right_select()
            self.right_dragging = False
          elif bstate & curses.BUTTON3_CLICKED:
            self.inv.right_select()

        except curses.error:
          pass

        self.display.render(self.stdscr, self.inv)

  def end(self):
    curses.curs_set(1)
    curses.mousemask(0)

def main(stdscr):
  game = Game(stdscr)
  game.run()
  game.end()

wrapper(main)

