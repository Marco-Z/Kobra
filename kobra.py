import curses
import time
from datetime import datetime as dt

class Kobra():

    def __init__(self, window, speed=500):
        self.kobra = [(1,1)]
        self.direction = "E"
        self.alive = True
        self.window = window
        self.speed = speed
        window.border()
        window.timeout(0)
        curses.curs_set(0)
        window.refresh()
        self.print()

    def print(self):
        self.window.erase()
        self.window.border()
        for x,y in self.kobra:
            self.window.addch(y,x,"O")
        self.window.refresh()


def main(_, window):
    kobra = Kobra(window)
    time.sleep(2)

if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.wrapper(main, stdscr)
