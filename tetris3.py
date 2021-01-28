import pygame
from pygamepages import*
from pieces import*
from random import choice
from functools import partial
import json

pygame.init()
pygame.font.init()
pygame.mixer.init()
sound_chanel = pygame.mixer.Channel(1)


def read_json(fname):
    with open(fname, 'r', encoding='utf-8') as file:
        json_dict = json.loads(file.read())
    return json_dict

def write_json(fname, json_dict):
    with open(fname, 'w', encoding='utf-8') as file:
        json.dump(json_dict, file, ensure_ascii=False, indent=4)

def play_sound(sound):
    sound_chanel.play(pygame.mixer.Sound('appData/sounds/' + sound + '.ogg'))



class Animation(Object):
    def __init__(self, end_frame, source, size, pos, **kw):
        super().__init__(source, size, pos, **kw)
        self.end_frame = end_frame        
        self.current_frame = 0
        self.animate = False
    
    def start(self):
        self.current_frame = 0
        self.animate = True
    
    def end(self):
        pass

    def draw(self):
        pass
    
    def update(self):
        if self.animate:
            self.draw()
            if self.current_frame == self.end_frame:
                self.animate = False
                self.end()
            else:
                self.current_frame += 1


class BrokeAnimation(Animation):
    def __init__(self, source, size, square_size, square_board):
        super().__init__(15, source, size, (0,0))
        self.square_size = square_size
        self.off_set = square_board//2
        self.detach_surf = pygame.Surface((10*square_size, square_size + self.off_set))
        self.detach_surf.fill((255,255,255))
        #self.sound = pygame.Sound('sounds/ogg/line-remove.ogg')
        self.alpha_values = [20, 60, 150, 200, 250]
        self.rows = []
    
    def start(self, rows):
        super().start()
        self.rows = rows


    def draw(self):
        self.draw_background()
        self.detach_surf.set_alpha(self.alpha_values[self.current_frame%5])
        for row in self.rows:
            self.surf.blit(self.detach_surf, (0, self.square_size*row + self.off_set))


class MainMenu(Page):
    def __init__(self, size):
        background = pygame.image.load('appData/images/main_menu_background.png')
        
        super().__init__('MainMenu', size, background_image=background)
        
        self.but_continue = Button(self, (size[0]//2, int(size[1]*0.54)), 
                'Continue', partial(self.change_page, 'GamePage', load=True))
        self.but_new_game = Button(self, (size[0]//2, int(size[1]*0.62)), 
                'New game', partial(self.change_page, 'GamePage', load=False))
        self.but_options = Button(self, (size[0]//2, int(size[1]*0.70)), 
                'Options', partial(self.change_page, 'OptionsMenu'))
    
    def loop(self):
        #self.source.fill(255,255,255)         
        self.draw()


class OptionsMenu(Page):
    def __init__(self, size):
        super().__init__('OptionsMenu', size)
        self.background = pygame.image.load('appData/images/options_menu_background.png')

        self.music_vol = Slider(self, (size[0]//2, int(size[1]*0.40)), default_value=0.3)
        self.sound_vol = Slider(self, (size[0]//2, int(size[1]*0.54)), default_value=0.8)
        Button(self, (size[0]//2, int(size[1]*0.74)), 'Voltar', partial(self.change_page, 'MainMenu'))

        self.load_settings()
        self.save_settings()

    def start(self):
        self.load_settings()

    def load_settings(self):
        try:
            settings = read_json('settings.json')
            self.music_vol.value = settings['music_vol']
            self.sound_vol.value = settings['sound_vol']
        except:
            self.save_settings()

    def save_settings(self):
        settings = {
            'music_vol': self.music_vol.value,
            'sound_vol': self.sound_vol.value
        }
        write_json('settings.json', settings)

    def close(self):
        pygame.mixer.music.set_volume(self.music_vol.value)
        sound_chanel.set_volume(self.sound_vol.value)
        self.save_settings()

    def loop(self):           
        self.draw()


class Game:
    def __init__(self):
        self.width = 10
        self.height = 20

        self.pieces = [Piece1, Piece2, Piece3, Piece4, Piece5, Piece6, Piece7]

        self.paused = True
        self.falling_speed = 15
        self.level = 1
        self.frame_count = 0
        self.complete_rows = []
        self.left_input = 0
        self.right_input = 0
    
    def verify_complete_rows(self):
        self.complete_rows = []
        i = self.height - 1
        while i >= self.top:
            if self.is_row_complete(i):
                self.complete_rows.append(i)
            i -= 1
                
    def is_row_complete(self, row):
        for j in range(self.width):
            if self.table[row][j] == 0:
                return False
        return True

    def clean_complete_rows(self):
        self.pts += len(self.complete_rows)*200 - 100
        i = self.height - 1
        while i >= self.top:
            if self.is_row_complete(i):
                self.clean_row(i)
            else:
                i -= 1
        self.complete_rows = []

    def clean_row(self, row):
        i = row
        while i >= self.top:
            self.table[i] = self.table[i-1].copy()
            i -= 1
        self.top += 1

    def new_game(self):
        self.table = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.top = self.height
        self.current_piece = self.generate_piece()
        self.next_piece = self.generate_piece()
        self.pts = 0

    def save_game(self):
        current_piece = {
            'color': self.current_piece.color,
            'column': self.current_piece.column,
            'row': self.current_piece.row,
            'orientation': self.current_piece.orientation,
        }
        save = {
            'table': self.table,
            'top': self.top,
            'pts': self.pts,
            'current_piece': current_piece,
            'next_piece_color': self.next_piece.color
        }
        write_json('save.json', save)

    def load_game(self):
        try:
            save = read_json('save.json')
            self.table = save['table']
            self.top = save['top']
            self.pts = save['pts']
            self.current_piece = self.pieces[save['current_piece']['color']-1]()
            self.current_piece.column = save['current_piece']['column']
            self.current_piece.row = save['current_piece']['row']
            self.current_piece.orientation = save['current_piece']['orientation']
            self.next_piece = self.pieces[save['next_piece_color']-1]()
        except:
            self.new_game()

    def collided(self):
        for pos in self.current_piece.body():
            j, i = pos
            if i < 0 or i >= self.height or j < 0 or j >= self.width:
                return True
            elif self.table[i][j] > 0:
                return True
        return False

    def move_down(self):
        piece = self.current_piece
        piece.row += 1
        if self.collided():
            piece.row -= 1
            self.change_piece()
            if self.falling_speed == 2:
                play_sound('force-hit')
            else:
                play_sound('slow-hit')
        elif self.falling_speed == 2:
            self.pts += 1

    def move_side(self, side):
        self.current_piece.column += side
        if self.collided():
            self.current_piece.column -= side
        else:
            play_sound('whoosh')
            
    def rotate(self):
        piece = self.current_piece
        piece.orientation = (piece.orientation+1)%4
        if self.collided():
            piece.orientation = (piece.orientation-1)%4
        else:
            play_sound('block-rotate')

    def change_piece(self):
        self.add_to_table()
        self.current_piece = self.next_piece
        self.next_piece = self.generate_piece()     
    
    def generate_piece(self):
        return choice(self.pieces)()

    def add_to_table(self):
        for pos in self.current_piece.body():
            j, i = pos
            self.table[i][j] = self.current_piece.color
            if i < self.top:
                self.top = i

    def make_moves():
        pass
        
    def event_handler(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and not self.paused:
                self.rotate()
            if event.key == pygame.K_DOWN:
                self.falling_speed = 2
            if event.key == pygame.K_RIGHT:
                self.right_input = 1
            if event.key == pygame.K_LEFT:
                self.left_input = 1
            if event.key == pygame.K_p:
                self.paused = not self.paused
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                self.falling_speed = 16-self.level
            if event.key == pygame.K_RIGHT:
                self.right_input = 0
            if event.key == pygame.K_LEFT:
                self.left_input = 0

    def loop(self):
        self.level = 1 + self.pts//1000
        if len(self.complete_rows) == 0 and self.top > 1 and not self.paused:
            self.frame_count = (self.frame_count + 1)%360360
            if self.frame_count%self.falling_speed == 0:
                self.move_down()
            if self.left_input > 0:
                if self.left_input == 1:
                    self.move_side(-1)
                if self.left_input > 5 and (self.left_input-5)%3 == 0:
                    self.move_side(-1)
                self.left_input += 1
            if self.right_input > 0:
                if self.right_input == 1:
                    self.move_side(1)
                if self.right_input > 5 and (self.right_input-5)%3 == 0:
                    self.move_side(1)
                self.right_input += 1
            self.verify_complete_rows()
            if self.complete_rows:
                self.broke_animation.start(self.complete_rows)
                play_sound('line-remove')


class NextPieceView(Object):
    def __init__(self, source, pos, square_size, square_board):
        self.square_size = square_size
        self.square_board = square_board
        size = (5*self.square_size-self.square_board, 3*self.square_size-self.square_board)
        super().__init__(source, size, pos, centralized=True)
        self.piece = None
        self.set_surfs()

    def set_surfs(self):
        self.square_surfs = [pygame.image.load('appData/images/square-%d.png'%i)
                for i in range(1, 8)]
        size = self.square_size + self.square_board
        #for surf in self.square_surfs:
        #    pygame.transform.scale(surf, (size, size))

    def draw(self):
        body = self.piece.body()
        min_pos = [10,20]
        max_pos = [0,0]
        for pos in body:
            i, j = pos
            if i < min_pos[0]:
                min_pos[0] = i
            if j < min_pos[1]:
                min_pos[1] = j
            if i > max_pos[0]:
                max_pos[0] = i
            if j > max_pos[1]:
                max_pos[1] = j

        piece_size = ((max_pos[0]-min_pos[0]+1)*self.square_size + self.square_board, 
                (max_pos[1]-min_pos[1]+1)*self.square_size + self.square_board)
            
        surf_size = self.surf.get_size()
        top_left = ((surf_size[0]-piece_size[0])//2, 
                (surf_size[1]-piece_size[1])//2)
        square_surf = self.square_surfs[self.piece.color-1]
        self.draw_background()

        for pos in body:
            new_pos = ((pos[0]-min_pos[0])*self.square_size + top_left[0], 
                    (pos[1]-min_pos[1])*self.square_size + top_left[1])
            self.surf.blit(square_surf, new_pos)


class GameInfo(Frame):
    def __init__(self, source, game, square_size, square_board):
        size = (square_size*7 + square_board, square_size*16)
        pos = (square_size*11, square_size)
        super().__init__(source, size, pos)

        self.game = game
        font_primary = int(1.7*square_size)
        font_secondary = int(0.7*square_size)
        x_pos = self.size[0]//2
        Label(self, (x_pos, int(1.6*square_size)), 'Points', font_size=font_secondary)
        self.lb_pts = Label(self, (x_pos, int(3.1*square_size)), '0', font_size=font_primary)
        Label(self, (x_pos, int(5.6*square_size)), 'Level', font_size=font_secondary)
        self.lb_lvl = Label(self, (x_pos, int(7.1*square_size)), '1', font_size=font_primary)
        Label(self, (x_pos, int(9.6*square_size)), 'Next', font_size=font_secondary)
        self.next_piece_view = NextPieceView(self, (x_pos, int(11.5*square_size)), square_size, square_board)

    def update(self):
        self.lb_pts.config(text=str(self.game.pts))
        self.lb_lvl.config(text=str(self.game.level))
        self.next_piece_view.piece = self.game.next_piece


class TetrisTable(Frame):
    def __init__(self, source, game, square_size, square_board):
        size = (square_size*game.width + 2*square_board, 
                square_size*game.height + 2*square_board)
        pos = (square_size, square_size)
        super().__init__(source, size, pos)

        self.game = game
        self.square_size = square_size
        self.square_board = square_board
        self.game.broke_animation = BrokeAnimation(self, self.size, square_size, square_board)
        self.game.broke_animation.end = self.game.clean_complete_rows

        self.set_surfs()

    def set_surfs(self):
        self.square_surfs = [pygame.image.load('appData/images/square-%d.png'%i)
                for i in range(1, 8)]
        size = self.square_size + self.square_board
        #for surf in self.square_surfs:
        #    pygame.transform.scale(surf, (size, size))
    
    def draw_piece(self, piece):
        square_surf = self.square_surfs[piece.color-1]
        for pos in piece.body():
            i, j = pos
            self.surf.blit(square_surf, (self.square_size*i, self.square_size*j))

    def draw_table(self):
        for i in range(self.game.top, self.game.height):
            for j in range(self.game.width):
                value = self.game.table[i][j]
                if value > 0:
                    square_surf = self.square_surfs[value-1]
                    self.surf.blit(square_surf, (self.square_size*j, self.square_size*i))

    def draw(self):
        self.draw_background()
        #self.surf.blit(self.background, (0,0))
        self.draw_piece(self.game.current_piece)
        self.draw_table()
        self.game.broke_animation.update()
        self.draw_objects()


class GamePage(Page):
    def __init__(self, size):
        super().__init__('GamePage', size)
        self.background = pygame.image.load('appData/images/background.png')
        self.square_size = 28
        self.square_board = 3
        self.game = Game()
        self.bind(pygame.KEYDOWN, self.game.event_handler)
        self.bind(pygame.KEYUP, self.game.event_handler)

        self.tetris_table = TetrisTable(self, self.game, self.square_size, self.square_board)
        self.game_info = GameInfo(self, self.game, self.square_size, self.square_board)
        self.but_menu = Button(self, (14.5*self.square_size, 18*self.square_size), 'Menu', 
                partial(self.change_page, 'MainMenu'), background_color=(255,255,255,255), font_size=20)

    def start(self, *args, **kw):
        if kw['load']:
            self.game.load_game()
        else:
            self.game.new_game()
        pygame.mixer.music.load('appData/sounds/music.mp3')
        pygame.mixer.music.play(loops=-1)
        self.game.paused = False

    def close(self):
        pygame.mixer.music.stop()
        self.game.save_game()

    def event_handler(self, event):
        self.game.event_handler(event)

    def loop(self):
        self.game.loop()
        self.game_info.update()
        self.draw()



sc_width = 507
sc_height = 619
sc_size = (sc_width, sc_height)


screen = pygame.display.set_mode((sc_width, sc_height))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()
PageManager.set_surf(screen)
MainMenu(sc_size)
OptionsMenu(sc_size)
GamePage(sc_size)
PageManager.set_start_page('MainMenu')
exit = False

while exit == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True
        PageManager.event_handler(event)
        
    
    PageManager.loop()
    
    clock.tick(30)
    pygame.display.update()

pygame.quit()