from random import randint


class BoardException(BaseException):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за поле. Повторите ход"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы сюда уже стреляли. Повторите ход"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow
        self.length = length
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        return [Dot(self.bow.x + i * self.direction, self.bow.y + i * (1 - self.direction)) for i in range(self.length)]

    def hit(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [["0"] * size for _ in range(size)]
        self.occup = []
        self.ships = []

    def __str__(self):  # для вывода доски
        display = ""
        display += "   A  B  C  D  E  F "
        for i in range(len(self.field)):
            row = self.field[i]
            display += f"\n{i + 1}  " + "  ".join(row) + "  "

        if self.hid:
            display = display.replace("◼", "0")
        return display

    def get_letters_to_numbers(self):
        return {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5}

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, visible=False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in around:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.occup:
                    if visible:
                        self.field[cur.x][cur.y] = "T"
                    self.occup.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.occup:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "◼"
            self.occup.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.occup:
            raise BoardUsedException()

        self.occup.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, visible=True)
                    print("Корабль уничтожен")
                    return False
                else:
                    print("Корабль подпит")
                    return True

        self.field[d.x][d.y] = "T"
        print("Мимо")
        return False

    def begin(self):
        self.occup = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        try:
            x_row = input("Введите число ряда: ")
            while x_row not in "123456":
                print("Ошибка.")
                x_row = input("Введите правильное число ряда: ")

            y_column = input("Введите букву столбца: ").upper()
            while y_column not in "ABCDEF":
                print("Ошибка.")
                y_column = input("Введите правильную букву столбца: ").upper()
            return Dot(int(x_row) - 1, self.board.get_letters_to_numbers()[y_column])
        except ValueError and KeyError:
            print("Ошибка.")
            return self.ask()


class Game:
    def __init__(self, size=6):
        self.size = size

        player = self.random_board()
        computer = self.random_board()
        computer.hid = True
        self.ai = AI(computer, player)
        self.user = User(player, computer)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for units in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), units, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print(" -> ИГРА МОРСКОЙ БОЙ <-")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Поле пользователя:")
            print(self.user.board)
            print("-" * 20)
            print("Поле компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.user.board.defeat():
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
