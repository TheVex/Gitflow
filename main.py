import pygame
import sys
import os
import random

pygame.init()

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
collectible_group = pygame.sprite.Group()
asterisks = pygame.sprite.Group()

clock = pygame.time.Clock()
size = width, height = 600, 600
screen = pygame.display.set_mode(size)
GRAVITY = 1.5

tile_images = {'B': pygame.color.Color('Black'),  # Ничего (Black)
               'R': pygame.color.Color('Red'),  # Смерть (Red)
               'W': pygame.color.Color('Blue'),  # Вода (Water)
               'G': pygame.color.Color('Green'),  # Победа (Green)
               'S': pygame.color.Color('Brown'), }  # Стена (Stena ('Wall' начинается как 'Water'))

music_number = 1
music_list = ['музыка1.mp3', 'музыка2.mp3', 'музыка3.mp3', 'музыка4.mp3', 'музыка5.mp3',
              'музыка6.mp3', 'музыка7.mp3', 'музыка8.mp3', 'музыка9.mp3', 'музыка10.mp3']

fullname1 = os.path.join('data', music_list[music_number])
pygame.mixer.music.load(fullname1)
fullname2 = os.path.join('data', 'button.wav')
button_sound = pygame.mixer.Sound(fullname2)


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
    tiles = open(f'data/{level.name}/level_tilemap.txt', mode='r', encoding='UTF-8').read().split()
    for i in tiles:
        level.tile_map.append([j for j in i])
        level.height += 1

    objects = open(f'data/{level.name}/level_objectmap.txt', mode='r', encoding='UTF-8').read().split()
    for i in range(len(objects)): # Привязывает объекты с другого файла к уровню
        for j in range(len(objects[i])):
            if objects[i][j] == '.':
                continue
            elif objects[i][j] == 'O':
                level.collectible_list.append(Collectible(i, j, level))
            elif objects[i][j] == 'E':
                level.enemy_list.append(Enemy(i, j, level))
            elif objects[i][j] == 'P':
                level.player = Player(i, j, level)



def create_particles(position):
    particle_count = 20  # количество создаваемых частиц
    numbers = range(-5, 6)  # возможные скорости
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def terminate():  # Завершает работу
    pygame.quit()
    sys.exit()


def show_menu():
    fullname = os.path.join('data', 'Menu2.jpg')
    menu_bckgr = pygame.image.load(fullname)
    start_button = Button(288, 70, (241, 219, 255), (255, 255, 255))
    quit_button = Button(120, 70, (255, 255, 255), (255, 255, 255))

    show = True
    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        screen.blit(menu_bckgr, (0, 0))
        start_button.draw(270, 200, 'Start game', start_game, 50)
        quit_button.draw(358, 300, 'Quit', terminate, 50)
        pygame.display.update()
        clock.tick(60)


def print_text(message, x, y, font_colour=(20, 20, 20), font_type='PingPong.ttf', font_size=30):
    font_type = os.path.join('data', font_type)
    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(message, True, font_colour)
    screen.blit(text, (x, y))


class Level:  # Класс игрового поля
    def __init__(self, name):  # создание поля
        self.name = name
        self.width = number_of_cells
        self.height = 0

        self.tile_map = []

        self.enemy_list = []
        self.collectible_list = []

        self.cell_size = 50  # значения по умолчанию

    def render(self, screen):  # Прорисовка поля
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, 'white', (j * self.cell_size,
                                                   i * self.cell_size,
                                                   self.cell_size, self.cell_size), 1)

                screen.fill(tile_images[self.tile_map[i][j]], ((j * self.cell_size) + 1,
                                                            (i * self.cell_size) + 1,
                                                            self.cell_size - 2, self.cell_size - 2))

                for m in self.enemy_list:
                    m.update()

                for n in self.collectible_list:
                    n.update()





    def is_free(self, y, x, only_wall=True):
        if only_wall:
            if self.tile_map[x][y] != 'S':
                return True
            return False
        if self.tile_map[x][y] == 'B':
            return True
        return False



class Player(pygame.sprite.Sprite):  # класс Персонажа
    def __init__(self, pos_x, pos_y, level):
        super(Player, self).__init__(enemy_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = player_image
        self.level = level
        self.update()

    def move(self, direction):
        if direction == 'up' and self.pos_x != 0:
            if self.level.is_free(self.pos_y, self.pos_x - 1):
                self.pos_x -= 1
        elif direction == 'left' and self.pos_y != 0:
            if self.level.is_free(self.pos_y - 1, self.pos_x):
                self.pos_y -= 1
        elif direction == 'down' and self.pos_x != number_of_cells - 1:
            if self.level.is_free(self.pos_y, self.pos_x + 1):
                self.pos_x += 1
        elif direction == 'right' and self.pos_y != number_of_cells - 1:
            if self.level.is_free(self.pos_y + 1, self.pos_x):
                self.pos_y += 1
        self.update()

    def on_tile(self):
        if self.level.tile_map[self.pos_y][self.pos_x] == 'G':
            create_particles((random.randint(-50, 650), random.randint(-100, 100)))
        elif self.level.tile_map[self.pos_y][self.pos_x] == 'W':
            pass
        elif self.level.tile_map[self.pos_y][self.pos_x] == 'R':
            pass

    def update(self):
        self.rect = self.image.get_rect().move(self.level.cell_size * self.pos_y + self.level.cell_size * 0.35,
                                               self.level.cell_size * self.pos_x + self.level.cell_size * 0.2)


class Enemy(pygame.sprite.Sprite, Level):  # Класс противника
    def __init__(self, pos_x, pos_y, level):
        super(Enemy, self).__init__(enemy_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = enemy_image
        self.level = level
        self.update()

    def move(self, direction):
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
        self.rect = self.image.get_rect().move(self.level.cell_size * self.pos_y + self.level.cell_size * 0.35,
                                               self.level.cell_size * self.pos_x + self.level.cell_size * 0.2)


class Collectible(pygame.sprite.Sprite):  # Класс собираемых объектов (пока не знаю каких, Даша - решай)
    def __init__(self, pos_x, pos_y, level):
        super(Collectible, self).__init__(collectible_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = star_image
        self.level = level
        self.update()

    def update(self):
        self.rect = self.image.get_rect().move(self.level.cell_size * self.pos_y + self.level.cell_size * 0.35,
                                               self.level.cell_size * self.pos_x + self.level.cell_size * 0.2)


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


class Button:
    def __init__(self, width_button, height_button, inactive_color, active_color):
        self.width_button = width_button
        self.height_button = height_button
        self.inactive_color = inactive_color
        self.active_color = active_color

    def draw(self, x, y, message, action=None, font_size=30):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width_button and y < mouse[1] < y + self.height_button:
            pygame.draw.rect(screen, self.active_color, (x, y, self.width_button, self.height_button))

            if click[0] == 1:
                pygame.mixer.Sound.play(button_sound)
                pygame.time.delay(300)
                if action is not None:
                    action()
        else:
            pygame.draw.rect(screen, self.inactive_color, (x, y, self.width_button, self.height_button))

        print_text(message=message, x=x + 10, y=y + 10, font_size=font_size)


def start_game():
    global number_of_cells, screen_rect
    number_of_cells = 12
    level = Level('level1')
    create_level(level)

    screen_rect = (0, 0, width, height)

    pygame.mixer.music.play(-1)
    flPause = False
    vol = 0.5
    pygame.mixer.music.set_volume(vol)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    level.player.move('left')
                elif event.key == pygame.K_UP:
                    level.player.move('up')
                elif event.key == pygame.K_RIGHT:
                    level.player.move('right')
                elif event.key == pygame.K_DOWN:
                    level.player.move('down')

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

        level.player.on_tile()
        screen.fill((0, 0, 0))
        level.render(screen)
        player_group.draw(screen)
        all_sprites.draw(screen)

        asterisks.update()
        asterisks.draw(screen)
        pygame.display.flip()
        clock.tick(50)

        pygame.display.flip()


player_image = load_image('mario.png')
enemy_image = load_image('box.png')
star_image = load_image('star.png')
if __name__ == '__main__':
    show_menu()
