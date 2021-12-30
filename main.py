import pygame
import sys
import os

pygame.init()
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
size = width, height = 800, 800
screen = pygame.display.set_mode(size)


# Функция для загрузки картинок
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


# Лезет в текстовый файл и добавляет значение каждой буквы в матрицу игрового поля
def create_level(level):
    tiles = open(f'data/{level.name}.txt', mode='r', encoding='UTF-8').read().split()
    for i in tiles:
        level.board.append([j for j in i])
        level.height += 1



# Завершает работу
def terminate():
    pygame.quit()
    sys.exit()


# Класс игрового поля
class Level:
    # создание поля
    def __init__(self, name):
        self.name = name
        self.width = 12
        self.height = 0
        self.board = []
        # значения по умолчанию
        self.cell_size = 60


    # Прорисовка поля
    def render(self, screen):
        for j in range(self.height):
            for i in range(self.width):
                pygame.draw.rect(screen, 'white', (i * self.cell_size,
                                                   j * self.cell_size,
                                                   self.cell_size, self.cell_size), 1)
                if self.board[j][i] == 'B':
                    color = pygame.Color('black')
                elif self.board[j][i] == 'R':
                    color = pygame.Color('brown')
                else:
                    color = pygame.Color('white')

                screen.fill(color, ((i * self.cell_size) + 1,
                                    (j * self.cell_size) + 1,
                                      self.cell_size - 2, self.cell_size - 2))


# класс Персонажа
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super(Player, self).__init__(player_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = player_image
        self.update()

    def move(self, direction):
        if direction == 'left':
            self.pos_x -= 1
        elif direction == 'up':
            self.pos_y -= 1
        elif direction == 'right':
            self.pos_x += 1
        elif direction == 'down':
            self.pos_y += 1
        self.update()

    def update(self):
        self.rect = self.image.get_rect().move(60 * self.pos_x + 15, 60 * self.pos_y + 5)


def game():
    level = Level('level1')
    create_level(level)
    player = Player(5, 2)
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
                    player.move('right')
                elif event.key == pygame.K_DOWN:
                    player.move('down')
        screen.fill((0, 0, 0))
        level.render(screen)
        all_sprites.draw(screen)
        pygame.display.flip()


tile_images = {'B': pygame.color.Color('Black'),
               'R': pygame.color.Color('Red'),
               'W': pygame.color.Color('White')}

player_image = load_image('mario.png')

if __name__ == '__main__':
    game()