import pygame
from pygamepages import PageManager

def get_transparent_surf(size, color=(0,0,0,0)):
    surf = pygame.Surface((1,1))
    surf = surf.convert_alpha()
    surf.set_at((0,0), color)
    return pygame.transform.scale(surf, size)


class Object:
    def __init__(self, source, size, pos, **kw):
        self.size = size
        self.pos = pos
        self.obj_id = source.obj_id + '-' + str(len(source._objects))  
        source._objects.append(self)

        default = {
            'centralized': False,
            'active': True,
            'background_color': (0,0,0,0),
            'background_image': False
        }
        default.update(kw)
        self.config(**default)    
    
    def __setattrs(self, **kw):
        for key, val in kw.items():
            self.__setattr__(key, val)
    
    def setup(self):
        self.surf = pygame.Surface(self.size)
        source_actual_pos = self.get_source_actual_pos()
        self.actual_pos = (source_actual_pos[0] + self.pos[0],
                source_actual_pos[1] + self.pos[1])
        if self.centralized:
            self.actual_pos = (self.actual_pos[0] - self.size[0]//2, 
                    self.actual_pos[1] - self.size[1]//2)
        if self.background_image:
            self.background = pygame.transform.scale(self.background_image, self.size)
        else:
            self.background = get_transparent_surf(self.size, self.background_color)

    def config(self, **kw):
        self.__setattrs(**kw)
        self.setup()

    def update(self):
        pass

    def draw_background(self):
        self.surf = self.background.copy()

    def place(self, source):
        if self.active:
            if self.centralized:
                source.blit(self.surf, (self.pos[0]-self.size[0]//2,
                        self.pos[1]-self.size[1]//2))
            else:
                source.blit(self.surf, tuple(self.pos))

    def get_source(self):
        return PageManager.find_object('-'.join(self.obj_id.split('-')[:-1]))

    def get_source_actual_pos(self):
        return self.get_source().actual_pos

    def bind(self, event_type, func):
        PageManager.bind(event_type, func, self.obj_id)

    def mouse_focus(self):
        mouse_pos = pygame.mouse.get_pos()
        pos = self.actual_pos
        if ((mouse_pos[0] > pos[0]) and 
                (mouse_pos[0] < pos[0] + self.size[0]) and
                (mouse_pos[1] > pos[1]) and
                (mouse_pos[1] < pos[1] + self.size[1])):
            return True
        return False


class Frame(Object):
    def __init__(self, source, size, pos, **kw):
        super().__init__(source, size, pos, **kw)

        self._objects = []

    def draw_objects(self):
        for obj in self._objects:
            obj.draw()
            obj.place(self.surf)
    
    def update_objects(self):
        for obj in self._objects:
            obj.update()

    def update(self):
        self.update_objects()

    def draw(self):
        self.draw_background()
        self.draw_objects()


class Page(Frame):
    def __init__(self, tag, size, pos=(0,0), **kw):
        self.source = PageManager.main_surf
        self.tag = tag
        self.obj_id = str(len(PageManager._pages))
        self.size = size
        self.pos = pos
        self.actual_pos = pos
        
        self.event_funcs = [[] for _ in range(PageManager.number_event_types)]

        default = {
            'centralized': False,
            'active': True,
            'background_color': (0,0,0,0),
            'background_image': False
        }
        default.update(kw)
        self.config(**default)
        
        self._objects = []
        PageManager._pages.append(self)
        self.change_page = PageManager.change_page
    
    def get_source(self):
        return None

    def get_source_actual_pos(self):
        return self.actual_pos

    def draw(self):
        super().draw()
        self.place(self.source)

    def on_open(self, *args, **kw):
        pass

    def on_close(self):
        pass

    def loop(self):
        self.draw()


class Label(Object):
    def __init__(self, source, pos, text, **kw):
        default = {
            'text': text,
            'centralized': True,
            'font': 'Arial',
            'font_size': 28,
            'text_color': (0,0,0)
        }
        default.update(kw)
        super().__init__(source, (1,1), pos, **default)
        
    def setup(self, **kw):
        self._font = pygame.font.SysFont(self.font, self.font_size)
        self._text = self._font.render(self.text, True, self.text_color)
        size = self._text.get_size()
        self.size = (size[0]+4, size[1]+4)
        super().setup()
        
    def draw(self):
        self.draw_background()
        self.surf.blit(self._text, (2,2))


class Button(Label):
    def __init__(self, source, pos, text, func, **kw):
        super().__init__(source, pos, text, **kw)
        self.func = func
        self.bind(pygame.MOUSEBUTTONDOWN, self.on_click)
    
    def on_click(self, event):
        if self.mouse_focus():
            self.func()
    

class Slider(Object):
    def __init__(self, source, pos, **kw):
        default = {
            'centralized': True,
            'width': 100,
            'default_value': 0
        }
        default.update(kw)
        self.value = default['default_value']
        self._sliding = False
        super().__init__(source, (1,1), pos, **default)
        self.bind(pygame.MOUSEBUTTONDOWN, self.on_click)
        self.bind(pygame.MOUSEBUTTONUP, self.on_button_up)
    
    def setup(self, **kw):
        self._vertical_rect = pygame.Rect(7, 10, self.width, 4)
        self._rect_value = pygame.Rect(0, 0, 14, 24)
        self.size = (self.width + 14, 24)
        super().setup()
    
    def update(self):
        if self._sliding:
            mouse_pos_x = pygame.mouse.get_pos()[0] - self.actual_pos[0] - 7
            if mouse_pos_x > self.width:
                mouse_pos_x = self.width
            if mouse_pos_x < 0:
                mouse_pos_x = 0
            self.value = mouse_pos_x/self.width

    def draw(self):
        self.draw_background()
        self._rect_value.left = int(self.value*self.width)
        pygame.draw.rect(self.surf, (0,0,0), self._vertical_rect)
        pygame.draw.rect(self.surf, (0,0,0), self._rect_value)
    
    def on_click(self, event):
        if self.mouse_focus():
            self._sliding = True
    
    def on_button_up(self, event):
        self._sliding = False 

