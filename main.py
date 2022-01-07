import pygame
import sys
import os
import random

pygame.init()
pygame.display.set_caption('Crossy Road')
clock = pygame.time.Clock()
size = width, height = 600, 660
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
    for i in range(len(objects)):  # Привязывает объекты с другого файла к уровню
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
    global menu_bckgr
    fullname = os.path.join('Общие картинки', 'Фон1.jpg')
    fullname = os.path.join('Картинки', fullname)
    fullname = os.path.join('data', fullname)
    menu_bckgr = pygame.image.load(fullname)
    start_desert_button = Button(200, 50, (190, 233, 221), (180, 255, 235))
    start_jungle_button = Button(200, 50, (190, 233, 221), (180, 255, 235))
    start_winter_button = Button(200, 50, (190, 233, 221), (180, 255, 235))
    start_random_button = Button(200, 50, (190, 233, 221), (180, 255, 235))
    rules_of_the_game_button = Button(345, 57, (190, 233, 221), (180, 255, 235))
    quit_button = Button(100, 60, (190, 233, 221), (180, 255, 235))
    show = True
    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        screen.blit(menu_bckgr, (0, 0))
        pygame.draw.rect(screen, (180, 255, 235), (150, 174, 300, 2), 0)

        font = pygame.font.Font(None, 75)
        text = font.render('Start game', True, (16, 17, 18))
        text_rect = text.get_rect(center=(300, 155))
        screen.blit(text, text_rect)

        start_desert_button.draw(200, 200, 'level "Desert"', start_level_desert, 30)
        pygame.draw.rect(screen, (180, 255, 235), (199, 199, 202, 52), 3)
        start_jungle_button.draw(200, 270, 'level "Jungle"', start_level_jungle, 30)
        pygame.draw.rect(screen, (180, 255, 235), (199, 269, 202, 52), 3)
        start_winter_button.draw(200, 340, 'level "Winter"', start_level_winter, 30)
        pygame.draw.rect(screen, (180, 255, 235), (199, 339, 202, 52), 3)
        start_random_button.draw(200, 410, 'random level', start_level_random, 30)
        pygame.draw.rect(screen, (180, 255, 235), (199, 409, 202, 52), 3)
        rules_of_the_game_button.draw(140, 500, 'Rules of the game', rule_window, 38)
        pygame.draw.rect(screen, (180, 255, 235), (139, 499, 347, 59), 3)
        quit_button.draw(250, 570, 'Quit', terminate, 40)
        pygame.draw.rect(screen, (180, 255, 235), (249, 569, 102, 62), 3)
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


class Player(pygame.sprite.Sprite):  # КЛАСС ПЕРСОНАЖА
    def __init__(self, pos_x, pos_y, level):
        super(Player, self).__init__(player_group, all_sprites)
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
        if self.level.tile_map[self.pos_x][self.pos_y] == 'G':
            create_particles((random.randint(-50, 650), random.randint(-100, 100)))
        elif self.level.tile_map[self.pos_x][self.pos_y] == 'W':
            game_over()
        elif self.level.tile_map[self.pos_x][self.pos_y] == 'R':
            game_over()

    def update(self):
        self.rect = self.image.get_rect().move(self.level.cell_size * self.pos_y + self.level.cell_size * 0.35,
                                               self.level.cell_size * self.pos_x + self.level.cell_size * 0.2)


class Enemy(pygame.sprite.Sprite, Level):  # КЛАСС ПРОТИВНИКА
    def __init__(self, pos_x, pos_y, level):
        super(Enemy, self).__init__(enemy_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = enemy_image
        self.level = level
        self.update()

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


def rule_window():
    back_button = Button(75, 60, (190, 233, 221), (180, 255, 235))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        screen.blit(menu_bckgr, (0, 0))
        back_button.draw(20, 580, '<--', show_menu, 40)
        pygame.draw.rect(screen, (180, 255, 235), (19, 579, 77, 62), 3)
        pygame.display.flip()


def game_over():
    replay_button = Button(130, 60, (190, 233, 221), (180, 255, 235))
    menu_button = Button(130, 60, (190, 233, 221), (180, 255, 235))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        screen.blit(menu_bckgr, (0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render('Game over', True, (16, 17, 18))
        text_rect = text.get_rect(center=(290, 250))
        screen.blit(text, text_rect)

        replay_button.draw(230, 300, 'replay', replay_the_level, 40)
        pygame.draw.rect(screen, (180, 255, 235), (229, 299, 132, 62), 3)
        menu_button.draw(230, 375, 'menu', show_menu, 40)
        pygame.draw.rect(screen, (180, 255, 235), (229, 374, 132, 62), 3)
        pygame.display.flip()


def replay_the_level():
    start_game(current_level)


def start_level_desert():
    global current_level
    current_level = 'level_Desert'
    start_game('level_Desert')


def start_level_jungle():
    global current_level
    current_level = 'level_Jungle'
    start_game('level_Jungle')


def start_level_winter():
    global current_level
    current_level = 'level_Winter'
    start_game('level_Winter')


def start_level_random():
    global current_level
    random_level = ['level_Winter', 'level_Jungle', 'level_Desert']
    current_level = random_level
    start_game(random.choice(random_level))


def start_game(name_level):
    global number_of_cells, screen_rect
    global all_sprites, player_group, enemy_group, collectible_group, asterisks
    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    collectible_group = pygame.sprite.Group()
    asterisks = pygame.sprite.Group()
    number_of_cells = 12
    level = Level(name_level)
    create_level(level)
    screen_rect = (0, 0, width, height)
    pygame.mixer.music.play(-1)
    flPause = False
    vol = 0.5
    pygame.mixer.music.set_volume(vol)

    back_button = Button(75, 50, (190, 233, 221), (180, 255, 235))

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
        screen.blit(menu_bckgr, (0, 0))
        level.render(screen)
        all_sprites.draw(screen)

        asterisks.update()
        asterisks.draw(screen)

        back_button.draw(10, 605, '<--', show_menu, 40)
        pygame.draw.rect(screen, (180, 255, 235), (9, 604, 77, 52), 3)

        clock.tick(50)

        pygame.display.flip()


player_image = load_image('mario.png')
enemy_image = load_image('box.png')
star_image = load_image('star.png')
if __name__ == '__main__':
    show_menu()
