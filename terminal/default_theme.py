#!/usr/bin/env python
#

class PyConTheme:
    def __init__(self):
        self.__theme = {
            'bounds' : { 'ul' : 0,
                         'ur' : 0,
                         'bl' : 0,
                         'br' : 0,
                         'h'  : 0,
                         'v'  : 0
                         }
            }
                

    def __call__(self):
        return self.__theme
