class Test:
    def __init__(self, **kw):
        self.size = 0
        self.attrs = [['size', self.size]]
        self.config(**kw)

    def config(self, **kw):
        for key, val in kw.items():
            if val:
                self.__setattr__(key, val)
        self._size = self.size + 1
        print('passo pela mae', self._size)
    
    def print_info(self):
        print(self._size)


class Test2(Test):
    def __init__(self, **kw):
        self.size = 0
        self.pos = 0
        super().__init__(**kw)
    
    def config(self, **kw):
        super().config(**kw)
        self._pos = self.pos + 1
    
    def print_info(self):
        print(self._size, self._pos)

t = Test2(size=7, pos=3)
t.print_info()
a = {'a': 2, 'b': 5}
b = {'a': 0, 'c': 2}
a.update(b)
print(a)