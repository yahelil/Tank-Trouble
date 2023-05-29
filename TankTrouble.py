import sys
from PrimarySettings import *
from pytmx.util_pygame import load_pygame
import math
import random
import time

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()


class Tank:
    def __init__(self, x, y, color):
        if color == "Blue":
            self.image = pygame.image.load(path.join(IMAGE_FOLDER, BlueTANK_IMAGE)).convert_alpha()
        else:
            self.image = pygame.image.load(path.join(IMAGE_FOLDER, GreenTank_IMAGE)).convert_alpha()
        self.rotated_image = self.image
        self.x = x
        self.y = y
        self.angle = 0
        self.bullets = []
        self.time_last_bullet = 0
        self.offset = 16
        self.color = color  # The tanks color
        self.score = 0  # The score of the other tank / The number of times the tank got hit
        self.score_text = pygame.font.Font(None, 36).render(f'{self.color} Score: {self.score}', True, (0, 0, 0))

    def tank_game_loop(self):
        if self.color == "Blue":
            self.handle_blue_keys()
        elif self.color == "Green":
            self.handle_green_keys()
        self.draw()
        self.update_bullets()
        self.score_board()

    def update_bullets(self):
        for bullet in self.bullets:
            rad = math.radians(bullet.angle)
            current_pos = (bullet.col, bullet.row)  # + (BulletSpeed * math.sin(rad), BulletSpeed * math.cos(rad))
            future_pos = (bullet.col + BulletSpeed * math.sin(rad), bullet.row + BulletSpeed * math.cos(rad))
            collision_bool, action_num = self.collision_bullet(current_pos, future_pos)
            if not collision_bool:
                bullet.row += BulletSpeed * math.cos(rad)
                bullet.col += BulletSpeed * math.sin(rad)
            else:
                if bullet.angle < 0:
                    bullet.angle += 360
                if action_num == 0: # right or left
                    print(f" door 0, angle: {bullet.angle}")
                    if 0 < bullet.angle < 90:
                        bullet.angle *= -1
                    elif 90 < bullet.angle < 180:
                        bullet.angle = 180 - bullet.angle
                    elif 270 < bullet.angle < 360:
                        bullet.angle = 360 - bullet.angle
                    print(bullet.angle)
                elif action_num == 1: # above or below
                    print(f" door 1, angle: {bullet.angle}")
                    if 0 < bullet.angle < 90:
                        print(bullet.angle)
                        bullet.angle = 180 - bullet.angle
                        print(bullet.angle)
                    elif 90 < bullet.angle < 180:
                        print(bullet.angle)
                        bullet.angle = 180 - bullet.angle
                        print(bullet.angle)
                    elif 180 < bullet.angle < 360:
                        bullet.angle = 540 - bullet.angle
                    else:
                        print(bullet.angle)
                        bullet.angle = 180 - bullet.angle
                        print(bullet.angle)
            time_a = time.time()
            bullet.draw()
            if self.did_hit((bullet.col, bullet.row)):
                self.score += 1
                print(self.score)
                if self.score == 2:
                    self.winning_screen()
                    quit()
                else:
                    self.win_reset()
            if time_a - bullet.start_time > KillTime:
                self.bullets.pop(self.bullets.index(bullet))

    def handle_blue_keys(self):
        rad = math.radians(self.angle)
        key = pygame.key.get_pressed()
        if key[pygame.K_UP]:
            future_pos = (self.x + PlayerSpeed * math.sin(rad), self.y + PlayerSpeed * math.cos(rad))
            if not self.collision_tank(future_pos, 16):
                self.y += PlayerSpeed * math.cos(rad)
                self.x += PlayerSpeed * math.sin(rad)
        if key[pygame.K_DOWN]:
            future_pos = (self.x - PlayerSpeed * math.sin(rad), self.y - PlayerSpeed * math.cos(rad))
            if not self.collision_tank(future_pos, 16):
                self.y -= PlayerSpeed * math.cos(rad)
                self.x -= PlayerSpeed * math.sin(rad)
        if key[pygame.K_RIGHT]:
            self.angle = (self.angle + 3) % 360
        if key[pygame.K_LEFT]:
            self.angle = (self.angle - 3) % 360
        if key[pygame.K_SPACE] and time.time() - self.time_last_bullet > CoolDown:
            if len(self.bullets) < MaxBullets:
                self.shoot()
                self.time_last_bullet = time.time()
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)

    def handle_green_keys(self):
        rad = math.radians(self.angle)
        key = pygame.key.get_pressed()
        if key[pygame.K_w]:
            future_pos = (self.x + PlayerSpeed * math.sin(rad), self.y + PlayerSpeed * math.cos(rad))
            if not self.collision_tank(future_pos, 16):
                self.y += PlayerSpeed * math.cos(rad)
                self.x += PlayerSpeed * math.sin(rad)
        if key[pygame.K_s]:
            future_pos = (self.x - PlayerSpeed * math.sin(rad), self.y - PlayerSpeed * math.cos(rad))
            if not self.collision_tank(future_pos, 16):
                self.y -= PlayerSpeed * math.cos(rad)
                self.x -= PlayerSpeed * math.sin(rad)
        if key[pygame.K_d]:
            self.angle = (self.angle + 3) % 360
        if key[pygame.K_a]:
            self.angle = (self.angle - 3) % 360
        if key[pygame.K_q] and time.time() - self.time_last_bullet > CoolDown:
            if len(self.bullets) < MaxBullets:
                self.shoot()
                self.time_last_bullet = time.time()
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)

    def shoot(self):
        self.bullets.append(Bullet(self.angle, self.x, self.y))

    def did_hit(self, current_pos): # did one of the bullets hit a tank
        for tank in Tanks:
            if (tank.x) <= current_pos[0] <= tank.x + 31 and tank.y <= current_pos[1] <= tank.y + 35:
                return True
        return False
        # Got a problem, When the angle is small the bullet is in the area of the tank and identifies as a hit

    def winning_screen(self):
        pass

    def win_reset(self):
        self.bullets.clear()
        for Tank_obj in tanks_layer:  # Loop through the tiles till last tile
            for Tank in Tanks:
                if Tank_obj.name == "BlueTank" and Tank.color == "Blue":
                    Tank.x = Tank_obj.x
                    Tank.y = Tank_obj.y
                elif Tank_obj.name == "GreenTank" and Tank.color == "Green":
                    Tank.x = Tank_obj.x
                    Tank.y = Tank_obj.y
    def collision_bullet(self, current_pos, future_pos):
        for pos in pos_list:
            if pos[0] < future_pos[0] < pos[0] + 16 and pos[1] < future_pos[1] < pos[1] + 16:
                if pos[0] + 16 < future_pos[0] + 12 or pos[0] > current_pos[0]:
                    print('right or left')
                    return True, 0
                if pos[1] + 16 < future_pos[1] + 11 or pos[1] > current_pos[1]:
                    print('above or below')
                    return True, 1
                '''
                if current_pos[0] <= pos[0] or current_pos[0] >= pos[0] - 16:
                    print('right or left')
                    return True, 0
                if current_pos[1] <= pos[1] or current_pos[1] >= pos[1] - 16:
                    print('above or below')
                    return True, 1
                '''
        return False, 0

    def collision_tank(self, future_pos, offset):
        for pos in pos_list:
            if pos[0] - offset < future_pos[0] < pos[0] + 16 + offset and pos[1] - offset < future_pos[1] < pos[1] + 16+ offset:
                return True
        return False

    def score_board(self):
        if self.color == "Blue":
            screen.blit(self.score_text, (50, 50))
        else:
            screen.blit(self.score_text, (220, 50))

    def draw(self):
        screen.blit(self.rotated_image, (self.x - self.image.get_width() / 2, self.y - self.image.get_height() / 2))


class Bullet:
    def __init__(self, angle, col, row):
        self.image = pygame.image.load(path.join(IMAGE_FOLDER, BULLET_IMAGE)).convert_alpha()
        self.row = row
        self.col = col
        self.angle = angle
        self.start_time = time.time()
        self.offset = 0

    def draw(self):
        screen.blit(self.image, (self.col - self.image.get_width() / 2, self.row - self.image.get_height() / 2))


class Wall:
    def __init__(self, row, col):
        self.image = pygame.image.load(path.join(IMAGE_FOLDER, WALL_IMAGE)).convert()
        self.row = row * 12
        self.col = col * 12
        self.draw()

    def draw(self):
        screen.blit(self.image, (self.col, self.row))


random_number = random.randint(1, 20)
Tanks = []


class WallTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)


tmx_data = load_pygame('C:/Users/yahel/tiled/TankTroubleMap.tmx')
sprite_group = pygame.sprite.Group()  # Create sprite group
print(tmx_data.layers)  # Print layers in tmx_data
wall_layer = tmx_data.get_layer_by_name("Walls")  # get layer named "Walls"
pos_list = []
for x, y, surf in wall_layer.tiles():  # Loop through the tiles till last tile
    pos = (x * 16, y * 16)  # Initialize pos variable
    pos_list.append(pos)
    WallTile(pos=pos, surf=surf, groups=sprite_group)  # Create wall tile
tanks_layer = tmx_data.get_layer_by_name("Tanks")  # get layer named "Tanks"
for Tank_obj in tanks_layer:  # Loop through the tiles till last tile
    if Tank_obj.name == "BlueTank":
        tank = Tank(Tank_obj.x, Tank_obj.y, "Blue")
    elif Tank_obj.name == "GreenTank":
        tank = Tank(Tank_obj.x, Tank_obj.y, "Green")
    else:
        tank = None
    Tanks.append(tank)  # Append Tank in Tanks
while True:  # While true
    for event in pygame.event.get():  # Loop through pygame events
        if event.type == pygame.QUIT:  # Close the game
            pygame.quit()  # close the pygame
            sys.exit()  # exit from game

    screen.fill(WHITE)  # fill screen with white color
    sprite_group.draw(screen)  # draw sprite on screen
    for tank in Tanks:  # Loop through Tanks
        tank.tank_game_loop()  # Handle tank keys, draw it and handle its bullets
        if tank.color == "Blue":
            screen.blit(tank.score_text, (50, 50))
        else:
            screen.blit(tank.score_text, (220, 50))
    pygame.display.flip()  # Flip the pygame screen
    clock.tick(FPS) / 1000  # Tick the clock
