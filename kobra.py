import curses
import random
import select
import sys
import threading
import time


class Kobra():

    def __init__(self):
        """Initialization of the window"""

        self.window = curses.initscr()
        curses.curs_set(0)

    def reset(self, speed=400):
        """Reset the game
        
        Keyword Arguments:
            speed {int} -- Update frequency of the screen 
                           (default: {400})
        """

        self.kobra = [(1, 1)]
        self.direction = "E"
        self.alive = True
        self.speed = speed
        self.window.timeout(self.speed)
        self.fruits = set([self.spawn_fruit()])

    def print(self):
        """Print the Kobra screen with the snake and the fruit"""

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
        """Returns the head of the Kobra as a tuple (x,y)
        
        Returns:
            tuple -- (x,y) coordinates of the head of the Kobra
        """

        return self.kobra[-1]

    def body(self):
        """Returns a list of coordinates for the body parts of the Kobra
        
        Returns:
            list -- List of (x,y) coordinate tuple of the body parts
        """

        return self.kobra[:-1]

    def tail(self):
        """Returns the last component of the Kobra body as a tuple
        
        Returns:
            tuple -- (x,y) coordinates of the last bit of Kobra
        """

        return self.kobra[0]

    def move(self):
        """Updates the state of the game given the current direction 
        of movement. If the Kobra head moves over a fruit, Kobra eats
        the fruit and grows. If the Kobra Eats itself of hits the wall
        it dies.
        """

        max_y, max_x = self.window.getmaxyx()
        head_x, head_y = self.head()

        # if the kobra eats a fruit it grows
        if (head_x, head_y) not in self.fruits:
            self.kobra.pop(0)
        else:
            self.fruits.remove((head_x, head_y))
            self.fruits.add(self.spawn_fruit())
            self.speed -= 10

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
        """Prints the Game Over screen"""

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
        """Whether the Kobra is still alive
        
        Returns:
            bool -- Whether the Kobra is still alive
        """

        return self.alive

    def set_direction(self, direction):
        """Sets the heading direction of the Kobra to a new direction
        
        Arguments:
            direction {string} -- The new direction of the Kobra:
            `N`: towards the top of the screen
            `S`: towards the bottom of the screen
            `E`: towards the right of the screen
            `W`: towards the left of the screen
        """

        self.direction = direction

    def spawn_fruit(self):
        """Spawns a new fruit in a random position on the screen
        
        Returns:
            tuple -- (x,y) coordinates of the new fruit position
        """

        max_y, max_x = self.window.getmaxyx()
        y = random.randint(1, max_y - 2)
        x = random.randint(1, max_x - 2)
        return x, y

    def menu(self, menu_items):
        """Renders a menu given a map of menu items
        
        Arguments:
            menu_items {dict} -- Menu items of the form: 
                                 "display string": function
                                 the display string is rendered on the 
                                 screen, while the function is invoked
                                 when the item selection is confirmed
        """

        self.window.erase()
        max_y, max_x = self.window.getmaxyx()

        title_string = [
            "_  _ ____ ___  ____ ____",
            "|_/  |  | |__] |__/ |__|",
            "| \\_ |__| |__] |  \\ |  |",
        ]

        x = (max_x - len(title_string[0])) // 2

        for i, title_line in enumerate(title_string):
            self.window.addstr(i + 2, x, title_line)

        y = max_y // 2 - len(menu_items) // 2
        for i, display_string in enumerate(menu_items.keys()):
            x = (max_x - len(display_string)) // 2
            self.window.addstr(y + 2 * i, x, display_string)

        self.window.border()

        codes = {
            259: "Up",
            258: "Down",
            10: "Enter",
        }
        x = (max_x - len(max(menu_items.keys(), key=len))) // 2 - 2
        key_code = ""
        focus = 0
        while True:
            self.window.addch(y, x, ">")
            self.window.timeout(-1)
            key_code = self.window.getch()

            if codes.get(key_code, "") == "Up":
                self.window.addch(y, x, " ")
                if focus > 0:
                    y -= 2
                    focus -= 1
            elif codes.get(key_code, "") == "Down":
                self.window.addch(y, x, " ")
                if focus < len(menu_items) - 1:
                    y += 2
                    focus += 1
            elif codes.get(key_code, "") == "Enter":
                break

        list(menu_items.values())[focus]()

    def pause(self):
        """Pause menu, with Resume, Main Menu and Quit"""

        self.window.timeout(-1)
        self.menu({
            "Resume": lambda: self.window.timeout(self.speed),
            "Main Menu": self.start_menu,
            "Quit": self.quit,
        })

    def start_menu(self):
        """Start Menu, with Play, AI play and Quit"""

        self.menu({
            "Play": self.play,
            "AI": self.play_AI,
            "Quit": self.quit,
        })

    def next(self):
        """Reads the commands, Returns every `self.speed` ms"""

        t = threading.Thread(target=lambda: time.sleep(self.speed / 1000))
        t.start()
        self.read_char()
        t.join()

    def is_possible(self, direction):
        """Whether the next move is possible with the given direction
        
        Arguments:
            direction {string} -- The direction to test:
                                  `N`: towards the top of the screen
                                  `S`: towards the bottom of the screen
                                  `E`: towards the right of the screen
                                  `W`: towards the left of the screen
        
        Returns:
            bool -- Whether the a move in the given direction is 
                    possible
        """

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
        """Returns the position of the closest fruit as a tuple
        
        Returns:
            tuple -- (x,y) coordinates of the fruit closest to the head
                     of the Kobra
        """

        h_x, h_y = self.head()
        fruit, _ = min(((
            (x, y), abs(x - h_x) * abs(y - h_y)
        ) for x, y in self.fruits), key=lambda f: f[1])

        return fruit

    def avoid_wall(self):
        """Steers the Kobra in order to avoid the walls
        
        Returns:
            string -- The new direction of the Kobra
        """

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
        """Updates the direction of the Kobra in a greedy manner"""

        key_code = self.window.getch()
        self.window.timeout(0)
        if key_code == 27:
            self.pause()

        head_x, head_y = self.head()
        fruit_x, fruit_y = self.closest_fruit()

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
        """Reads the next commend of the user:
            Arrow keys: change the direction of the Kobra,
            Escape: pause menu
        """

        char_map = {
            259: "N",
            261: "E",
            258: "S",
            260: "W",
            27: "PAUSE",
        }

        curses.flushinp()
        key_code = self.window.getch()

        command = char_map.get(key_code)
        if command == "PAUSE":
            self.pause()
        elif command in ["N", "E", "S", "W"]:
            self.set_direction(command)

    def start(self):
        """Displays the start menu"""

        self.start_menu()

    def play(self):
        """Starts a game with user input"""

        self.reset()
        while self.is_alive():
            self.window.timeout(self.speed)
            self.next()
            self.move()

    def play_AI(self):
        """Starts a game played by the greedy AI"""

        self.reset()
        while self.is_alive():
            self.next_AI()
            self.move()

    def quit(self):
        """Quits the game"""

        exit()

def main(_):
    kobra = Kobra()
    kobra.start()


if __name__ == "__main__":
    curses.wrapper(main)
