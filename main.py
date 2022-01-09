import pygame
import sys
import os
import random
import pytmx

pygame.init()

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
collectible_group = pygame.sprite.Group()
asterisks = pygame.sprite.Group()

clock = pygame.time.Clock()
size = width, height = 600, 650
screen = pygame.display.set_mode(size)
GRAVITY = 1.5
ENEMY_EVENT_TYPE = 30

fullname1 = os.path.join('data', 'музыка1.mp3')
pygame.mixer.music.load(fullname1)
fullname2 = os.path.join('data', 'button.wav')
button_sound = pygame.mixer.Sound(fullname2)  # Подключение музыки
pygame.mixer.music.play(-1)
vol = 0.5  # громкость музыки
pygame.mixer.music.set_volume(vol)
flPause = False  # флаг включена/выключена музыка


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


def create_particles(position):
    particle_count = 20  # количество создаваемых частиц
    numbers = range(-5, 6)  # возможные скорости
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def terminate():  # Завершает работу
    pygame.quit()
    sys.exit()


def show_menu():  # окнj меню
    global menu_bckgr, flPause, vol
    fullname = os.path.join('Общие картинки', 'Фон1.jpg')  # подключение фона
    fullname = os.path.join('Картинки', fullname)
    fullname = os.path.join('data', fullname)
    menu_bckgr = pygame.image.load(fullname)
    start_desert_button = Button(200, 50, (190, 233, 221), (180, 255, 235))  # создание кнопок
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
        pygame.draw.rect(screen, (180, 255, 235), (150, 174, 300, 2), 0)

        font = pygame.font.Font(None, 75)  # Надпись 'Start game'
        text = font.render('Start game', True, (16, 17, 18))
        text_rect = text.get_rect(center=(300, 155))
        screen.blit(text, text_rect)

        start_desert_button.draw(200, 200, 'level "Desert"', start_level_desert, 30)  # Прорисовка кнопок
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
    def __init__(self, name, free_tiles, finish_tile):  # создание поля
        self.name = name
        self.free_tiles = free_tiles
        self.finish_tile = finish_tile
        filename = os.path.join('data', f'{name}', f'{name}.tmx')

        self.tile_map = pytmx.load_pygame(filename)
        self.height = self.tile_map.height
        self.width = self.tile_map.width
        self.tile_size = self.tile_map.tilewidth


    def render(self):  # Прорисовка поля
        for y in range(self.height):
            for x in range(self.width):
                image1 = self.tile_map.get_tile_image(x, y, 0)
                screen.blit(image1, (x * self.tile_size, y * self.tile_size))

                image2 = self.tile_map.get_tile_image(x, y, 1)
                screen.blit(image2, (x * self.tile_size, y * self.tile_size))



    def find_path_step(self, start, target):
        INF = 1000
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
                        and self.is_free((next_x, next_y)) and distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y

    def get_tile_id(self, position):
        print(self.tile_map.tiledgidmap[self.tile_map.get_tile_gid(*position, 1)])

        return self.tile_map.tiledgidmap[self.tile_map.get_tile_gid(*position, 1)]


    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles



class Player(pygame.sprite.Sprite):  # КЛАСС ПЕРСОНАЖА
    def __init__(self, name, position):
        super(Player, self).__init__(player_group, all_sprites)
        self.pos_x, self.pos_y = position
        self.image = load_image(name)
        self.update()

    def get_pos(self):
        return self.pos_x, self.pos_y

    def set_pos(self, pos):
        self.pos_x, self.pos_y = pos

    def render(self, level):
        self.rect = self.image.get_rect().move(level.tile_size * self.pos_x,
                                               level.tile_size * self.pos_y)


class Enemy(pygame.sprite.Sprite):  # КЛАСС ПРОТИВНИКА
    def __init__(self, pos, level, sheet, columns, rows):
        super(Enemy, self).__init__(enemy_group, all_sprites)
        self.pos_x, self.pos_y = pos
        self.level = level
        self.delay = 200
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(1):
            for i in range(5):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def render(self):
        self.rect = self.image.get_rect().move(self.level.tile_size * self.pos_x,
                                               self.level.tile_size * self.pos_y)

    def update_frame(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def get_pos(self):
        return self.pos_x, self.pos_y

    def set_pos(self, pos):
        self.pos_x, self.pos_y = pos




class Collectible(pygame.sprite.Sprite):  # Класс собираемых объектов (пока не знаю каких, Даша - решай)
    def __init__(self, pos_x, pos_y, level):
        super(Collectible, self).__init__(collectible_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = star_image
        self.level = level
        self.update()

    def render(self):
        self.rect = self.image.get_rect().move(self.level.cell_size * self.pos_y + self.level.cell_size * 0.35,
                                               self.level.cell_size * self.pos_x + self.level.cell_size * 0.2)


class Game:
    def __init__(self, level, player, enemy_list):
        self.level = level
        self.player = player
        self.enemy_list = enemy_list

    def render(self):
        self.level.render()
        self.player.render(self.level)
        for i in self.enemy_list:
            i.render()

    def move_player(self):
        next_x, next_y = self.player.get_pos()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.level.is_free((next_x, next_y)):
            self.player.set_pos((next_x, next_y))
            self.check_tile()

    def check_tile(self):
        global amount_of_animation
        if self.level.get_tile_id(self.player.get_pos()) == 44:
            if amount_of_animation > 0:
                amount_of_animation -= 1
                create_particles((random.randint(-50, 650), random.randint(-100, 100)))
            else:
                win_window()

    def move_enemy(self, enemy):
        next_position = self.level.find_path_step(enemy.get_pos(), self.player.get_pos())
        enemy.pos_x, enemy.pos_y = next_position



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


def rule_window():  # окно с правилами игры
    global flPause, vol
    back_button = Button(75, 60, (190, 233, 221), (180, 255, 235))  # оздание кнопки вернуться в меню
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
        back_button.draw(20, 580, '<--', show_menu, 40)
        pygame.draw.rect(screen, (180, 255, 235), (19, 579, 77, 62), 3)
        pygame.display.flip()


def win_window():  # окно с правилами игры
    global flPause, vol
    back_button = Button(75, 60, (190, 233, 221), (180, 255, 235))  # оздание кнопки вернуться в меню
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
        back_button.draw(20, 580, '<--', show_menu, 40)
        pygame.draw.rect(screen, (180, 255, 235), (19, 579, 77, 62), 3)
        pygame.display.flip()


def game_over():  # окно проигрыша
    global number_of_lives, flPause, vol
    replay_button = Button(130, 60, (190, 233, 221), (180, 255, 235))  # создание кнопок переиграть и вернуться в меню
    menu_button = Button(130, 60, (190, 233, 221), (180, 255, 235))
    number_of_lives -= 1
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

        if number_of_lives < 1:  # открытие окна в случае отсутствия жизней
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
        else:
            pygame.mixer.Sound.play(button_sound)
            pygame.time.delay(300)
            replay_the_level()


def replay_the_level():  # функция "переиграть"
    global number_of_lives
    start_game(current_level)


def start_level_desert():  # функция level_desert
    global current_level, number_of_lives
    number_of_lives = 3
    current_level = 'level_Desert'
    start_game('desert_map')


def start_level_jungle():  # функция level_jungle
    global current_level, number_of_lives
    number_of_lives = 3
    current_level = 'level_Jungle'
    start_game('jungle_map')


def start_level_winter():  # функция level_winter
    global current_level, number_of_lives
    number_of_lives = 3
    current_level = 'level_Winter'
    start_game('winter_map')


def start_level_random():  # функция level_random
    global current_level, number_of_lives
    number_of_lives = 3
    random_level = ['level_Winter', 'level_Jungle', 'level_Desert']
    current_level = random.choice(random_level)
    start_game(current_level)


def start_game(name_level):
    global number_of_cells, screen_rect, number_of_lives, vol, flPause, amount_of_animation
    global all_sprites, player_group, enemy_group, collectible_group, asterisks

    size = width, height = 640, 640
    screen = pygame.display.set_mode(size)

    amount_of_animation = 100  # количество прокруток анимации победы
    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    collectible_group = pygame.sprite.Group()
    asterisks = pygame.sprite.Group()
    number_of_cells = 12

    level = Level('winter_map', [27, 30, 44], 44)
    player = Player('mario.png', (10, 16))
    enemies = []
    for i in (1, 1), (18, 1), (1, 18), (18, 18), (5, 10), (10, 5):
        enemies.append(Enemy(i, level, enemy_image, 6, 8))
    game = Game(level, player, enemies)

    back_button = Button(75, 50, (190, 233, 221), (180, 255, 235))

    fullname = os.path.join('Общие картинки', 'Жизнь.png')
    fullname = os.path.join('Картинки', fullname)

    all_sprites_life1 = pygame.sprite.Group()
    sprite = pygame.sprite.Sprite()
    image = load_image(fullname)
    sprite.image = pygame.transform.scale(image, (50, 50))
    sprite.rect = sprite.image.get_rect()
    all_sprites_life1.add(sprite)
    sprite.rect.x = 540
    sprite.rect.y = 605

    all_sprites_life2 = pygame.sprite.Group()
    sprite = pygame.sprite.Sprite()
    image = load_image(fullname)
    sprite.image = pygame.transform.scale(image, (50, 50))
    sprite.rect = sprite.image.get_rect()
    all_sprites_life2.add(sprite)
    sprite.rect.x = 485
    sprite.rect.y = 605

    all_sprites_life3 = pygame.sprite.Group()
    sprite = pygame.sprite.Sprite()
    image = load_image(fullname)
    sprite.image = pygame.transform.scale(image, (50, 50))
    sprite.rect = sprite.image.get_rect()
    all_sprites_life3.add(sprite)
    sprite.rect.x = 430
    sprite.rect.y = 605

    screen_rect = (0, 0, width, height)

    pygame.mixer.music.play(-1)
    flPause = False
    vol = 0.5
    pygame.mixer.music.set_volume(vol)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == ENEMY_EVENT_TYPE:
                for i in game.enemy_list:
                    game.move_enemy(i)
                    i.update_frame()
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


        game.render()
        all_sprites.draw(screen)

        asterisks.update()
        asterisks.draw(screen)

        if number_of_lives == 3:
            all_sprites_life1.draw(screen)
            all_sprites_life2.draw(screen)
            all_sprites_life3.draw(screen)
        elif number_of_lives == 2:
            all_sprites_life1.draw(screen)
            all_sprites_life2.draw(screen)
        else:
            all_sprites_life1.draw(screen)

        back_button.draw(10, 605, '<--', show_menu, 40)
        pygame.draw.rect(screen, (180, 255, 235), (9, 604, 77, 52), 3)


        clock.tick(60)
        pygame.display.flip()


player_image = load_image('mario.png')
enemy_image = load_image('winter_map\Yeti.png')
star_image = load_image('star.png')

if __name__ == '__main__':
    show_menu()
