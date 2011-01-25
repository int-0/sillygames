#!/usr/bin/env python
#

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import cairo
import copy

# GTK+ widgeton wich we will draw using Cairo
class Display(gtk.DrawingArea):

    # Draw in response toan expose-event
    __gsignals__ = { "expose-event" : "override" }

    width = 10
    height = 20

    boxes = []
    phantom = []
    for x in range(width):
        row = []
        prow = []
        for y in range(height):
            row.append(False)
            prow.append(False)
        boxes.append(row)
        phantom.append(prow)

    # Handle expose-event by drawing
    def do_expose_event(self, event):
        # Create cairo context
        cr = self.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y,
                     event.area.width, event.area.height)
        cr.clip()
        self.draw(cr, *self.window.get_size())

    def draw(self, cr, width, height):
        # Fill width gray
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        size_x = width / self.width
        size_y = height / self.height

        cr.set_source_rgb(1.0, 0.0, 0.0)
        for x in range(self.width):
            for y in range(self.height):
                if self.boxes[x][y] or self.phantom[x][y]:
                    cr.rectangle(size_x * x, size_y * y,
                                 size_x, size_y)
                    cr.fill()

    def connect_signals(self):
        self.connect('key-press-event', self.do_key_press_event)
        self.connect('key-release-event', self.do_key_release_event)

if __name__ == '__main__':
    window = gtk.Window()
    window.set_default_size(350, 700)
    window.connect("delete-event", gtk.main_quit)
    board = Display()
    board.show()
    window.add(board)
    window.present()

    # Draw some boxes
    board.boxes.append((0, 0))
    board.boxes.append((9, 9))
    board.show()

    gtk.main()
