#!/usr/bin/env python
#

# Simple text surface
class TxtSurface:
    def __init__(self, size, data = []):
        self.size = size

    def clear(self):
        raise NotImplementedError

    def resize(self, new_size):
        raise NotImplementedError

    def blit(self, position, surface):
        raise NotImplementedError

    def set_foreground(self, attributes, color):
        raise NotImplementedError

    def set_background(self, attributes, color):
        raise NotImplementedError

    def fill(self, char, char_attributes):
        raise NotImplementedError

    def dump(self, position, text_vector, attributes_vector):
        raise NotImplementedError

# Terminal
class Terminal(TxtSurface):

    def __init__(self, size = None):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def maximize(self):
        raise NotImplementedError

    def frame(self):
        raise NotImplementedError

    def close(self, with_clear):
        raise NotImplementedError

    def new_surface(self, size, data):
        raise NotImplementedError
