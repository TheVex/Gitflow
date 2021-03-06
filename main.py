import pygame  # подключение библиотек
import sys
import os
import random
import pytmx
import time
import sqlite3

pygame.init()

clock = pygame.time.Clock()
size = width, height = 640, 704
screen = pygame.display.set_mode(size)
GRAVITY = 0.5
ENEMY_EVENT_TYPE = pygame.USEREVENT + 1
COUNTDOWN_EVENT_TYPE = pygame.USEREVENT + 2
UPDATE_ANIMATION_TYPE = pygame.USEREVENT + 3
INF = 1000

number_of_lives = 3
fullname1 = os.path.join('data', 'музыка1.mp3')  # открытие файла с фоновой музыкой
pygame.mixer.music.load(fullname1)  # подключение фоновой музыки
fullname2 = os.path.join('data', 'button.wav')  # открытие файла со звуком нажатия на кнопу
button_sound = pygame.mixer.Sound(fullname2)
pygame.mixer.music.play(-1)
vol = 0.5  # громкость музыки
pygame.mixer.music.set_volume(vol)
flPause = False  # флаг включена/выключена музыка
current_level = None
screen_rect = None
final_points = None


def load_image(name, colorkey=None):  # Функция для загрузки картинок
    fn = os.path.join('data', name)
    if not os.path.isfile(fn):  # если файл не существует, то выходим
        print(f"Файл с изображением '{fn}' не найден")
        sys.exit()
    im = pygame.image.load(fn)
    if colorkey is not None:
        im = im.convert()
        if colorkey == -1:
            colorkey = im.get_at((0, 0))
        im.set_colorkey(colorkey)
    else:
        im = im.convert_alpha()
    return im


# Cловарь который присоединяет все объекты в игре к своим уровням
GAME_BASE = {'winter_map': {'player': (10, 16),  # Координаты игрока
                            'free_tiles': [27, 30, 59, 60, 44],  # Свободные плитки
                            'win_tile': 44,  # Победная плитка
                            'death_tiles': [],  # Смертельные плитки
                            'enemies_list': [[True, [(12, 15), (12, 17), (17, 15), (17, 17)]],
                                             [True, [(7, 15), (7, 17), (2, 17), (2, 15)]],
                                             [True, [(13, 9), (13, 7), (18, 7), (18, 9)]],
                                             [True, [(6, 9), (6, 7), (1, 7), (1, 9)]],
                                             [False, [(1, 1)]],
                                             [False, [(18, 1)]]],  # Список координат появления противников
                            'enemy_image': load_image('winter_map/Yeti.png'),  # Картинка противника
                            'enemy_size': (6, 8),  # Количество кадров противника по горизонтали и вертикали
                            'points': {59: 5, 60: 50},
                            # Количество очков, получаемых при сборе предмета (в виде "ID_предмета: кол_очков")
                            'countdown': 120},  # Таймер, в секундах


             'desert_map': {'player': (9, 1),
                            'free_tiles': [19, 43, 20, 0, 42, 4, 163, 376, 377],
                            'win_tile': 163,
                            'death_tiles': [169, 170],
                            'enemies_list': [[True, [(5, 9), (9, 9), (9, 7), (5, 7)]],
                                             [True, [(14, 9), (10, 9), (10, 7), (14, 7)]],
                                             [True, [(5, 12), (5, 17), (8, 17), (8, 12)]],
                                             [True, [(14, 12), (14, 17), (11, 17), (11, 12)]],
                                             [False, [(4, 18)]],
                                             [False, [(15, 18)]]],
                            'enemy_image': load_image('desert_map/Shaman.png'),
                            'enemy_size': (6, 8),
                            'points': {377: 50, 376: 5},
                            'countdown': 120},

             'city_map': {'player': (1, 9),
                          'free_tiles': [0, 232, 235, 241, 177, 179, 142, 9],
                          'win_tile': 9,
                          'death_tiles': [142],
                          'enemies_list': [[True, [(11, 7), (17, 7), (17, 12), (11, 12)]],
                                           [True, [(3, 8), (3, 1)]],
                                           [True, [(14, 15), (14, 17), (17, 17), (17, 15)]],
                                           [True, [(14, 4), (14, 2), (17, 2), (17, 4)]],
                                           [True, [(3, 11), (3, 18)]],
                                           [True, [(7, 1), (7, 9)]],
                                           [True, [(7, 18), (7, 10)]],
                                           [True, [(17, 12), (11, 12), (11, 7), (17, 7)]]],
                          'enemy_image': load_image('city_map/Axeman.png'),
                          'enemy_size': (6, 6),
                          'points': {235: 50, 232: 5},
                          'countdown': 120}}

fullname = os.path.join('Общие картинки', 'Меню71.png')  # картинка находящаяся на кнопке выхода в меню
fullname = os.path.join('Картинки', fullname)
all_sprites_menu = pygame.sprite.Group()
sprite = pygame.sprite.Sprite()
image = load_image(fullname, -1)
sprite.image = pygame.transform.scale(image, (45, 45))
sprite.rect = sprite.image.get_rect()
all_sprites_menu.add(sprite)
sprite.rect.x = 12
sprite.rect.y = 645


def create_particles(position):  # создание звездочек в случае победы
    particle_count = 1  # количество создаваемых частиц
    numbers = range(-5, 2)  # возможные скорости
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def terminate():  # Завершает работу
    pygame.quit()
    sys.exit()


def show_menu():  # окно меню
    global flPause, vol, menu_bckgr
    full_name = os.path.join('Общие картинки', 'Фон1.jpg')  # подключение фона
    full_name = os.path.join('Картинки', full_name)
    full_name = os.path.join('data', full_name)
    menu_bckgr = pygame.image.load(full_name)

    play_game_button = Button(250, 60, (190, 233, 221), (180, 255, 235))  # создание кнопок
    records_button = Button(250, 60, (190, 233, 221), (180, 255, 235))
    rules_of_the_game_button = Button(250, 60, (190, 233, 221), (180, 255, 235))
    quit_button = Button(250, 60, (190, 233, 221), (180, 255, 235))
    show = True
    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # остановка музыки
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
        screen.blit(menu_bckgr, (0, 0))
        font = pygame.font.Font(None, 110)  # Надпись 'Run or die'
        text = font.render('Run or die', True, (0, 0, 0))
        text_rect = text.get_rect(center=(320, 200))
        screen.blit(text, text_rect)

        play_game_button.draw(200, 300, '', play, 38)  # прорисовка кнопок
        pygame.draw.rect(screen, (180, 255, 235), (199, 299, 252, 62), 3)
        font_type = os.path.join('data', 'PingPong.ttf')
        font_type = pygame.font.Font(font_type, 40)
        text = font_type.render('Play', True, (20, 20, 20))
        screen.blit(text, text.get_rect(center=(325, 330)))

        records_button.draw(200, 380, '', record, 38)  # прорисовка кнопок
        pygame.draw.rect(screen, (180, 255, 235), (199, 379, 252, 62), 3)
        font_type = os.path.join('data', 'PingPong.ttf')
        font_type = pygame.font.Font(font_type, 40)
        text = font_type.render('Records', True, (20, 20, 20))
        screen.blit(text, text.get_rect(center=(325, 410)))

        rules_of_the_game_button.draw(200, 460, '', rule_window, 38)  # прорисовка кнопок
        pygame.draw.rect(screen, (180, 255, 235), (199, 459, 252, 62), 3)
        font_type = os.path.join('data', 'PingPong.ttf')
        font_type = pygame.font.Font(font_type, 40)
        text = font_type.render('Rules', True, (20, 20, 20))
        screen.blit(text, text.get_rect(center=(325, 490)))

        quit_button.draw(200, 540, '', terminate, 38)  # прорисовка кнопок
        pygame.draw.rect(screen, (180, 255, 235), (199, 539, 252, 62), 3)
        font_type = os.path.join('data', 'PingPong.ttf')
        font_type = pygame.font.Font(font_type, 40)
        text = font_type.render('Exit', True, (20, 20, 20))
        screen.blit(text, text.get_rect(center=(325, 570)))

        pygame.display.update()
        clock.tick(60)


def play():  # окно для выбора уровня
    global menu_bckgr, flPause, vol
    full_name = os.path.join('Общие картинки', 'Фон1.jpg')  # подключение фона
    full_name = os.path.join('Картинки', full_name)
    full_name = os.path.join('data', full_name)
    menu_bckgr = pygame.image.load(full_name)

    menu_button = Button(50, 45, (190, 233, 221), (180, 255, 235))
    start_button = Button(200, 200, (190, 233, 221), (180, 255, 235))  # создание кнопок уровней

    all_sprites_button = pygame.sprite.Group()

    full_name = os.path.join('Пустыня', 'Верблюд.png')  # открытие картинок, находящихся на кнопках
    full_name = os.path.join('Картинки', full_name)
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name)
    sprite_file.image = pygame.transform.scale(image_file, (150, 150))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_button.add(sprite_file)
    sprite_file.rect.x = 85
    sprite_file.rect.y = 170

    full_name = os.path.join('Джунгли', 'пугало.png')  # открытие картинок, находящихся на кнопках
    full_name = os.path.join('Картинки', full_name)
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name)
    sprite_file.image = pygame.transform.scale(image_file, (150, 150))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_button.add(sprite_file)
    sprite_file.rect.x = 400
    sprite_file.rect.y = 170

    full_name = os.path.join('Зима', 'Снеговик1.jpg')
    full_name = os.path.join('Картинки', full_name)
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name)
    sprite_file.image = pygame.transform.scale(image_file, (140, 140))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_button.add(sprite_file)
    sprite_file.rect.x = 100
    sprite_file.rect.y = 420

    full_name = os.path.join('Общие картинки', 'вопрос.png')
    full_name = os.path.join('Картинки', full_name)
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name)
    sprite_file.image = pygame.transform.scale(image_file, (140, 140))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_button.add(sprite_file)
    sprite_file.rect.x = 415
    sprite_file.rect.y = 420

    show = True
    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # остановка музыки
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

        screen.blit(menu_bckgr, (0, 0))

        font = pygame.font.Font(None, 70)  # Надпись 'Выберите уровень'
        text = font.render('Выберите уровень', True, (16, 17, 18))
        text_rect = text.get_rect(center=(320, 70))
        screen.blit(text, text_rect)
        pygame.draw.rect(screen, (180, 255, 235), (70, 100, 500, 2), 0)

        menu_button.draw(10, 645, '', show_menu, 40)  # прорисовка кнопок
        pygame.draw.rect(screen, (180, 255, 235), (9, 644, 52, 47), 3)

        start_button.draw(70, 150, '', start_level_desert, 30)  # Прорисовка кнопок уровней
        pygame.draw.rect(screen, (180, 255, 235), (69, 149, 202, 202), 3)
        font = pygame.font.Font(None, 30)
        text = font.render('level "Desert"', True, (16, 17, 18))
        text_rect = text.get_rect(center=(170, 330))
        screen.blit(text, text_rect)

        start_button.draw(370, 150, '', start_level_city, 30)  # Прорисовка кнопок уровней
        pygame.draw.rect(screen, (180, 255, 235), (369, 149, 202, 202), 3)
        font = pygame.font.Font(None, 30)
        text = font.render('level "Village"', True, (16, 17, 18))
        text_rect = text.get_rect(center=(470, 330))
        screen.blit(text, text_rect)

        start_button.draw(70, 400, '', start_level_winter, 30)  # Прорисовка кнопок уровней
        pygame.draw.rect(screen, (180, 255, 235), (69, 399, 202, 202), 3)
        font = pygame.font.Font(None, 30)
        text = font.render('level "Winter"', True, (16, 17, 18))
        text_rect = text.get_rect(center=(170, 580))
        screen.blit(text, text_rect)

        start_button.draw(370, 400, '', start_level_random, 30)  # Прорисовка кнопок уровней
        pygame.draw.rect(screen, (180, 255, 235), (369, 399, 202, 202), 3)
        font = pygame.font.Font(None, 30)
        text = font.render('random level', True, (16, 17, 18))
        text_rect = text.get_rect(center=(470, 580))
        screen.blit(text, text_rect)

        all_sprites_button.draw(screen)
        all_sprites_menu.draw(screen)

        pygame.display.update()
        clock.tick(60)


def print_text(message, x, y, font_colour=(20, 20, 20), font_type='PingPong.ttf',
               font_size=30):  # функция для написание текста на кнопках
    font_type = os.path.join('data', font_type)
    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(message, True, font_colour)
    screen.blit(text, (x, y))


class Level:  # Класс игрового поля
    def __init__(self, name, free_tiles, finish_tile, collectible_tiles, death_tiles):  # создание поля
        self.name = name
        self.free_tiles = free_tiles + death_tiles
        self.finish_tile = finish_tile
        self.collectible_tiles = collectible_tiles
        self.death_tiles = death_tiles
        filename = os.path.join('data', f'{name}', f'{name}.tmx')

        self.tile_map = pytmx.load_pygame(filename)
        self.height = self.tile_map.height
        self.width = self.tile_map.width

        self.tile_size = self.tile_map.tilewidth
        self.points = 0

        self.collectible_list = {}
        for y in range(self.height):  # Проверяет, доступна ли клетка для сбора и добавляет в список предметов для сбора
            for x in range(self.width):
                pos_tile = self.get_tile_id((x, y))
                if pos_tile in self.collectible_tiles.keys():
                    self.collectible_list[(x, y)] = Collectible((x, y), self.collectible_tiles[pos_tile])

    def render(self):  # Прорисовка поля, а также предметов сбора, если они не собраны
        for y in range(self.height):
            for x in range(self.width):
                flag = False

                image1 = self.tile_map.get_tile_image(x, y, 0)
                screen.blit(image1, (x * self.tile_size, y * self.tile_size))

                try:
                    image2 = self.tile_map.get_tile_image(x, y, 1)
                    if (x, y) in self.collectible_list.keys():
                        flag = True
                    if flag or self.get_tile_id((x, y)) not in self.collectible_tiles.keys():
                        screen.blit(image2, (x * self.tile_size, y * self.tile_size))
                except (TypeError, KeyError):
                    pass

    def find_path_step(self, start, target):  # Функция ИИ у противников
        x, y = start
        distance = [[INF] * self.width for _ in range(self.height)]
        distance[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.width and 0 <= next_y < self.height \
                        and self.is_free((next_x, next_y), True) and distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y

    def get_tile_id(self, position):  # Возвращает ID клетки (узнать чем эта клетка является)
        try:
            return self.tile_map.tiledgidmap[self.tile_map.get_tile_gid(*position, 1)]
        except (KeyError, ValueError):
            return 0

    def is_free(self, position, enemy=False):  # Проверяет, свободна ли клетка
        if enemy:
            return self.get_tile_id(position) in self.free_tiles and self.get_tile_id(position) not in self.death_tiles
        return self.get_tile_id(position) in self.free_tiles

    def collect(self, pos):  # Добавление очков за предмет и удаление этого предмета с экрана
        global points
        item = self.collectible_list[pos]
        self.points += item.points
        del self.collectible_list[pos]


class Player(pygame.sprite.Sprite):  # Класс игрока
    def __init__(self, pos, image):
        super(Player, self).__init__(player_group, all_sprites)
        self.pos_x, self.pos_y = pos
        self.start_pos = pos
        self.image = image

    def get_pos(self):  # Возвращает координаты игрока
        return self.pos_x, self.pos_y

    def set_pos(self, pos):  # Устанавливает координаты игрока
        self.pos_x, self.pos_y = pos

    def render(self, level):  # Ставит игрока на поле
        self.rect = self.image.get_rect().move(level.tile_size * self.pos_x,
                                               level.tile_size * self.pos_y)


class Enemy(pygame.sprite.Sprite):  # Класс противника
    def __init__(self, pos, level, sheet,
                 size, patrol=False):  # принимает в себя картинку, состоящую из нескольких картинок для анимации
        super(Enemy, self).__init__(enemy_group, all_sprites)  # и размер, который будет взят для анимирования
        self.pos_x, self.pos_y = pos[0]
        self.start_pos = pos[0]
        self.pos = pos
        self.level = level

        self.patrol = patrol  # Определяет тип противника. False: преследует игрока. True: идёт по заданному пути
        if self.patrol:
            self.patrol_coord = self.pos[0]

        self.delay = 600
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)
        self.frames = []
        self.cut_sheet(sheet, size[0], size[1])
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):  # Создаёт список кадров для анимации
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(1):
            for i in range(5):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def render(self):  # Ставит противника на поле
        self.rect = self.image.get_rect().move(self.level.tile_size * self.pos_x,
                                               self.level.tile_size * self.pos_y)

    def update_frame(self):  # Анимирует противника. Вызывается в определенный промежуток времени
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def get_pos(self):  # Возвращает координаты противника
        return self.pos_x, self.pos_y

    def set_pos(self, pos):  # Устанавливает координаты противника
        self.pos_x, self.pos_y = pos


class Collectible:  # Класс собираемых объектов (в зависимости от уровня)
    def __init__(self, pos, points):
        self.pos_x, self.pos_y = pos
        self.points = points

    def get_pos(self):  # Возвращает координаты предмета
        return self.pos_x, self.pos_y


class Game:  # Класс, объединяющий уровень, противников, игрока и предметы сбора.
    def __init__(self, level, player,
                 enemy_list):  # Принимает экземпляры классов уровня, игрока и список экземпляров класса противника
        self.level = level
        self.player = player
        self.enemy_list = enemy_list

    def render(self):  # Общая прорисовка: Вызывает метод render у всех зависимых объектов
        self.level.render()
        self.player.render(self.level)
        for i in self.enemy_list:
            i.render()
        self.check_tile()
        self.check_collide()

    def move_player(self):  # Отвечает за перемещение игрока
        next_x, next_y = self.player.get_pos()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        elif pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        elif pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.level.is_free((next_x, next_y)):  # проверка, может ли игрок наступить на плитку
            self.player.set_pos((next_x, next_y))
            self.check_on_bug()

    def check_on_bug(self):  # Убирает жизнь если игрок выйдет за пределы экрана
        if self.player.pos_x < 0 or self.player.pos_y < 0 or self.player.pos_x > 20 or self.player.pos_y > 20:
            self.decrease_live()

    def check_collide(self):  # Проверяет столкновение игрока с противником
        if pygame.sprite.spritecollideany(self.player, enemy_group):
            self.decrease_live()

    def check_tile(self):  # Функция реагирует на некоторые клетки
        if self.level.get_tile_id(
                self.player.get_pos()) == self.level.finish_tile:  # Реакция в случае попадания на победную плитку
            win_window()
        elif self.level.get_tile_id(self.player.get_pos()) in self.level.collectible_tiles.keys() and \
                self.player.get_pos() in self.level.collectible_list.keys():  # В случае попадания на клетку с предметом
            self.level.collect(self.player.get_pos())
        elif self.level.get_tile_id(self.player.get_pos()) in self.level.death_tiles:
            self.decrease_live()  # В случае попадания на смертельную плитку

    def move_enemy(self, enemy):  # Отвечает за перемещение противника
        if enemy.patrol:
            next_position = self.level.find_path_step(enemy.get_pos(), enemy.patrol_coord)
            if next_position == enemy.get_pos():
                enemy.patrol_coord = enemy.pos[(enemy.pos.index(enemy.patrol_coord) + 1) % len(enemy.pos)]
            enemy.pos_x, enemy.pos_y = next_position
        else:
            next_position = self.level.find_path_step(enemy.get_pos(), self.player.get_pos())
            for i in self.enemy_list:
                t_pos = i.get_pos()
                if t_pos == next_position and not i.patrol:
                    return
            enemy.pos_x, enemy.pos_y = next_position

    def decrease_live(self):  # Уменьшает количество жизней
        global number_of_lives
        number_of_lives -= 1
        if number_of_lives < 1:
            game_over()
        self.player.set_pos(self.player.start_pos)
        for i in self.enemy_list:
            i.set_pos(i.start_pos)


class Particle(pygame.sprite.Sprite):  # класс звездочек, появляющихся при победе
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


class Button:  # создания кнопок
    def __init__(self, width_button, height_button, inactive_color, active_color):
        self.width_button = width_button
        self.height_button = height_button
        self.inactive_color = inactive_color
        self.active_color = active_color

    def draw(self, x, y, message, action=None, font_size=30):  # порисовка кнопок
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width_button and y < mouse[1] < y + self.height_button:  # проверка положения курсора
            pygame.draw.rect(screen, self.active_color, (x, y, self.width_button, self.height_button))

            if click[0] == 1:  # нажатие на кнопку
                pygame.mixer.Sound.play(button_sound)
                pygame.time.delay(300)
                if action is not None:
                    action()
        else:
            pygame.draw.rect(screen, self.inactive_color, (x, y, self.width_button, self.height_button))

        print_text(message=message, x=x + 10, y=y + 10, font_size=font_size)


def record():
    global flPause, vol
    menu_button = Button(50, 45, (190, 233, 221), (180, 255, 235))  # создание кнопки вернуться в меню
    record_button = Button(115, 45, (190, 233, 221), (180, 255, 235))  # создание кнопки обнулить рекорды

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # остановка музыки
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

        con = sqlite3.connect("results.sqlite")  # подключение бд
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM glasses""").fetchall()
        con.close()
        winter, village, desert = result[0][1], result[1][1], result[2][1]

        screen.blit(menu_bckgr, (0, 0))
        font = pygame.font.Font(None, 70)  # Надпись 'Лучшие результаты'
        text_game = font.render('Лучшие результаты', True, (16, 17, 18))
        text_rect = text_game.get_rect(center=(320, 100))
        screen.blit(text_game, text_rect)
        pygame.draw.rect(screen, (180, 255, 235), (70, 130, 500, 2), 0)

        pygame.draw.rect(screen, (180, 255, 235), (150, 300, 340, 2), 0)  # прорисовка тпблицы рекордов
        pygame.draw.rect(screen, (180, 255, 235), (150, 350, 340, 2), 0)
        pygame.draw.rect(screen, (180, 255, 235), (150, 400, 340, 2), 0)
        pygame.draw.rect(screen, (180, 255, 235), (150, 450, 340, 2), 0)
        pygame.draw.rect(screen, (180, 255, 235), (350, 300, 2, 150), 0)
        pygame.draw.rect(screen, (180, 255, 235), (150, 300, 2, 150), 0)
        pygame.draw.rect(screen, (180, 255, 235), (490, 300, 2, 150), 0)

        font = pygame.font.Font(None, 35)  # Надпись 'level "Desert"'
        text_game = font.render('level "Desert"', True, (16, 17, 18))
        text_rect = text_game.get_rect(center=(250, 325))
        screen.blit(text_game, text_rect)

        font = pygame.font.Font(None, 35)  # Надпись 'level "Village"'
        text_game = font.render('level "Village"', True, (16, 17, 18))
        text_rect = text_game.get_rect(center=(250, 375))
        screen.blit(text_game, text_rect)

        font = pygame.font.Font(None, 35)  # Надпись 'level "Winter"'
        text_game = font.render('level "Winter"', True, (16, 17, 18))
        text_rect = text_game.get_rect(center=(250, 425))
        screen.blit(text_game, text_rect)

        font = pygame.font.Font(None, 40)
        text_game = font.render(str(desert), True, (16, 17, 18))
        text_rect = text_game.get_rect(center=(420, 325))
        screen.blit(text_game, text_rect)

        font = pygame.font.Font(None, 40)
        text_game = font.render(str(village), True, (16, 17, 18))
        text_rect = text_game.get_rect(center=(420, 375))
        screen.blit(text_game, text_rect)

        font = pygame.font.Font(None, 40)
        text_game = font.render(str(winter), True, (16, 17, 18))
        text_rect = text_game.get_rect(center=(420, 425))
        screen.blit(text_game, text_rect)

        menu_button.draw(10, 645, '', show_menu, 40)
        pygame.draw.rect(screen, (180, 255, 235), (9, 644, 52, 47), 3)
        all_sprites_menu.draw(screen)

        record_button.draw(70, 645, 'update', reset_database, 30)
        pygame.draw.rect(screen, (180, 255, 235), (69, 644, 117, 47), 3)
        all_sprites_menu.draw(screen)
        pygame.display.flip()


def rule_window():  # окно с правилами игры
    global flPause, vol
    menu_button = Button(50, 45, (190, 233, 221), (180, 255, 235))  # создание кнопки вернуться в меню
    text = os.path.join('data', 'правила.txt')
    text = open(text, mode="r", encoding="utf8")
    text = text.read()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # остановка музыки
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
        screen.blit(menu_bckgr, (0, 0))
        font = pygame.font.Font(None, 70)  # Надпись 'Правила игры'
        text_game = font.render('Правила игры', True, (16, 17, 18))
        text_rect = text_game.get_rect(center=(320, 50))
        screen.blit(text_game, text_rect)
        pygame.draw.rect(screen, (180, 255, 235), (70, 80, 500, 2), 0)
        descriptioncounter = 0  # расстояние между строчками
        for x in text.split('\n'):  # вывод текста из txt на экран
            descriptioncounter += 2.1
            screen.blit((pygame.font.SysFont('constantia', 18).render(x, True, 'BLACK')),
                        (20, 75 + 10 * descriptioncounter))

        menu_button.draw(10, 645, '', show_menu, 40)
        pygame.draw.rect(screen, (180, 255, 235), (9, 644, 52, 47), 3)
        all_sprites_menu.draw(screen)
        pygame.display.flip()


def reset_database():  # обнуление бд
    con = sqlite3.connect("results.sqlite")  # подключение бд
    cur = con.cursor()

    cur.execute("""SELECT * FROM glasses""").fetchall()
    cur.execute("""UPDATE glasses SET number = 0
                        WHERE name = 'desert_map'""").fetchall()
    cur.execute("""UPDATE glasses SET number = 0
                            WHERE name = 'city_map'""").fetchall()
    cur.execute("""UPDATE glasses SET number = 0
                            WHERE name = 'winter_map'""").fetchall()
    con.commit()
    con.close()


def win_window():  # окно победы
    global flPause, vol
    replay_button = Button(120, 65, (190, 233, 221), (180, 255, 235))  # создание кнопок переиграть и вернуться в меню
    menu_button = Button(120, 65, (190, 233, 221), (180, 255, 235))
    all_sprites_game_over = pygame.sprite.Group()
    full_name = os.path.join('Общие картинки', 'Меню71.png')
    full_name = os.path.join('Картинки', full_name)
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name, -1)
    sprite_file.image = pygame.transform.scale(image_file, (90, 70))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_game_over.add(sprite_file)
    sprite_file.rect.x = 193
    sprite_file.rect.y = 445

    all_sprites_emerald = pygame.sprite.Group()
    full_name = os.path.join('Общие картинки', 'Emerald.png')
    full_name = os.path.join('Картинки', full_name)
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name)
    sprite_file.image = pygame.transform.scale(image_file, (35, 35))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_emerald.add(sprite_file)
    sprite_file.rect.x = 260
    sprite_file.rect.y = 395

    full_name = os.path.join('Общие картинки', 'переиграть3.png')
    full_name = os.path.join('Картинки', full_name)
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name, -1)
    sprite_file.image = pygame.transform.scale(image_file, (140, 60))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_game_over.add(sprite_file)
    sprite_file.rect.x = 340
    sprite_file.rect.y = 450

    con = sqlite3.connect("results.sqlite")  # подключение бд
    cur = con.cursor()
    result = cur.execute("""SELECT * FROM glasses
                    WHERE name = ?""", (current_level,)).fetchall()
    if final_points > result[0][1]:
        cur.execute("""UPDATE glasses SET number = ?
                         WHERE name = ? """, (final_points, current_level)).fetchall()
        con.commit()
    con.close()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # остановка музыки
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
        screen.blit(menu_bckgr, (0, 0))

        font_type = os.path.join('data', 'PingPong.ttf')  # надпись 'You win ;)'
        font = pygame.font.Font(font_type, 90)
        text = font.render('You win ;)', True, (16, 17, 18))
        text_rect = text.get_rect(center=(320, 340))
        screen.blit(text, text_rect)

        replay_button.draw(350, 450, '', replay_the_level, 40)  # прорисовка кнопок
        pygame.draw.rect(screen, (180, 255, 235), (349, 449, 122, 67), 3)

        menu_button.draw(180, 450, '', show_menu, 40)
        pygame.draw.rect(screen, (180, 255, 235), (179, 449, 122, 67), 3)

        font = pygame.font.Font(None, 60)  # прорисовка кол-ва очков
        text = font.render(str(final_points), True, (15, 20, 15))
        screen.blit(text, (305, 395))

        create_particles((random.randint(-50, 650), random.randint(-100, 500)))

        all_sprites_game_over.draw(screen)
        asterisks.update()
        asterisks.draw(screen)
        all_sprites_emerald.draw(screen)

        pygame.display.flip()
        clock.tick(50)


def game_over():  # окно проигрыша
    global number_of_lives, flPause, vol
    replay_button = Button(120, 65, (190, 233, 221), (180, 255, 235))  # создание кнопок переиграть и вернуться в меню
    menu_button = Button(120, 65, (190, 233, 221), (180, 255, 235))
    number_of_lives -= 1  # уменьшение кол-ва жизней
    all_sprites_game_over = pygame.sprite.Group()
    full_name = os.path.join('Общие картинки', 'Меню71.png')
    full_name = os.path.join('Картинки', full_name)
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name, -1)
    sprite_file.image = pygame.transform.scale(image_file, (90, 70))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_game_over.add(sprite_file)
    sprite_file.rect.x = 193
    sprite_file.rect.y = 395

    full_name = os.path.join('Общие картинки', 'переиграть3.png')
    full_name = os.path.join('Картинки', full_name)
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name, -1)
    sprite_file.image = pygame.transform.scale(image_file, (140, 60))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_game_over.add(sprite_file)
    sprite_file.rect.x = 340
    sprite_file.rect.y = 400
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # остановка музыки
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

        screen.blit(menu_bckgr, (0, 0))
        font_type = os.path.join('data', 'PingPong.ttf')
        font = pygame.font.Font(font_type, 90)
        text = font.render('Game over', True, (16, 17, 18))
        text_rect = text.get_rect(center=(320, 330))
        screen.blit(text, text_rect)

        replay_button.draw(350, 400, '', replay_the_level, 40)  # прорисовка кнопок
        pygame.draw.rect(screen, (180, 255, 235), (349, 399, 122, 67), 3)

        menu_button.draw(180, 400, '', show_menu, 40)
        pygame.draw.rect(screen, (180, 255, 235), (179, 399, 122, 67), 3)

        all_sprites_game_over.draw(screen)

        pygame.display.flip()


def replay_the_level():  # функция "переиграть"
    start_game(current_level)


def start_level_desert():  # Запуск уровня 'Desert'
    global current_level
    current_level = 'desert_map'
    start_game('desert_map')


def start_level_city():  # Запуск уровня 'Village'
    global current_level
    current_level = 'city_map'
    start_game('city_map')


def start_level_winter():  # Запуск уровня 'Winter'
    global current_level
    current_level = 'winter_map'
    start_game('winter_map')


def start_level_random():  # Запуск случайного уровня
    global current_level
    random_level = ['winter_map', 'city_map', 'desert_map']
    current_level = random.choice(random_level)
    start_game(current_level)


def start_game(name_level):  # функция игрового процесса
    global screen_rect, number_of_lives, vol, flPause, final_points
    global all_sprites, player_group, enemy_group, collectible_group, asterisks, countdown

    number_of_lives = 3  # количество жизней
    final_points = 0  # кол-во окончательных очков

    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    collectible_group = pygame.sprite.Group()
    asterisks = pygame.sprite.Group()

    gb = GAME_BASE[name_level]  # Сокращение записи

    level = Level(name_level, gb['free_tiles'], gb['win_tile'], gb['points'], gb['death_tiles'])
    player = Player(gb['player'], load_image('mario.png', colorkey=-1))
    enemies = []
    for i in gb['enemies_list']:
        enemies.append(Enemy(i[1], level, gb['enemy_image'], gb['enemy_size'], i[0]))
    game = Game(level, player, enemies)

    menu_button = Button(50, 45, (190, 233, 221), (180, 255, 235))

    full_name = os.path.join('Общие картинки', 'Жизнь.png')
    full_name = os.path.join('Картинки', full_name)

    all_sprites_life1 = pygame.sprite.Group()
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name)
    sprite_file.image = pygame.transform.scale(image_file, (40, 40))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_life1.add(sprite_file)
    sprite_file.rect.x = 370
    sprite_file.rect.y = 645

    all_sprites_life2 = pygame.sprite.Group()
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name)
    sprite_file.image = pygame.transform.scale(image_file, (40, 40))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_life2.add(sprite_file)
    sprite_file.rect.x = 325
    sprite_file.rect.y = 645

    all_sprites_life3 = pygame.sprite.Group()
    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name)
    sprite_file.image = pygame.transform.scale(image_file, (40, 40))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_life3.add(sprite_file)
    sprite_file.rect.x = 280
    sprite_file.rect.y = 645

    all_sprites_play = pygame.sprite.Group()

    full_name = os.path.join('Общие картинки', 'Emerald.png')
    full_name = os.path.join('Картинки', full_name)

    sprite_file = pygame.sprite.Sprite()
    image_file = load_image(full_name)
    sprite_file.image = pygame.transform.scale(image_file, (25, 25))
    sprite_file.rect = sprite_file.image.get_rect()
    all_sprites_play.add(sprite_file)
    sprite_file.rect.x = 530
    sprite_file.rect.y = 655

    screen_rect = (0, 0, width, height)

    countdown = gb['countdown']
    pygame.time.set_timer(COUNTDOWN_EVENT_TYPE, 1000)
    pygame.time.set_timer(UPDATE_ANIMATION_TYPE, 200)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == ENEMY_EVENT_TYPE:  # Передвижение противника
                for i in game.enemy_list:
                    game.move_enemy(i)
            if event.type == UPDATE_ANIMATION_TYPE:  # Обновление анимации противников
                for i in game.enemy_list:
                    i.update_frame()
            if event.type == COUNTDOWN_EVENT_TYPE:  # счётчик времени
                countdown -= 1
                if countdown <= 0:
                    game_over()
            elif event.type == pygame.KEYDOWN:
                game.move_player()
                if event.key == pygame.K_SPACE:  # остановка музыки
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

        screen.blit(menu_bckgr, (0, 0))

        game.render()
        all_sprites.draw(screen)

        asterisks.update()
        asterisks.draw(screen)

        if number_of_lives == 3:  # происовка жизней
            all_sprites_life1.draw(screen)
            all_sprites_life2.draw(screen)
            all_sprites_life3.draw(screen)
        elif number_of_lives == 2:
            all_sprites_life1.draw(screen)
            all_sprites_life2.draw(screen)
        else:
            all_sprites_life1.draw(screen)

        menu_button.draw(10, 645, '', show_menu, 40)  # прорисовка времени
        pygame.draw.rect(screen, (180, 255, 235), (9, 644, 52, 47), 3)
        time_play = time.strftime("%M:%S", time.gmtime(countdown))
        font = pygame.font.Font(None, 50)
        text = font.render(str(time_play), True, (0, 0, 0))
        text_rect = text.get_rect(center=(470, 670))
        screen.blit(text, text_rect)

        font = pygame.font.Font(None, 50)  # прорисовка кол-ва очков
        text = font.render(str(game.level.points), True, (0, 0, 0))
        screen.blit(text, (560, 652))

        final_points = game.level.points + countdown * 2 + number_of_lives * 100

        all_sprites_menu.draw(screen)
        all_sprites_play.draw(screen)

        clock.tick(60)
        pygame.display.flip()


if __name__ == '__main__':
    show_menu()
