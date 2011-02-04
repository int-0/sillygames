#!/usr/bin/env python

# Console
class Console:
    def __init__(self, terminal):
        self.__term = terminal

    def set_cursor_pos(self, position):
        raise NotImplementedError

    def set_text_attributes(self, position):
        raise NotImplementedError

    def put_text(self, text):
        raise NotImplementedError

    def put_line(self, text):
        raise NotImplementedError

    def put_lines(self, text):
        raise NotImplementedError
