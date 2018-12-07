import curses
import random
import select
import sys
import threading
import time


class Kobra():

    def __init__(self, speed=400):
        self.kobra = [(1, 1)]
        self.direction = "E"
        self.alive = True
        self.window = curses.initscr()
        self.speed = speed
        self.window.timeout(self.speed)
        curses.curs_set(0)
        self.fruits = set([self.spawn_fruit()])
        self.print()

    def print(self):
        self.window.erase()
        self.window.border()

        for x, y in self.fruits:
            self.window.addch(y, x, "ò")

        for x, y in self.body():
            self.window.addch(y, x, "#")

        x, y = self.head()
        if self.direction == "N":
            symbol = "^"
        elif self.direction == "E":
            symbol = ">"
        elif self.direction == "S":
            symbol = "v"
        elif self.direction == "W":
            symbol = "<"

        self.window.addch(y, x, symbol)

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
            self.speed -= 10
            self.window.timeout(self.speed)

        if self.direction == "N":
            self.kobra.append((head_x, head_y - 1))
            if head_y <= 1:
                return self.game_over()
        elif self.direction == "E":
            self.kobra.append((head_x + 1, head_y))
            if head_x >= max_x - 2:
                return self.game_over()
        elif self.direction == "S":
            self.kobra.append((head_x, head_y + 1))
            if head_y >= max_y - 2:
                return self.game_over()
        elif self.direction == "W":
            self.kobra.append((head_x - 1, head_y))
            if head_x <= 1:
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
        time.sleep(2)

    def is_alive(self):
        return self.alive

    def set_direction(self, direction):
        self.direction = direction

    def spawn_fruit(self):
        max_y, max_x = self.window.getmaxyx()
        y = random.randint(1, max_y - 2)
        x = random.randint(1, max_x - 2)
        return x, y

    def pause(self):
        self.window.timeout(-1)

        display_string = "PAUSE"
        resume_string = "Press any key to continue"
        self.window.erase()
        self.window.border()
        max_y, max_x = self.window.getmaxyx()
        y = max_y // 2
        x1 = (max_x - len(display_string)) // 2
        x2 = (max_x - len(resume_string)) // 2
        self.window.addstr(y - 1, x1, display_string)
        self.window.addstr(y + 1, x2, resume_string)
        self.window.refresh()

        self.window.getch()
        self.window.timeout(self.speed)

    def next(self):
        t = threading.Thread(target=lambda: time.sleep(self.speed / 1000))
        t.start()
        self.read_char()
        t.join()

    def is_possible(self, direction):
        head_x, head_y = self.head()
        max_y, max_x = self.window.getmaxyx()

        if direction == "N":
            free = head_y > 1 and (head_x, head_y - 1) not in self.body()
        elif direction == "E":
            free = head_x < max_x - \
                2 and (head_x + 1, head_y) not in self.body()
        elif direction == "S":
            free = head_y < max_y - \
                2 and (head_x, head_y + 1) not in self.body()
        elif direction == "W":
            free = head_x > 1 and (head_x - 1, head_y) not in self.body()
        else:
            free = True

        return free

    def closest_fruit(self):
        h_x, h_y = self.head()
        fruit, _ = min(((
            (x, y), abs(x - h_x) * abs(y - h_y)
        ) for x, y in self.fruits), key=lambda f: f[1])

        return fruit

    def avoid_wall(self):
        res = self.direction

        if self.direction == "N" and not self.is_possible("N"):
            res = "E" if self.is_possible("E") else "W"

        elif self.direction == "E" and not self.is_possible("E"):
            res = "N" if self.is_possible("N") else "S"

        elif self.direction == "S" and not self.is_possible("S"):
            res = "E" if self.is_possible("E") else "W"

        elif self.direction == "W" and not self.is_possible("W"):
            res = "N" if self.is_possible("N") else "S"

        return res

    def next_AI(self):
        head_x, head_y = self.head()
        fruit_x, fruit_y = self.closest_fruit()
        self.window.addstr(0, 0, str(fruit_x) + " " + str(fruit_y))
        self.window.refresh()

        if head_x < fruit_x and (head_x + 1, head_y) not in self.body():
            command = "E"
        elif head_x > fruit_x and (head_x - 1, head_y) not in self.body():
            command = "W"
        elif head_y < fruit_y and (head_x, head_y + 1) not in self.body():
            command = "S"
        elif head_y > fruit_y and (head_x, head_y - 1) not in self.body():
            command = "N"
        else:
            command = self.avoid_wall()

        self.set_direction(command)

        time.sleep(.1)

    def read_char(self):
        char_map = {
            259: "N",
            261: "E",
            258: "S",
            260: "W",
            112: "PAUSE",
        }

        curses.flushinp()
        key_code = self.window.getch()

        command = char_map.get(key_code)
        if command == "PAUSE":
            self.pause()
        elif command in ["N", "E", "S", "W"]:
            self.set_direction(command)

    def play(self):
        while self.is_alive():
            self.next()
            self.move()


def main(_):
    kobra = Kobra()
    kobra.play()


if __name__ == "__main__":
    curses.wrapper(main)
