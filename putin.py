import math
from datetime import datetime, timedelta

import pygame
import random
import pygame.mixer

pygame.mixer.init()
pygame.mixer.music.load("assets/audio/sound.wav")
pygame.mixer.music.play()
clock = pygame.time.Clock()
# инициализация Pygame
pygame.init()

# параметры окна
WIDTH = 1200
HEIGHT = 800

background_image = pygame.image.load("assets/img/background_1.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
background_x = 0
background_x2 = background_image.get_width()
background_x3 = background_image.get_width()
background_x4 = background_image.get_width()

TITLE = "Убей Путина"
FPS = 60

# цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
last_shot = datetime.now()
ENEMY_COUNT = 100
SPEED_PLAYER = 5
SPEED_ENEMY = 3
SPEED_BULLET = 5
SIZE_PLAYER = 100
SIZE_ENEMY = 100
SIZE_BOSS = 400
SIZE_BULLET = 60
ENEMY_HEALTH = 100
BOSS_HEALTH = 1000
LIVES = 3
score = 0
winner = False


# Функция для отображения бесконечного фона
def display_background():
    global background_x, background_x2, background_x3, background_x4
    screen.blit(background_image, (background_x, 0))
    screen.blit(background_image, (background_x2, 0))
    screen.blit(background_image, (background_x3, 0))
    screen.blit(background_image, (background_x4, 0))
    background_x -= 1
    background_x2 -= 1
    background_x3 -= 1
    background_x4 -= 1
    if background_x < -background_image.get_width():
        background_x = background_x4 + background_image.get_width()
    if background_x2 < -background_image.get_width():
        background_x2 = background_x + background_image.get_width()
    if background_x3 < -background_image.get_width():
        background_x3 = background_x2 + background_image.get_width()
    if background_x4 < -background_image.get_width():
        background_x4 = background_x3 + background_image.get_width()


# создание класса Player
class Player(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.image.load("assets/img/player_1.png")
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(center=(WIDTH / 2, 0))
        self.width = width
        self.height = height
        self.lives = LIVES
        self.select_weapons = Bullet
        self.weapons = [Bullet, HomingBullet, Laser]

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            self.select_weapons = self.weapons[0]
        if keys[pygame.K_2]:
            self.select_weapons = self.weapons[1]
        if keys[pygame.K_3]:
            self.select_weapons = self.weapons[2]

        if keys[pygame.K_LEFT] and self.rect.x > 0 - 50:
            self.rect.x -= SPEED_PLAYER
        if keys[pygame.K_RIGHT] and self.rect.x < WIDTH - 50:
            self.rect.x += SPEED_PLAYER
        self.rect.y = HEIGHT - self.height
        if keys[pygame.K_SPACE]:
            global last_shot
            bullet = self.select_weapons(self.rect.x + self.width / 2,
                                         self.rect.y,
                                         0,
                                         -SPEED_BULLET,
                                         SIZE_BULLET,
                                         SIZE_BULLET)
            if bullet.can_shot():
                bullets.add(bullet)
                last_shot = datetime.now()

    def collidercircle(self, other, radius):
        distance = ((self.rect.centerx - other.rect.centerx) ** 2 +
                    (self.rect.centery - other.rect.centery) ** 2) ** 0.5
        sum_radius = abs(self.rect.width + radius) / 2
        return distance + 10 <= sum_radius


class Enemy(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.image.load("assets/img/enemy_1.png")
        self.image.set_colorkey((255, 255, 255))
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -self.rect.height

        self.max_health = ENEMY_HEALTH
        self.current_health = self.max_health
        self.create_time = datetime.now()

    def get_position(self):
        return self.rect.centerx, self.rect.centery

    def hit(self, damage):
        self.current_health -= damage
        if self.current_health <= 0:
            self.kill()
            add_score(1)

    def draw_health_bar(self):
        BAR_LENGTH = 40
        BAR_HEIGHT = 5
        fill = (self.current_health / self.max_health) * BAR_LENGTH
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 10, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 10, fill, BAR_HEIGHT)
        pygame.draw.rect(screen, (255, 0, 0), outline_rect, 2)
        pygame.draw.rect(screen, (0, 255, 0), fill_rect)

    def collidercircle(self, other, radius):
        distance = ((self.rect.centerx - other.rect.centerx) ** 2 +
                    (self.rect.centery - other.rect.centery) ** 2) ** 0.5
        sum_radius = abs(self.rect.width + radius) / 2
        return distance <= sum_radius

    def update(self):
        self.rect.move_ip(0, SPEED_ENEMY)
        if self.rect.top > HEIGHT:
            self.kill()


class HomingEnemy(Enemy):
    def __init__(self, width, height, x, y):
        super().__init__(width, height)
        self.dx = None
        self.dy = None
        self.rect.x = x
        self.rect.y = y
        self.max_health = 10
        self.current_health = self.max_health

    def get_position(self):
        return self.rect.centerx, self.rect.centery

    def collidercircle(self, other, radius):
        distance = ((self.rect.centerx - other.rect.centerx) ** 2 +
                    (self.rect.centery - other.rect.centery) ** 2) ** 0.5
        sum_radius = abs(self.rect.width + radius) / 2
        return distance <= sum_radius

    def set_dx_dy(self):
        if player:
            self.dx = 0
            self.dy = 0
            if player.rect.centerx <= self.rect.centerx:
                self.dx -= SPEED_BULLET

            elif player.rect.centerx >= self.rect.centerx:
                self.dx += SPEED_BULLET

            if player.rect.centery <= self.rect.centery:
                self.dy -= SPEED_BULLET
            elif player.rect.centery >= self.rect.centery:
                self.dy += SPEED_BULLET

    def update(self):
        self.set_dx_dy()
        self.rect.move_ip(self.dx, self.dy)
        if self.rect.top > HEIGHT:
            self.kill()


class Boss(Enemy):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.direction = 1
        self.rect.y = -self.rect.height + height
        self.max_health = BOSS_HEALTH
        self.current_health = self.max_health
        self.shot_time = datetime.now()

    def draw_health_bar(self):
        BAR_LENGTH = 400
        BAR_HEIGHT = 50
        fill = (self.current_health / self.max_health) * BAR_LENGTH
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 10, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 10, fill, BAR_HEIGHT)
        pygame.draw.rect(screen, (255, 0, 0), outline_rect, 2)
        pygame.draw.rect(screen, (0, 255, 0), fill_rect)

    def update(self):
        if datetime.now() - self.shot_time > timedelta(seconds=1):
            self.shot_time = datetime.now()
            self.shot()
        self.rect.move_ip(self.direction * SPEED_ENEMY, 0)  # движение в текущем направлении
        if self.rect.right > WIDTH:  # проверка достижения границы
            self.direction = -1  # изменение направления движения
        elif self.rect.left < 0:  # проверка достижения границы
            self.direction = 1  # изменение направления движения
            # Проверка столкновения с оружием

    def hit(self, damage):
        self.current_health -= damage
        if self.current_health <= 0:
            self.kill()
            add_score(5)
            global winner
            winner = True

    def shot(self):
        enemy = HomingEnemy(SIZE_ENEMY, SIZE_ENEMY, self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height)
        enemies.add(enemy)


class Bullet(pygame.sprite.Sprite):
    shoot_delay = timedelta(seconds=0.1)

    def __init__(self, x, y, dx, dy, width, height):
        super().__init__()
        self.image = pygame.image.load("assets/img/bullet_1.png")
        self.width = width
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x - width / 2
        self.rect.y = y
        self.image = pygame.transform.scale(self.image, (width, height))
        self.dx = dx
        self.dy = dy
        self.angle = 90
        self.damage = 25

    def collidercircle(self, other, radius):
        distance = ((self.rect.centerx - other.rect.centerx) ** 2 +
                    (self.rect.centery - other.rect.centery) ** 2) ** 0.5
        sum_radius = abs(self.rect.width + radius) / 2
        return distance <= sum_radius

    def update(self):
        self.rect.move_ip(self.dx, self.dy)
        if self.rect.bottom < 0:
            self.kill()
        self.shot()

    def can_shot(self):
        return datetime.now() - last_shot >= self.shoot_delay

    def shot(self):
        for boss in bosses:
            if self.collidercircle(boss, boss.rect.width):
                boss.hit(self.damage)
                self.kill()
        for enemy in enemies:
            if self.collidercircle(enemy, enemy.rect.width):
                enemy.hit(self.damage)
                self.kill()


class HomingBullet(Bullet):
    def __init__(self, x, y, dx, dy, width, height):
        super().__init__(x, y, dx, dy, width, height)
        self.image = pygame.image.load("assets/img/bullet_4.png")
        self.image = pygame.transform.scale(self.image, (width, height))
        self.target = None
        self.damage = 10

    def get_target(self):
        near_enemies = self.get_near()
        if not near_enemies:
            return None
        return min(near_enemies, key=lambda x: x[1])[0]

    def get_near(self):
        near_enemies = []
        for boss in bosses:
            distance = ((self.rect.centerx - boss.rect.centerx) ** 2 +
                        (self.rect.centery - boss.rect.centery) ** 2) ** 0.5
            near_enemies.append((boss, distance))
        for enemy in enemies:
            distance = ((self.rect.centerx - enemy.rect.centerx) ** 2 +
                        (self.rect.centery - enemy.rect.centery) ** 2) ** 0.5
            near_enemies.append((enemy, distance))
        return near_enemies

    def update(self):

        enemy = self.get_target()
        if enemy:
            self.dx = 0
            self.dy = 0
            if enemy.rect.centerx <= self.rect.centerx:
                self.dx -= SPEED_BULLET

            elif enemy.rect.centerx >= self.rect.centerx:
                self.dx += SPEED_BULLET

            if enemy.rect.centery <= self.rect.centery:
                self.dy -= SPEED_BULLET
            elif enemy.rect.centery >= self.rect.centery:
                self.dy += SPEED_BULLET
        self.rect.move_ip(self.dx, self.dy)

        if self.rect.bottom < 0:
            self.kill()
        for enemy in pygame.sprite.spritecollide(self, enemies, False):
            if self.collidercircle(enemy, self.width / 2):
                enemy.kill()
                self.kill()
                add_score(1)
        self.shot()


class Laser(Bullet):
    shoot_delay = timedelta(seconds=0.00001)

    def __init__(self, x, y, dx, dy, width, height):
        super().__init__(x, y, dx, dy, width, height)
        self.image = pygame.image.load("assets/img/bullet_3.png")
        self.width = width
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.damage = 5

        self.rect.x = x - width / 2
        self.rect.y = y
        self.dx = 0
        self.dy = -10

    def update(self):
        self.rect.move_ip(self.dx, self.dy)
        self.rect.x = player.rect.x + 20
        if self.rect.bottom < 0:
            self.kill()
        for star in pygame.sprite.spritecollide(self, enemies, False):
            if self.collidercircle(star, self.width / 2):
                star.kill()
                add_score(1)
        self.shot()


bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bosses = pygame.sprite.Group()
player = Player(SIZE_PLAYER, SIZE_PLAYER)
start_time = datetime.now()


def reset():
    global bullets, enemies, player, bosses, start_time,SPEED_ENEMY
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bosses = pygame.sprite.Group()
    player = Player(SIZE_PLAYER, SIZE_PLAYER)
    start_time = datetime.now()
    SPEED_ENEMY = 3
    set_score()


def set_score():
    global score
    score = 0


def add_score(total):
    global score
    score += total



def game_text_update():
    font = pygame.font.SysFont(None, 48)
    score_lives = font.render("Lives: {}".format(player.lives), True, WHITE)
    text_rect = score_lives.get_rect()
    text_rect.topright = (WIDTH - 10, 10)
    screen.blit(score_lives, text_rect)

    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (10, 10))


def looser():
    font = pygame.font.SysFont(None, 72)
    game_over_text = font.render("Game Over!", True, WHITE)

    text_width, text_height = font.size("Game Over!")
    text_x = (WIDTH - text_width) / 2
    text_y = (HEIGHT - text_height) / 2

    screen.fill(BLACK)
    screen.blit(game_over_text, (text_x, text_y))

    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (10, 10))
    pygame.display.update()

    pygame.time.wait(2000)
    reset()


create_time = datetime.now()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    if len(enemies) < ENEMY_COUNT and score < ENEMY_COUNT-30:
        if datetime.now() - create_time >= timedelta(seconds=0.1):
            enemy = Enemy(SIZE_ENEMY, SIZE_ENEMY)
            enemies.add(enemy)
            create_time = enemy.create_time

    elif len(bosses) < 1 and score > ENEMY_COUNT-40:
        boss = Boss(SIZE_BOSS, SIZE_BOSS)
        bosses.add(boss)

    player.update()
    bullets.update()
    enemies.update()
    bosses.update()

    screen.fill(BLACK)
    display_background()

    if datetime.now() - start_time > timedelta(seconds=1):
        start_time = datetime.now()
        SPEED_ENEMY += 0.1

    for boss in bosses:
        boss.draw_health_bar()
        screen.blit(boss.image, boss.rect)
    for enemy in enemies:
        enemy.draw_health_bar()
        screen.blit(enemy.image, enemy.rect)
    for bullet in bullets:
        screen.blit(bullet.image, bullet.rect)
    screen.blit(player.image, player.rect)

    game_text_update()

    for enemy in enemies:
        if player.collidercircle(enemy, player.width / 2):
            enemy.kill()
            player.lives -= 1
            if player.lives == 0:
                looser()
    clock.tick(60)
    pygame.display.update()
    if winner:
        break
font = pygame.font.SysFont(None, 84)
winner_text = font.render("Поздравляю вы победили Путина!", True, BLACK)

text_width, text_height = font.size("Поздравляю вы победили Путина!")
text_x = (WIDTH - text_width) / 2
text_y = (HEIGHT - text_height) / 2


background_image = pygame.image.load("assets/img/flag.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
screen.fill(BLACK)
screen.blit(background_image, (0, 0))
screen.blit(winner_text, (text_x, text_y))
pygame.display.update()
pygame.time.wait(1000)
pygame.mixer.music.load("assets/audio/winner.wav")
pygame.mixer.music.play()
pygame.time.wait(130000)
reset()
