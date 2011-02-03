#!/usr/bin/env python
#

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import copy
import random

import display

class Part:
    def __init__(self, masks):
        self.__masks = masks
        self.mask = self.__masks[0]
        self.__current_idx = 0

    def rotate_pos(self):
        self.__current_idx = (self.__current_idx + 1) % len(self.__masks)
        self.mask = self.__masks[self.__current_idx]
 
    def rotate_neg(self):
        self.__current_idx -= 1
        if self.__current_idx < 0:
            self.__current_idx = len(self.__masks) - 1
        self.mask = self.__masks[self.__current_idx]

class Game:
    def __init__(self, window):
        self.__win = window
        self.__board = display.Display()
        self.__board.connect_signals()
        self.__board.show()
        self.__win.connect('key-press-event', self.__press_key)
        self.__win.connect("delete-event", self.__game_quit)

        self.__win.add(self.__board)
        self.__win.present()

        self.__quit_game = False

        self.__speed = 100000
        self.__fast_down = False
        self.__in_game = []
        self.__selected = 0

        self.__parts = [
            Part([
                    [[True],
                     [True],
                     [True],
                     [True]],

                    [[True, True, True, True]]
                    ]),
            Part([
                    [[True],
                     [True],
                     [True, True]],

                    [[True, True, True],
                     [True]],

                    [[True, True],
                     [False, True],
                     [False, True]],

                    [[False, False, True],
                     [True, True, True]],
                    ]),
            Part([
                    [[False, True],
                     [False, True],
                     [True, True]],

                    [[True],
                     [True, True, True]],

                    [[True, True],
                     [True],
                     [True]],

                    [[True, True, True],
                     [False, False, True]],
                    ]),
            Part([
                    [[True, True],
                     [True, True]]
                    ]),
            Part([
                    [[True, True],
                     [False, True, True]],

                    [[False, True],
                     [True, True],
                     [True]]
                    ]),
            Part([
                    [[False, True, True],
                     [True, True]],

                    [[True],
                     [True, True],
                     [False, True]]
                    ]),
            Part([
                    [[False, True],
                     [True, True, True]],

                    [[True],
                     [True, True],
                     [True]],

                    [[True, True, True],
                     [False, True]],

                    [[False, True],
                     [True, True],
                     [False, True]]
                    ])
            ]

    def __flush_events(self):
        # GTK iteration
        while gtk.events_pending():
            gtk.main_iteration()

    def __game_quit(self, widget, event):
        self.__quit_game = True

    def __press_key(self, widget, event):
        if self.__selected < len(self.__in_game):
            part = self.__in_game[self.__selected]

            # CURSOR_DOWN
            if event.keyval == 65364:
                self.__fast_down = True

            # CURSOR_LEFT
            if event.keyval == 65361:
                if self.part_fills(part[1] - 1, part[2], part[0]):
                    self.clear_phantom_part(part[1], part[2], part[0])
                    self.put_phantom_part(part[1] - 1, part[2], part[0])
                    self.__in_game[self.__selected] = (part[0],
                                                       part[1] - 1,
                                                       part[2])
                # Update frame
                self.__win.queue_draw()

            # CURSOR_RIGHT
            if event.keyval == 65363:
                if self.part_fills(part[1] + 1, part[2], part[0]):
                    self.clear_phantom_part(part[1], part[2], part[0])
                    self.put_phantom_part(part[1] + 1, part[2], part[0])
                    self.__in_game[self.__selected] = (part[0],
                                                       part[1] + 1,
                                                       part[2])
                # Update frame
                self.__win.queue_draw()

            # CURSOR_UP
            if event.keyval == 65362:
                part[0].rotate_pos()
                if self.part_fills(part[1], part[2], part[0]):
                    part[0].rotate_neg()
                    self.clear_phantom_part(part[1], part[2], part[0])
                    part[0].rotate_pos()
                    self.put_phantom_part(part[1], part[2], part[0])
                    self.__in_game[self.__selected] = (part[0],
                                                       part[1],
                                                       part[2])
                else:
                    part[0].rotate_neg()
                    
    def part_fills(self, x, y, part):
        part_x = x
        for row in part.mask:
            part_y = y
            for position in row:
                if position:
                    if ((part_x < 0) or
                        (part_y < 0) or
                        (part_x > self.__board.width - 1) or
                        (part_y > self.__board.height - 1)):
                        return False
                    if self.__board.boxes[part_x][part_y]:
                        return False
                part_y += 1
            part_x += 1
        return True

    def put_part(self, x, y, part):
        part_x = x
        for row in part.mask:
            part_y = y
            for position in row:
                if position:
                    self.__board.boxes[part_x][part_y] = True
                part_y += 1
            part_x += 1

    def put_phantom_part(self, x, y, part):
        part_x = x
        for row in part.mask:
            part_y = y
            for position in row:
                if position:
                    self.__board.phantom[part_x][part_y] = True
                part_y += 1
            part_x += 1

    def clear_phantom_part(self, x, y, part):
        part_x = x
        for row in part.mask:
            part_y = y
            for position in row:
                if position:
                    self.__board.phantom[part_x][part_y] = False
                part_y += 1
            part_x += 1
        
    def get_me_part(self):
        return copy.copy(random.choice(self.__parts))

    def check_filled_rows(self):
        more_rows = True
        while more_rows:
            more_rows = False
            for y in range(self.__board.height - 1, -1, -1):
                filled = 0
                for x in range(self.__board.width):
                    if self.__board.boxes[x][y]:
                        filled += 1
                if filled == self.__board.width:
                    more_rows = True
                    # This line is filled!
                    if (y - 1) < 0:
                        # Special case: last row
                        for x in range(self.__board.width):
                            self.__board.boxes[x][y] = 0
                    else:
                        # Normal case: frop all rows
                        for cpx in range(self.__board.width):
                            for cpy in range(y, 0, -1):
                                self.__board.boxes[cpx][cpy] = self.__board.boxes[cpx][cpy - 1]
                            self.__board.boxes[cpx][0] = False
                    # Re-scan
                    break

    def game_loop(self):
        while not self.__quit_game:
            # Any part in game?
            if len(self.__in_game) == 0:
                # Out new part!
                part = self.get_me_part()
                self.__in_game.append((part, 5, 0))
                # No more parts fills! game over!
                if not self.part_fills(5, 0, part):                   
                    self.__quit_game = True
            # Player can move parts
            to_go = self.__speed
            self.__fast_down = False
            while ((to_go > 0) and (not self.__fast_down)):
                for part in self.__in_game:
                    self.put_phantom_part(part[1], part[2], part[0])
                to_go -= 1
                self.__flush_events()
            for part in self.__in_game:
                self.clear_phantom_part(part[1], part[2], part[0])
            # Step down!
            for part in self.__in_game:
                if not self.part_fills(part[1], part[2] + 1, part[0]):
                    # Drop!
                    self.put_part(part[1], part[2], part[0])
                    idx = self.__in_game.index(part)
                    del(self.__in_game[idx])
                else:
                    idx = self.__in_game.index(part)
                    self.__in_game[idx] = (part[0], part[1], part[2] + 1)

            # Any row filled?
            self.check_filled_rows()

            # Update frame
            self.__win.queue_draw()

if __name__ == '__main__':
    window = gtk.Window()
    window.set_default_size(350, 700)
    game = Game(window)
    game.game_loop()
