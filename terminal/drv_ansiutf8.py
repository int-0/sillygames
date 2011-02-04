#!/usr/bin/env python
#
import sys
import copy

from pycondriver import TxtSurface
from pycondriver import Terminal

_ESC = chr(0x1B)
#_SPC = 32
#_SPC = 9587
_SPC = 0x258A

# ATTRIBS
_RESET      = 0
_BRIGHT     = 1
_DIM        = 2
_UNDERSCORE = 3
_BLINK      = 5
_REVERSE    = 7
_HIDDEN     = 8

# COLORS
_FG = 30
_BG = 40

_BLACK   = 0
_RED     = 1
_GREEN   = 2
_YELLOW  = 3
_BLUE    = 4
_MAGENTA = 5
_CYAN    = 6
_WHITE   = 7

# Simple text surface (for UTF-8 only)
#
# Each element has this format:
#
# -------X|XXYYYZZZ|CCCCCCCC|CCCCCCCC
#
#              XXX: text attribute
#              YYY: foreground color
#              ZZZ: background color
# CCCCCCCCCCCCCCCC: UTF-16 character
#

class Utf8Surface(TxtSurface):
    def __init__(self, size, data = []):
        self.size = size
        if not (len(data) == (self.size[0] * self.size[1])):
            # Raises an error! (given data is different than
            # surface size)
            self.srf = [_SPC] * (self.size[0] * self.size[1])
        else:
            self.srf = data

    def clear(self):
        self.srf = [_SPC] * (self.size[0] * self.size[1])

    def resize(self, new_size):
        if new_size == self.size:
            return

        # Get crop rectangle
        min_x = min(self.size[0], new_size[0])
        min_y = min(self.size[1], new_size[1])

        # Create empty surface
        new_srf = [_SPC] * (new_size[0] * new_size[1])

        # Copy lines
        new_ind = 0
        for y in range(min_y):
            # Copy source line
            new_srf[new_ind : new_ind + min_x] = self.srf[0:min_x]
            new_ind += new_size[0]
        self.srf = new_srf
        self.size = new_size
        
    def blit(self, position, surface):
        if (surface.size > self.size):
            # Raises an exception!!
            return
        (px, py) = position

        # Compute crop area
        line_len = (px + surface.size[0]) % self.size[0]
        lines = (px + surface.size[1]) % self.size[1]

        # Initial copy index
        srf_ind = (py * self.size[0]) + px
        # Dump lines
        for y in range(lines):
            self.srf[srf_ind:srf_ind + line_len] = surface.srf[:line_len]
            srf_ind += self.size[0]
        self.dirty = True

    def set_background(self, attributes, color):
        for i in range(len(self.srf)):
            char = self.srf[i]
            attr = (char >> 16)
            char &= 0xFFFF
            # Set new background (saving foreground)
            attr &= 0b000111000
            attr |= (color & 7)
            attr |= (attributes & 7) << 6
            self.srf[i] = char | (attr << 16)

    def set_foreground(self, attributes, color):
        for i in range(len(self.srf)):
            char = self.srf[i]
            attr = (char >> 16)
            char &= 0xFFFF
            # Set new foreground (saving background)
            attr &= 0b000000111
            attr |= (color & 7) << 3
            attr |= (attributes & 7) << 6
            self.srf[i] = char | (attr << 16)

    def fill(self, char):
        (char, attributes, foreground, background) = char
        element = (attributes & 7) << 22
        element |= (foreground & 7) << 19
        element |= (background & 7) << 16
        element |= (char & 0xFFFF)
        self.srf = [element] * (self.size[0] * self.size[1])

    # Need to crop text lines?
    def dump(self, position, text, attributes, foreground, background):
        attributes = (attributes & 7) << 22
        attributes |= (foreground & 7) << 19
        attributes |= (background & 7) << 16
        # Make surface index
        ind = (self.size[0] * (position[1] % self.size[1]) +
               (position[0] % self.size[0]))
        for itext in range(len(text)):
            self.srf[ind + itext] = (attributes << 16) | (text[itext] & 0xFFFF)

    def char_at(self, position):
        element = self.srf[(self.size[0] * (position[1] % self.size[1])) +
                           (position[0] % self.size[0])]
        return (element & 0xFFFF,
                (element & 0b1110000000000000000000000) >> 22,
                (element & 0b1110000000000000000000) >> 19,
                (element & 0b1110000000000000000) >> 16)

    def set_char(self, position, char):
        self.srf[(self.size[0] * (position[1] % self.size[1])) +
                 (position[0] % self.size[0])] = (
            (char[0] & 0xFFFF) | ((char[1] & 7) << 22) | ((char[2] & 7) << 19) |
            (char[3] & 7 << 16))

# Terminal
class Utf8Terminal(Utf8Surface):
    def __init__(self, size = None):
        if size is None:
            size = self.__getConsoleSize()
        Utf8Surface.__init__(self, size)
        self.reset()

    def reset(self):
        self.__cls()
        self.attr = 0
        self.fg_color = _BLACK
        self.bg_color = _WHITE        
        self.fill((_SPC, self.attr, self.fg_color, self.bg_color))
        self.frame()

    def maximize(self):
        size = self.__getConsoleSize()
        if (size != self.size):
            self.resize(size)
        self.frame()

    def frame(self):
        attribute = -1
        self.__setCursorPos((0, 0))
        for ind in range(len(self.srf)):
            char = self.srf[ind]
            new_attribute = (char & 0xFF0000)            
            if (new_attribute != attribute):
                attribute = new_attribute
                self.__set_attributes(attribute >> 16)
            char = char & 0xFFFF
            if char > 255:
                # UTF-8 char encoding
                sys.stdout.write(chr(0xE0 | (char >> 12)) +
                                 chr(0x82 | (char & 0xF00) >> 6) +
                                 chr(char & 0xFF))
            else:
                # ASCII encoding
                sys.stdout.write(chr(char))
        sys.stdout.flush()

    def close(self, with_clear = False):
        self.__set_attributes(449)
        if with_clear:
            self.__cls()

    def new_surface(self, size, data = None):
        if data is None:
            return Utf8Surface(size)
        else:
            return Utf8Surface(size, data)

    def __getConsoleSize(self):
        def ioctl_GWINSZ(fd):
            try:
                import fcntl, termios, struct, os
                cr = struct.unpack('hh',
                                   fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            except:
                return None
            return cr
        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
        if not cr:
            try:
                cr = (env['LINES'], env['COLUMNS'])
            except:
                cr = (25, 80)
        return int(cr[1]), int(cr[0])

    def __set_attributes(self, attrs):
        sys.stdout.write(_ESC + '[' + str((attrs & 0b111000000) >> 6)+ ';' +
                         str(((attrs & 0b111000) >> 3) + _FG) + ';' +
                         str((attrs & 0b111) + _BG) + 'm')
        sys.stdout.flush()
      
    def __setCursorPos(self, pos):
        sys.stdout.write(_ESC + '[' + str(pos[1] % self.size[1]) + ';' +
                         str(pos[0] & self.size[0]) + 'f')
        sys.stdout.flush()

    def __cls(self):
        sys.stdout.write(_ESC + '[2J')
        sys.stdout.flush()

if __name__ == '__main__':
    term = Utf8Terminal()
    term.set_background(0, _RED)
    term.frame()
    term.close()
