from random import randint
from random import choice


class Piece3D(dict):
    def __init__(self, name, data: str, color=None):
        if len(data) != 27:
            raise Exception("Invalid 3D Object")
        dict.__init__(self, name=name, data_3D=data, color=color)
        self.name = name
        self.data = data
        self.color = color
        self.front = data[:9]
        self.back = data[-9:]
        self.top = "".join([x for y in [data[i:i + 3] for i in range(0, len(data), 9)] for x in y])
        self.bot = "".join([x for y in [data[i:i + 3] for i in range(6, len(data), 9)] for x in y])
        self.right = "".join([data[i] for i in range(2, len(data), 3)])
        self.left = "".join([data[i] for i in range(0, len(data), 3)])

    def __repr__(self):
        return str(self.name)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.data == other.data


class Piece6D(dict):
    def __init__(self, data: list[Piece3D]):
        if len(data) != 27:
            raise Exception("Invalid 6D Object")
        dict.__init__(self, data_6D=data)
        # data = [str(x.data) for x in data]
        self.hash = self.__hash__()

        self.front = "".join([str(p.front) for p in data])
        self.back = "".join([str(p.back) for p in data])
        self.top = "".join(
            [str(p.top) for p in data])
        self.bot = "".join(
            [str(p.bot) for p in data])
        self.right = "".join([str(p.right) for p in data])
        self.left = "".join([str(p.left) for p in data])

        """self.front = "".join([str(p.front) for p in data[:9]])
        self.back = "".join([str(p.back) for p in data[-9:]])
        self.top = "".join([str(p.top) for p in [x for y in [data[i:i + 3] for i in range(0, len(data), 9)] for x in y]])
        self.bot = "".join([str(p.bot) for p in [x for y in [data[i:i + 3] for i in range(6, len(data), 9)] for x in y]])
        self.right = "".join([str(p.right) for p in [data[i] for i in range(2, len(data), 3)]])
        self.left = "".join([str(p.left) for p in [data[i] for i in range(0, len(data), 3)]])"""

    def __eq__(self, other):
        for i, d in enumerate(self["data_6D"]):
            if d != other["data_6D"][i]:
                return False
        return True

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "".join([str(x.data) for x in self["data_6D"]])

    def __hash__(self):
        return hash(self.__repr__())


class Grid:
    def __init__(self, rows, cols, pieces):
        self.rows = rows
        self.cols = cols
        self.pieces = pieces
        self.grid = []
        self.reset(pieces)

    def __repr__(self):
        b = 20
        val = ""
        for row in self.grid:
            row_arr = []
            for cell in row:
                if not cell:
                    text = "None"
                elif isinstance(cell, Piece3D):
                    text = str(cell)
                else:
                    text = "len:" + str(len(cell))
                row_arr.append(text + " " * (b - len(text)))
            val += ",".join(row_arr) + "\n\n"
        return val

    def reset(self, pieces=None):
        if not pieces:
            pieces = self.pieces
        if len(self.grid) == 0:
            for i in range(self.rows):
                row = []
                for j in range(self.cols):
                    row.append(pieces)
                self.grid.append(row)
        else:
            for i in range(self.rows):
                for j in range(self.cols):
                    self.grid[i][j] = pieces

    def collapse_random_cell(self):
        r_row = randint(0, self.rows - 1)
        r_col = randint(0, self.cols - 1)
        self.grid[r_row][r_col] = choice(self.grid[r_row][r_col])
        # print(self.get_neighbors(r_row, r_col))
        self._domino(r_row, r_col)

    def collapse_next_cell(self, stop_on_none=False):
        if None in self.grid:
            self.reset()
            return stop_on_none
        # find piece with lowest number of options -> collapse that one
        d = [len(cell) for row in self.grid for cell in row if cell and not
        isinstance(cell, Piece3D) and not isinstance(cell, Piece6D)]
        if len(d) == 0:
            return True
        m = min(d)
        found = False
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j] and not isinstance(self.grid[i][j], Piece3D) \
                        and not isinstance(self.grid[i][j], Piece6D) \
                        and len(self.grid[i][j]) == m:
                    found = True
                    break
            if found:
                break
        self.grid[i][j] = choice(self.grid[i][j])
        self._domino(i, j)
        return False

    def _domino(self, row, col):
        current_piece = self.grid[row][col]
        higherPieceType = Piece3D
        if not isinstance(current_piece, Piece3D):
            higherPieceType = Piece6D
        n = self._get_neighbors(row, col)  # n for neighbors

        for dir in ["b", "r", "f", "l"]:
            if dir in n:
                coords = n[dir]

                if self.grid[coords[0]][coords[1]] and not isinstance(self.grid[coords[0]][coords[1]], higherPieceType):
                    new_list = []
                    for possible in self.grid[coords[0]][coords[1]]:
                        if dir == "b":
                            # print(possible, current_piece)
                            # print(type(possible), type(current_piece))
                            if possible.front == current_piece.back:
                                new_list.append(possible)
                        elif dir == "r":
                            if possible.left == current_piece.right:
                                new_list.append(possible)
                        elif dir == "f":
                            if possible.back == current_piece.front:
                                new_list.append(possible)
                        elif dir == "l":
                            if possible.right == current_piece.left:
                                new_list.append(possible)
                    recur = False
                    if len(new_list) == 1:
                        new_list = new_list[0]
                        recur = True
                    elif len(new_list) == 0:
                        new_list = None
                        print(f"Direction: {dir}")
                    self.grid[coords[0]][coords[1]] = new_list
                    if recur:
                        self._domino(coords[0], coords[1])

    def _get_neighbors(self, row, col):
        neighbors = {}
        if row + 1 <= self.rows - 1:
            neighbors["f"] = [row + 1, col]  # front
        if row - 1 >= 0:
            neighbors["b"] = [row - 1, col]  # back
        if col + 1 <= self.cols - 1:
            neighbors["r"] = [row, col + 1]  # right
        if col - 1 >= 0:
            neighbors["l"] = [row, col - 1]  # left
        return neighbors

    def get_grid_smooth(self):
        '''
        Converts the self.grid into a smoothed version.
        convert 3x3x3 areas of cubes into 3x3x3 meshes that only include common edges and edges
        that only touch the outer edges
        :return:
        '''
        pass


class Controller:
    def __init__(self, pieces, rows, cols):
        self.pieces = pieces
        self.grid = Grid(rows, cols, pieces)
        self.is6D = isinstance(pieces[0], Piece6D)

    def collapse(self):
        self.grid.collapse_random_cell()

        inp = ""
        end = False
        while not end:
            end = self.grid.collapse_next_cell()

        return self.grid.grid

    def reset(self):
        self.grid.reset(self.pieces)

    def redo_grid(self):
        self.reset()
        return self.collapse()
