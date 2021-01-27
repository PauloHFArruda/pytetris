import pygame

class Piece:
    def __init__(self, color):
        self.row = 1
        self.column = 5
        self.color = color
        self.orientation = 0

class Piece1(Piece):
    def __init__(self):
        super().__init__(1)

    def body(self):
        if self.orientation%2 == 0:
            return [(self.column-1, self.row), (self.column, self.row),
                (self.column+1, self.row), (self.column+2, self.row)]
        else:
            return [(self.column, self.row-1), (self.column, self.row),
                (self.column, self.row+1), (self.column, self.row+2)]
    
class Piece2(Piece):
    def __init__(self):
        super().__init__(2)
    
    def body(self):
        if self.orientation == 0:
            return [(self.column-1, self.row-1), (self.column-1, self.row),
                (self.column, self.row), (self.column+1, self.row)]
        if self.orientation == 1:
            return [(self.column, self.row-1), (self.column+1, self.row-1),
                (self.column, self.row), (self.column, self.row+1)]
        if self.orientation == 2:
            return [(self.column-1, self.row), (self.column, self.row),
                (self.column+1, self.row), (self.column+1, self.row+1)]
        if self.orientation == 3:
            return [(self.column, self.row-1), (self.column, self.row),
                (self.column-1, self.row+1), (self.column, self.row+1)]

class Piece3(Piece):
    def __init__(self):
        super().__init__(3)
    
    def body(self):
        if self.orientation == 0:
            return [(self.column+1, self.row-1), (self.column-1, self.row),
                (self.column, self.row), (self.column+1, self.row)]
        if self.orientation == 1:
            return [(self.column+1, self.row+1), (self.column, self.row-1),
                (self.column, self.row), (self.column, self.row+1)]
        if self.orientation == 2:
            return [(self.column-1, self.row+1), (self.column-1, self.row),
                (self.column, self.row), (self.column+1, self.row)]
        if self.orientation == 3:
            return [(self.column-1, self.row-1), (self.column, self.row-1),
                (self.column, self.row), (self.column, self.row+1)]

class Piece4(Piece):
    def __init__(self):
        super().__init__(4)
    
    def body(self):
        if self.orientation == 0:
            return [(self.column, self.row), (self.column-1, self.row),
                (self.column+1, self.row), (self.column, self.row-1)]
        if self.orientation == 1:
            return [(self.column, self.row), (self.column, self.row-1),
                (self.column, self.row+1), (self.column+1, self.row)]
        if self.orientation == 2:
            return [(self.column, self.row), (self.column-1, self.row),
                (self.column+1, self.row), (self.column, self.row+1)]
        if self.orientation == 3:
            return [(self.column, self.row), (self.column, self.row-1),
                (self.column, self.row+1), (self.column-1, self.row)]

class Piece5(Piece):
    def __init__(self):
        super().__init__(5)

    def body(self):
        return [(self.column, self.row), (self.column+1, self.row),
            (self.column, self.row+1), (self.column+1, self.row+1)]

class Piece6(Piece):
    def __init__(self):
        super().__init__(6)
    
    def body(self):
        if self.orientation%2 == 0:
            return [(self.column, self.row-1), (self.column-1, self.row),
                (self.column, self.row), (self.column+1, self.row-1)]
        else:
            return [(self.column, self.row-1), (self.column, self.row),
                (self.column+1, self.row), (self.column+1, self.row+1)]

class Piece7(Piece):
    def __init__(self):
        super().__init__(7)
    
    def body(self):
        if self.orientation%2 == 0:
            return [(self.column-1, self.row-1), (self.column, self.row-1),
                (self.column, self.row), (self.column+1, self.row)]
        else:
            return [(self.column+1, self.row-1), (self.column, self.row),
                (self.column+1, self.row), (self.column, self.row+1)]
