import pygame
import sys
import os
import random

pygame.init()
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
asterisks = pygame.sprite.Group()
clock = pygame.time.Clock()
size = width, height = 600, 600
screen = pygame.display.set_mode(size)

GRAVITY = 1
fullname = os.path.join('data', "музыка1.mp3")
pygame.mixer.music.load(fullname)

def load_image(name, colorkey=None): # Функция для загрузки картинок
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

def create_level(level): # Лезет в текстовый файл и добавляет значение каждой буквы в матрицу игрового поля
    tiles = open(f'data/{level.name}.txt', mode='r', encoding='UTF-8').read().split()
    for i in tiles:
        level.board.append([j for j in i])
        level.height += 1


def terminate(): # Завершает работу
    pygame.quit()
    sys.exit()

class Level: # Класс игрового поля
    def __init__(self, name): # создание поля
        self.name = name
        self.width = number_of_cells
        self.height = 0
        self.board = []

        self.cell_size = 75 # значения по умолчанию

    def render(self, screen): # Прорисовка поля
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

class Player(pygame.sprite.Sprite): # класс Персонажа
    def __init__(self, pos_x, pos_y):
        super(Player, self).__init__(player_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = player_image
        self.update()

    def move(self, direction):
        if direction == 'left':
            if self.pos_x != 0:
                self.pos_x -= 1
        elif direction == 'up':
            if self.pos_y != 0:
                self.pos_y -= 1
        elif direction == 'right':
            if self.pos_x != number_of_cells:
                self.pos_x += 1
        elif direction == 'down':
            if self.pos_y != number_of_cells:
                self.pos_y += 1
        self.update()

    def update(self):
        self.rect = self.image.get_rect().move(60 * self.pos_x + 15, 60 * self.pos_y + 5)


class Particle(pygame.sprite.Sprite):
    fire = [load_image("star.png")] # сгенерируем частицы разного размера
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(asterisks)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy] # у каждой частицы своя скорость — это вектор
        self.rect.x, self.rect.y = pos # и свои координаты
        self.gravity = GRAVITY # гравитация будет одинаковой (значение константы)

    def update(self):
        self.velocity[1] += self.gravity # применяем гравитационный эффект: # движение с ускорением под действием гравитации
        self.rect.x += self.velocity[0] # перемещаем частицу
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect): # убиваем, если частица ушла за экран
            self.kill()

def create_particles(position):
    particle_count = 20 # количество создаваемых частиц
    numbers = range(-5, 6) # возможные скорости
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


tile_images = {'B': pygame.color.Color('Black'),
               'R': pygame.color.Color('Red'),
               'W': pygame.color.Color('White')}

player_image = load_image('mario.png')

if __name__ == '__main__':
    number_of_cells = 9
    level = Level('level1')
    create_level(level)
    player = Player(5, 2)  ##### надо сделать так чтобы менялось в зависимости от уровня
    finish_point_x = 7  ##### надо сделать так чтобы менялось в зависимости от уровня
    finish_point_y = 8  ##### надо сделать так чтобы менялось в зависимости от уровня

    screen_rect = (0, 0, width, height)

    pygame.mixer.music.play(-1)
    flPause = False
    vol = 0.5
    pygame.mixer.music.set_volume(vol)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN: # создаём частицы по щелчку мыши
                create_particles(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move('left')
                elif event.key == pygame.K_UP:
                    player.move('up')
                elif event.key == pygame.K_RIGHT:
                    player.move('right')
                elif event.key == pygame.K_DOWN:
                    player.move('down')

                elif event.key == pygame.K_SPACE:  # остановка музыки
                    flPause = not flPause
                    if flPause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()

                elif event.key == pygame.K_a:  # изменение громкости звука
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_d:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
        screen.fill((0, 0, 0))
        level.render(screen)
        player_group.draw(screen)


        asterisks.update()
        asterisks.draw(screen)
        pygame.display.flip()
        clock.tick(50)

        pygame.display.flip()