import pygame
import os
import math
import sqlite3
import random
import sys
WIDTH, HEIGHT = 1399, 900

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 530
TARGET_HEIGHT = 100
TARGET_SIZE = 30  # Размер спрайта
BULLET_SPEED = 5
NUM_TARGETS = 100
TARGET_SPAWN_DELAY = 3200
PLAYER_SPEED = 5
TARGET_SPACING = 500
TARGET_SPEED = 3
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
H = 500
DATABASE_NAME_uh = 'scores_uh.db'
# --- Цвета ---

os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'
pygame.init()
screen = pygame.display.set_mode((100, 250))

screen_rect = (0, 0, WIDTH, HEIGHT)
all_sprites = pygame.sprite.Group()
PARTICLE_GENERATION_RATE = 10  # Частиц в секунду
last_particle_creation_time = pygame.time.get_ticks()

# Загрузка изображений (убедитесь, что файлы существуют в той же директории)
player_image = pygame.image.load("submarine2.png").convert_alpha()
obstacle_image = pygame.image.load("tar.png").convert_alpha()
background_image = pygame.image.load("background1.png").convert()
# База данных
DATABASE_NAME = 'scores.db'
numbers = range(-5, 6)
sound1 = pygame.mixer.Sound('jixaw-metal-pipe-falling-sound.mp3')
sound1.set_volume(0.2)

pygame.mixer.music.load('K-391-Triple Rush-kissvk.com.mp3')
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)


# --- Класс для кнопки меню ---
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height


defbuttons = [
    Button('Mute', 1250, 50, 50, 50, (100, 0, 0), (150, 0, 0), pygame.mixer.music.set_volume(0)),
    Button('50%', 1150, 50, 50, 50, (100, 0, 0), (150, 0, 0), pygame.mixer.music.set_volume(0.5)),
    Button('100%', 1050, 50, 50, 50, (100, 0, 0), (150, 0, 0), pygame.mixer.music.set_volume(1))]


# --- Класс для меню ---
class Menu:
    def __init__(self, screen):  # Добавили bubble_image в параметры
        self.screen = screen
        init_database()
        self.all_sprites = pygame.sprite.Group()
        self.submarine_image = pygame.image.load("submarin_menu.png").convert_alpha()
        self.submarine_rect = self.submarine_image.get_rect(topleft=(580, 350))
        init_database_uh()
        self.buttons = [
            Button("Торпедная атака", 100, 200, 300, 50, (0, 100, 0), (0, 150, 0), self.run_game1),
            Button("Путь через мины", 100, 300, 300, 50, (0, 100, 0), (0, 150, 0), self.run_game2),
            Button("Выход", 100, 400, 300, 50, (100, 0, 0), (150, 0, 0), self.quit_game),
            Button('Mute', 1125, 50, 50, 50, (100, 0, 0), (150, 0, 0), 0),
            Button('50%', 1200, 50, 50, 50, (100, 0, 0), (150, 0, 0), 0.5),
            Button('100%', 1275, 50, 50, 50, (100, 0, 0), (150, 0, 0), 1)]

    def run(self):
        running = True
        while running:
            self.all_sprites.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if (button.is_clicked(event.pos) and button.action != 0 and button.action != 0.5
                                and button.action != 1):
                            button.action()
                        if button.is_clicked(event.pos) and button.action == 0:
                            pygame.mixer.music.set_volume(0)
                            sound1.set_volume(0)
                        elif button.is_clicked(event.pos) and button.action == 0.5:
                            pygame.mixer.music.set_volume(0.4)
                            sound1.set_volume(0.2)
                        elif button.is_clicked(event.pos) and button.action == 1:
                            pygame.mixer.music.set_volume(0.8)
                            sound1.set_volume(0.4)

            self.draw()  # Отрисовка меню

            for i in create_bubbles():
                self.all_sprites.add(i)
            self.all_sprites.draw(self.screen)

            pygame.display.flip()
            pygame.time.Clock().tick(60)

        return False  # Вернет False, когда меню закрыто

    def draw(self):
        self.screen.fill((0, 50, 50))
        font = pygame.font.Font(None, 36)
        font1 = pygame.font.Font(None, 75)
        name = font1.render('ПОДВОДНЫЙ СТРАЖ', True, WHITE)
        self.screen.blit(name, (520, 20))
        high_score_uh = get_high_score_uh()
        high_score_text_uh = font.render(f"Рекорд (Торпедная атака): {high_score_uh}", True, WHITE)
        self.screen.blit(high_score_text_uh, (10, 10))
        self.screen.blit(self.submarine_image, self.submarine_rect)
        high_score_planets = get_high_score()
        high_score_text_planets = font.render(f"Рекорд (Путь через мины): {high_score_planets}", True, WHITE)
        self.screen.blit(high_score_text_planets, (10, 50))
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            if button.is_clicked(mouse_pos):
                button.color = button.hover_color
            else:
                button.color = (0, 100, 0) if button.action != self.quit_game else (100, 0, 0)
            button.draw(self.screen)

    def run_game1(self):
        game1 = Game1(self.screen)
        game1.run()

    def run_game2(self):
        game2 = Game2(self.screen)
        game2.run()

    def quit_game(self):
        pygame.quit()
        sys.exit()


def init_database_uh():
    conn = sqlite3.connect(DATABASE_NAME_uh)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores_uh (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def save_score_uh(score):
    conn = sqlite3.connect(DATABASE_NAME_uh)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores_uh (score) VALUES (?)", (score,))
    conn.commit()
    conn.close()


def get_high_score_uh():
    conn = sqlite3.connect(DATABASE_NAME_uh)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(score) FROM scores_uh")
    high_score = cursor.fetchone()
    conn.close()
    return high_score[0] if high_score else 0


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, pos, dx, dy, scale, grav):
        super().__init__(all_sprites)
        self.scale = scale
        self.frames = []
        self.framesf = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.framesf[self.cur_frame]
        self.rect = self.rect.move(x, y)

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = grav

        self.frame = 0  # текущий кадр
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100  # как быстро кадры меняются

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
        for ll in self.frames:
            self.framesf.append(pygame.transform.scale(ll, (self.scale, self.scale)))

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.frames):
                self.frame = 0

            self.image = self.framesf[self.frame]
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()

    def get_sprite_rect(self):
        return self.image.get_rect()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    list = []

    for _ in range(particle_count):
        list.append(AnimatedSprite(load_image("Pixel Flame Spritesheet.png"), 4, 1, 32, 32, position,
                                   random.choice(numbers), random.choice(numbers), random.choice((10, 20, 40)), 0.1))
    return list


def create_bubbles():
    # количество создаваемых частиц
    particle_count = 1
    numbers = range(-1, 1)
    list = []
    for _ in range(particle_count):
        list.append(
            AnimatedSprite(load_image("energy-shield-sprite-sheet-png-6186-300x207.png"), 5, 4, 32, 32,
                           (random.choice(range(WIDTH)), HEIGHT),
                           random.choice(numbers), random.choice(numbers), random.choice((10, 20, 40)), -0.2))
    return list


def load_image(name, colorkey=None):
    fullname = os.path.join(name)  # Замените на путь к вашей картинке
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print(f"Cannot load image: {fullname}")
        raise SystemExit(message)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Target(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = load_image("shipp.png")  # Или создайте прямоугольник, как в предыдущем примере
        self.rect = self.image.get_rect(topleft=(x, 200))
        self.speed = 3  # Скорость движения
        self.direction = -1  # 1 - вправо, -1 - влево
        self.image.set_colorkey((255, 255, 255))

    def update(self):
        self.rect.x += self.speed * self.direction


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((5, 10), pygame.SRCALPHA)
        pygame.draw.rect(self.image, WHITE, (0, 0, 5, 10))

        self.speed = BULLET_SPEED  # Assign speed BEFORE using it

        self.rect = self.image.get_rect(center=(x, HEIGHT - self.image.get_height()))

        dx = target_x - x
        dy = target_y - y
        self.angle = math.atan2(dy, dx)

        self.vx = self.speed * math.cos(self.angle)
        self.vy = self.speed * math.sin(self.angle)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()


class Player_uh(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("player1.png")  # Замените на имя вашего файла
        self.rect = self.image.get_rect(bottomleft=(50, 450))
        self.speed = PLAYER_SPEED
        self.image.set_colorkey((0, 0, 0))

    def update(self):  # Убрали аргумент keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed


# --- Класс для мини-игры 1 ---
class Game1:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.background_image = load_image("sea_uh.png")
        self.boom_image = load_image("boom.png")

        self.all_sprites = pygame.sprite.Group()
        self.targets = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.player = Player_uh()
        self.all_sprites.add(self.player)

        self.score = 0
        self.game_over = False
        self.last_target_spawn = pygame.time.get_ticks()
        self.num_bullets = 3  # Начальное количество снарядов

    def reset(self):
        self.all_sprites.empty()
        self.bullets.empty()
        self.targets.empty()
        self.all_sprites.add(self.player)
        self.score = 0
        self.game_over = False
        self.last_target_spawn = pygame.time.get_ticks()
        self.num_bullets = 3  # Сбрасываем количество снарядов

    def run(self):
        self.reset()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_score_uh(self.score)
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not self.game_over and self.num_bullets > 0:
                    bullet = Bullet(self.player.rect.centerx, HEIGHT - 50, self.player.rect.centerx,
                                    self.player.rect.centery)
                    self.all_sprites.add(bullet)
                    self.bullets.add(bullet)
                    self.num_bullets -= 1

            self.all_sprites.update()

            # Spawn targets
            now = pygame.time.get_ticks()
            if now - self.last_target_spawn > TARGET_SPAWN_DELAY and not self.game_over:
                x = WIDTH + TARGET_SIZE
                target = Target(x)
                self.all_sprites.add(target)
                self.targets.add(target)
                self.last_target_spawn = now

            # Check for collisions
            for bullet in list(self.bullets):
                collisions = pygame.sprite.spritecollide(bullet, self.targets, True)
                if collisions:
                    for target in collisions:
                        explosion_rect = self.boom_image.get_rect(center=target.rect.center)
                        self.screen.blit(self.boom_image, explosion_rect)
                        pygame.display.flip()
                        pygame.time.delay(200)
                        sound1.play()
                        for i in create_particles((explosion_rect.x, explosion_rect.y)):
                            self.all_sprites.add(i)
                    bullet.kill()
                    self.score += len(collisions)
                    self.num_bullets += len(collisions)
            if self.score >= NUM_TARGETS:
                self.game_over = True

            self.screen.blit(self.background_image, (0, 0))
            self.all_sprites.draw(self.screen)

            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Счёт: {self.score}", True, WHITE)
            bullets_text = font.render(f"Торпеды: {self.num_bullets}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(bullets_text, (10, 50))
            if self.num_bullets == 0:  # Game Over при достижении цели или нуле снарядов
                self.game_over = True
            if self.game_over:
                game_over_text = font.render("Игра окончена", True, WHITE)

                text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
                self.screen.blit(game_over_text, text_rect)
                save_score_uh(self.score)

            pygame.display.flip()
            self.clock.tick(60)
        return


def init_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def save_score(score):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (score) VALUES (?)", (score,))
    conn.commit()
    conn.close()


def get_high_score():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(score) FROM scores")
    high_score = cursor.fetchone()
    conn.close()
    return high_score[0] if high_score else 0


# Классы
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.speed = 4
        self.image.set_colorkey((255, 255, 255))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, speed):
        super().__init__()
        self.image = obstacle_image
        self.rect = self.image.get_rect(x=x, y=0)
        self.speed = speed
        self.image.set_colorkey((255, 255, 255))

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Game2:
    def __init__(self, screen):
        self.screen = screen
        self.partickles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.clock = pygame.time.Clock()
        self.score = 0
        self.k = 0
        self.game_over = False
        self.last_obstacle_spawn = pygame.time.get_ticks()
        self.obstacle_spawn_delay = 750
        self.obstacle_min_spacing = 50
        self.obstacle_speed = 4
        self.text_color = (255, 255, 255)
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)

    def reset(self):
        self.score = 0
        self.game_over = False
        self.obstacles.empty()
        self.player.rect.center = (WIDTH // 2, 650)
        self.last_obstacle_spawn = pygame.time.get_ticks()
        self.k = 0

    def run(self, is_running=True):
        self.reset()
        running = is_running
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_over:
                            self.reset()
                        else:
                            running = False

            now = pygame.time.get_ticks()
            if not self.game_over:
                self.score += 1
                score_text = self.font.render(f"Счет: {self.score}", True, self.text_color)
                screen.blit(score_text, (10, 10))
                if now - self.last_obstacle_spawn > self.obstacle_spawn_delay:
                    found_place = False
                    while not found_place:
                        x = random.randint(0, WIDTH - obstacle_image.get_width())
                        valid_position = True
                        for obstacle in self.obstacles:
                            if abs(x - obstacle.rect.x) < self.obstacle_min_spacing:
                                valid_position = False
                                break
                        if valid_position:
                            obstacle = Obstacle(x, self.obstacle_speed)
                            obstacle.rect.y = -obstacle_image.get_height()
                            self.all_sprites.add(obstacle)
                            self.obstacles.add(obstacle)
                            self.last_obstacle_spawn = now
                            found_place = True

                self.all_sprites.update()
                for obstacle in list(self.obstacles):
                    if obstacle.rect.top > HEIGHT:
                        self.score += 1

                        obstacle.kill()

                if pygame.sprite.spritecollide(self.player, self.obstacles, True, pygame.sprite.collide_mask):
                    self.game_over = True
            self.partickles.update()

            self.screen.blit(background_image, (0, 0))
            self.partickles.draw(self.screen)
            self.all_sprites.draw(self.screen)
            score_text = self.font.render(f"Счет: {self.score}", True, self.text_color)
            self.screen.blit(score_text, (10, 10))

            if self.game_over:
                if self.k == 0:
                    sound1.play()
                if self.k < 300:
                    for i in create_particles((self.player.rect.x, self.player.rect.y)):
                        self.partickles.add(i)
                        self.k += 1

                game_over_text = self.game_over_font.render("Игра окончена!", True, self.text_color)
                text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(game_over_text, text_rect)
                press_space = self.font.render("Нажмите пробел для перезапуска", True, self.text_color)
                press_space_rect = press_space.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
                self.screen.blit(press_space, press_space_rect)
                save_score(self.score)  # Сохраняем счет в базу данных
            pygame.display.flip()
            self.clock.tick(60)
        return  # Возврат в меню


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Подводная атака")

    menu = Menu(screen)
    in_menu = True
    while in_menu:
        in_menu = menu.run()  # Цикл меню
    pygame.quit()


if __name__ == "__main__":
    main()
