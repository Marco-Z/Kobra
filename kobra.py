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


    def move(self):
        max_y, max_x = self.window.getmaxyx()
        head_x, head_y = self.kobra[-1]
        self.kobra.pop(0)
        if self.direction == "N":
            if head_y > 1:
                self.kobra.append((head_x, head_y - 1))
            else:
                self.game_over()
        elif self.direction == "E":
            if head_x < max_x - 2:
                self.kobra.append((head_x + 1, head_y))
            else:
                self.game_over()
        elif self.direction == "S":
            if head_y < max_y - 2:
                self.kobra.append((head_x, head_y + 1))
            else:
                self.game_over()
        elif self.direction == "W":
            if head_x > 1:
                self.kobra.append((head_x - 1, head_y))
            else:
                self.game_over()
        self.print()
            
    def game_over(self):
        display_string = "GAME OVER!"
        self.window.erase()
        self.window.border()
        max_y, max_x = self.window.getmaxyx()
        y = max_y // 2
        x = (max_x - len(display_string)) // 2
        self.window.addstr(y,x, display_string)
        self.window.refresh()
        self.alive = False

    def is_alive(self):
        return self.alive

    def set_direction(self, key):
        direction_map = {
            259: "N", 
            261: "E", 
            258: "S", 
            260: "W",
        }
        direction = direction_map.get(key)
        if direction:
            self.direction = direction

def main(_, window):
    kobra = Kobra(window)
    while kobra.is_alive():
        tic = dt.now()
        while (dt.now() - tic).microseconds < kobra.speed * 1000:
            key = window.getch()
            kobra.set_direction(key)
        kobra.move()

    time.sleep(2)

if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.wrapper(main, stdscr)
