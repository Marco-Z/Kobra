import curses
import time
from datetime import datetime as dt
import random


class Kobra():

    def __init__(self, speed=500):
        self.kobra = [(1, 1)]
        self.direction = "E"
        self.alive = True
        self.window = curses.initscr()
        self.speed = speed
        self.window.timeout(0)
        curses.curs_set(0)
        self.fruits = set([self.spawn_fruit()])
        self.print()

    def print(self):
        self.window.erase()
        self.window.border()

        for x, y in self.fruits:
            self.window.addch(y, x, "🍒")

        for x, y in self.kobra:
            self.window.addch(y, x, "O")

        _, max_x = self.window.getmaxyx()
        y = 0
        points = f" {len(self.body())} "
        x = (max_x - len(points)) // 2
        self.window.addstr(y, x, points)

        self.window.refresh()

    def head(self):
        return self.kobra[-1]

    def body(self):
        return self.kobra[:-1]
    
    def tail(self):
        return self.kobra[0]

    def move(self):
        max_y, max_x = self.window.getmaxyx()
        head_x, head_y = self.head()

        # if the kobra eats a fruit it grows
        if (head_x, head_y) not in self.fruits:
            self.kobra.pop(0)
        else:
            self.fruits.remove((head_x, head_y))
            self.fruits.add(self.spawn_fruit())

        if self.direction == "N":
            if head_y > 1:
                self.kobra.append((head_x, head_y - 1))
            else:
                return self.game_over()
        elif self.direction == "E":
            if head_x < max_x - 2:
                self.kobra.append((head_x + 1, head_y))
            else:
                return self.game_over()
        elif self.direction == "S":
            if head_y < max_y - 2:
                self.kobra.append((head_x, head_y + 1))
            else:
                return self.game_over()
        elif self.direction == "W":
            if head_x > 1:
                self.kobra.append((head_x - 1, head_y))
            else:
                return self.game_over()

        # if the kobra eats itself it's game over
        if self.head() in self.body():
            return self.game_over()

        self.print()

    def game_over(self):
        display_string = "GAME OVER!"
        points_string = f"Your points: {len(self.body())}"
        self.window.erase()
        self.window.border()
        max_y, max_x = self.window.getmaxyx()
        y = max_y // 2
        x1 = (max_x - len(display_string)) // 2
        x2 = (max_x - len(points_string)) // 2
        self.window.addstr(y - 1, x1, display_string)
        self.window.addstr(y + 1, x2, points_string)
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

    def spawn_fruit(self):
        max_y, max_x = self.window.getmaxyx()
        y = random.randint(1, max_y - 2)
        x = random.randint(1, max_x - 2)
        return x, y


def main(_):
    kobra = Kobra()
    while kobra.is_alive():
        tic = dt.now()
        while (dt.now() - tic).microseconds < kobra.speed * 1000:
            key = kobra.window.getch()
            kobra.set_direction(key)
        kobra.move()

    time.sleep(2)


if __name__ == "__main__":
    curses.wrapper(main)
