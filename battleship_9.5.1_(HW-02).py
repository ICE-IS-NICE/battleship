#import os
from  random import randint

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Out of board bounds."
    
class BoardUsedException(BoardException):
    def __str__(self):
        return "Already shot this tile."
    
class BoardWrongShipException(BoardException):
    pass

class Dot():
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)
    
    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

class Ship():
    def __init__(self, bow: Dot, l: int, orient: int):
        self.length = l
        self.bow: Dot = bow
        self.orient = orient
        self.lifes = l

    @property
    def dots(self): #all ships face north or west
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y
            if self.orient == 0:
                cur_x += i
            elif self.orient == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots
    
    def shooten(self, shot):
        return shot in self.dots

class Board():
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [["0"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"
        if self.hid:
            res = res.replace("■", "0")
        return res

    def add_ship(self, ship: Ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy: 
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■" 
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)
    
    def contour(self, ship: Ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy, in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb: 
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)
    
    def out(self, d: Dot):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))
    
    def shot(self, d: Dot):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d)
        for ship in self.ships:
            if d in ship.dots:
                ship.lifes -= 1
                self.field[d.x][d.y] = "X"
                if ship.lifes == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Ship destroyed.")
                    return False
                else:
                    print("Hit!")
                    return True
        self.field[d.x][d.y] = "."
        print("Miss.")
        return False
    
    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)

class Player():
    def __init__(self, board: Board, enemy: Board):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError() #должен быть у потомков класса, поэтому вызываем error
    
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class User(Player):
    def ask(self):
        while True:
            cords = input("Your turn (Row Column): ").split()
            if len(cords) != 2:
                print("Need 2 coords.")
                continue
            x, y = cords
            if not(x.isdigit()) or not(y.isdigit()):
                print("Error.")
                continue
            x, y = int(x), int(y)
            return Dot(x-1, y-1)

class AI(Player):
    #last_ai_shot = None

    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"AI turn: {d.x+1} {d.y+1}")
        self.last_ai_shot = d
        return d

class Game():
    def __init__(self, size=6):
        self.size = size
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("Game begins.")

    def print_boards(self):
        print("-"*25)
        print("User board:")
        print(self.us.board)
        print("-"*25)
        print("AI board:")
        print(self.ai.board)
        print("-"*25)
        
    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                #if self.ai.last_ai_shot:
                    #print(f"Last AI shot: {self.ai.last_ai_shot.x+1} {self.ai.last_ai_shot.y+1}")
                print("User turn.")
                repeat = self.us.move()
            else:
                print("AI turn.")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.defeat():
                self.print_boards()
                print("-"*20)
                input("User wins.")
                break
            if self.us.board.defeat():
                self.print_boards()
                print("-"*20)
                input("AI wins.")
                break
            num += 1
            #os.system('cls')

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()