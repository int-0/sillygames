#!/usr/bin/env python
#
import uuid
from default_theme import PyConTheme

class PyConRender:
    def __init__(self, terminal, theme = None):
        self.__term = terminal
        if theme is None:
            self.__theme = PyConTheme()
        else:
            self.__theme = theme
        self.__objs = {}
        self.__draw_queue = []

    def add_obj(self, obj, drawable = True):
        oid = uuid.uuid4()
        self.__objs[oid] = obj
        self.__draw_queue.append(oid)
        return oid

    def remove_obj(self, oid):
        if not self.__objs.has_key(oid):
            # RAISES AN ERROR!
            return
        del(self.__objs[oid])
        if oid in self.__draw_queue:
            self.__draw_queue.remove(oid)

    def update(self):
        for oid in self.__objs.keys():
            self.__objs[oid].update()

    def draw(self):
        for oid in self.__draw_queue:
            self.__objs[oid].draw()
