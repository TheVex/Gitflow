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
GRAVITY = 1.5

tile_images = {'B': pygame.color.Color('Black'), # Ничего (Black)
               'R': pygame.color.Color('Red'), # Смерть (Red)
               'W': pygame.color.Color('Blue'), # Вода (Water)
               'G': pygame.color.Color('Green'), # Победа (Green)
               'S': pygame.color.Color('Brown'),} # Стена (Stena ('Wall' начинается как 'Water'))

music_number = 1
music_list = ['музыка1.mp3', 'музыка2.mp3', 'музыка3.mp3', 'музыка4.mp3', 'музыка5.mp3',
              'музыка6.mp3', 'музыка7.mp3', 'музыка8.mp3', 'музыка9.mp3', 'музыка10.mp3']

fullname = os.path.join('data', music_list[music_number])
pygame.mixer.music.load(fullname)


def load_image(name, colorkey=None):  # Функция для загрузки картинок
    fn = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fn):
        print(f"Файл с изображением '{fn}' не найден")
        sys.exit()
    image = pygame.image.load(fn)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def create_level(level):  # Лезет в текстовый файл и добавляет значение каждой буквы в матрицу игрового поля
    tiles = open(f'data/{level.name}.txt', mode='r', encoding='UTF-8').read().split()
    for i in tiles:
        level.board.append([j for j in i])
        level.height += 1


def terminate():  # Завершает работу
    pygame.quit()
    sys.exit()


class Level:  # Класс игрового поля
    def __init__(self, name):  # создание поля
        self.name = name
        self.width = number_of_cells
        self.height = 0
        self.board = []

        self.cell_size = 50  # значения по умолчанию

    def render(self, screen):  # Прорисовка поля
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, 'white', (j * self.cell_size,
                                                   i * self.cell_size,
                                                   self.cell_size, self.cell_size), 1)

                screen.fill(tile_images[self.board[i][j]], ((j * self.cell_size) + 1,
                                    (i * self.cell_size) + 1,
                                    self.cell_size - 2, self.cell_size - 2))


class Player(pygame.sprite.Sprite):  # класс Персонажа
    def __init__(self, pos_x, pos_y, level):
        super(Player, self).__init__(player_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = player_image
        self.cell_size = level.cell_size
        self.board = level.board
        self.update()

    def move(self, direction):
        if direction == 'left' and self.board[self.pos_y][self.pos_x - 1] != 'S':
            if self.pos_x != 0:
                self.pos_x -= 1
        elif direction == 'up' and self.board[self.pos_y - 1][self.pos_x] != 'S':
            if self.pos_y != 0:
                self.pos_y -= 1
        elif direction == 'right' and self.board[self.pos_y][self.pos_x + 1] != 'S':
            if self.pos_x != number_of_cells:
                self.pos_x += 1
        elif direction == 'down' and self.board[self.pos_y + 1][self.pos_x] != 'S':
            if self.pos_y != number_of_cells:
                self.pos_y += 1
        self.update()

    def on_tile(self, level):
        if level.board[self.pos_y][self.pos_x] == 'G':
            create_particles((random.randint(-50, 650), random.randint(-100, 100)))
        elif level.board[self.pos_y][self.pos_x] == 'W':
            print('Game over! (Пока интерфейс не написан)')
            terminate()
        elif level.board[self.pos_y][self.pos_x] == 'R':
            print('Game over! (Пока интерфейс не написан)')
            terminate()

    def update(self):
        self.rect = self.image.get_rect().move(self.cell_size * self.pos_x + self.cell_size * 0.35,
                                               self.cell_size * self.pos_y + self.cell_size * 0.2)


class Particle(pygame.sprite.Sprite):
    fire = [load_image("star.png")]  # сгенерируем частицы разного размера
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(asterisks)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]  # у каждой частицы своя скорость — это вектор
        self.rect.x, self.rect.y = pos  # и свои координаты
        self.gravity = GRAVITY  # гравитация будет одинаковой (значение константы)

    def update(self):
        self.velocity[1] += self.gravity  # применяем гравитац. эффект: движение с ускорением под действием гравитации
        self.rect.x += self.velocity[0]  # перемещаем частицу
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):  # убиваем, если частица ушла за экран
            self.kill()


def create_particles(position):
    particle_count = 20  # количество создаваемых частиц
    numbers = range(-5, 6)  # возможные скорости
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


player_image = load_image('mario.png')

if __name__ == '__main__':
    number_of_cells = 12
    level = Level('level1')
    create_level(level)
    player = Player(6, 10, level)   # надо сделать так чтобы менялось в зависимости от уровня
    finish_point_x = 0   # надо сделать так чтобы менялось в зависимости от уровня
    finish_point_y = 0   # надо сделать так чтобы менялось в зависимости от уровня

    screen_rect = (0, 0, width, height)

    pygame.mixer.music.play(-1)
    flPause = False
    vol = 0.5
    pygame.mixer.music.set_volume(vol)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:  # создаём частицы по щелчку мыши
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
                elif event.key == pygame.K_w:  # переключение музыки
                    music_number += 1
                    if music_number == 10:
                        music_number = 0
                    fullname = os.path.join('data', music_list[music_number])
                    pygame.mixer.music.load(fullname)
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_s:
                    music_number -= 1
                    if music_number == -1:
                        music_number = 9
                    fullname = os.path.join('data', music_list[music_number])
                    pygame.mixer.music.load(fullname)
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(vol)
        player.on_tile(level)
        screen.fill((0, 0, 0))
        level.render(screen)
        player_group.draw(screen)

        asterisks.update()
        asterisks.draw(screen)
        pygame.display.flip()
        clock.tick(50)

        pygame.display.flip()
