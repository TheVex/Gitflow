import pygame
import sys
import os

pygame.init()
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
size = width, height = 800, 800
screen = pygame.display.set_mode(size)

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def create_level(level):
    if level == 'level1':
        level.add_line(['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'])
        level.add_line(['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'])
        level.add_line()


def terminate():
    pygame.quit()
    sys.exit()


class Level:
    # создание поля
    def __init__(self, width):
        self.width = width
        self.height = 0
        self.board = []
        # значения по умолчанию
        self.left = 100
        self.top = 100
        self.cell_size = 60

    def render(self, screen):
        for j in range(self.height):
            for i in range(self.width):
                pygame.draw.rect(screen, 'white', (self.left + i * self.cell_size,
                                                   self.top + j * self.cell_size,
                                                   self.cell_size, self.cell_size), 1)
                if self.board[j][i] == 'B':
                    color = pygame.Color('black')
                elif self.board[j][i] == 'R':
                    color = pygame.Color('brown')
                else:
                    color = pygame.Color('white')

                screen.fill(color, ((self.left + i * self.cell_size) + 1,
                                    (self.top + j * self.cell_size) + 1,
                                      self.cell_size - 2, self.cell_size - 2))

    def add_line(self, line):
        self.board.insert(-1, line)
        self.height += 1

# класс Персонажа
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super(Player, self).__init__(player_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = player_image
        self.rect = self.image.get_rect().move(60 * pos_x + 15, 60 * pos_y + 5)

    def move(self, direction):
        pass


def game():


    level = Level(8)
    create_level('level1')
    player = Player(0, 2)
    running = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move('left')
                elif event.key == pygame.K_UP:
                    player.move('up')
                elif event.key == pygame.K_RIGHT:
                    player.move('left')
        screen.fill((0, 0, 0))
        level.render(screen)
        pygame.display.flip()

tile_images = {'B': pygame.color.Color('Black'),
               'R': pygame.color.Color('Red'),
               'W': pygame.color.Color('White')}

player_image = load_image('mario.png')

if __name__ == '__main__':
    game()