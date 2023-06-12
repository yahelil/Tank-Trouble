import socket

import pygame
from server import send_msg, receive_msg
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


class Client:
    def __init__(self, _client_socket, color=""):
        self.client_socket = _client_socket
        self.color = color

    def connect(self):
        self.client_socket.connect(("127.0.0.1", 80))
        print("connected")
        self.color = "blue" if self.client_socket.recv(1) == b'B' else "green"


class Tank(Client):
    def __init__(self, x, y, sock, color):
        Client.__init__(self, sock, color)
        if self.color == "blue":
            self.image = pygame.image.load(path.join(IMAGE_FOLDER, BlueTANK_IMAGE)).convert_alpha()
            self.opposing_image = pygame.image.load(path.join(IMAGE_FOLDER, GreenTank_IMAGE)).convert_alpha()
        else:
            self.image = pygame.image.load(path.join(IMAGE_FOLDER, GreenTank_IMAGE)).convert_alpha()
            self.opposing_image = pygame.image.load(path.join(IMAGE_FOLDER, BlueTANK_IMAGE)).convert_alpha()
        self.rotated_image = self.image
        self.rotated_opposing = self.opposing_image
        self.x = x
        self.y = y
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))
        self.rect_opposing = self.rotated_opposing.get_rect()
        self.angle = 0
        self.bullets = []
        self.opposing_bullets = []
        self.time_last_bullet = 0
        self.offset = 16
        self.score = 0  # The score of the other tank / The number of times the tank got hit
        self.score_text = pygame.font.Font(None, 36).render(f'{self.color} Score: {self.score}', True, (0, 0, 0))
        self.win_text = pygame.font.Font(None, 36).render(f'{self.color} won!!!!', True, (0, 0, 0))

    def send_bullets(self):
        msg = ""
        for bullet in self.bullets:
            msg += f"{bullet.row},{bullet.col}|"  # string of all the bullet positions separated by '|'
        send_msg(self.client_socket, msg)

    def send_position(self):
        msg = str(self.x)+','+str(self.y)+','+str(self.angle)
        send_msg(self.client_socket, msg)

    def receive_position(self):
        list = receive_msg(self.client_socket).split(',')  # list of pos and angle from the other tank
        list = [float(x) for x in list]  # the list with floats and not strings
        msg = tuple(list)  # converting the list to a tuple
        pos = [msg[0], msg[1]]  # list of the pos only
        self.rotated_opposing = pygame.transform.rotate(self.opposing_image, msg[2])
        # rotate the other tank by angle(msg[2])
        self.rect_opposing = self.rotated_opposing.get_rect(center=pos)
        self.draw_opposing()  # draw the other tank

    def tank_game_loop(self):
        if self.color == "blue":
            self.handle_blue_keys()
        elif self.color == "green":
            self.handle_green_keys()
        self.send_position()
        self.receive_position()
        self.draw()
        self.update_bullets()
        send_msg(self.client_socket, str(len(self.bullets)))
        if len(self.bullets) > 0:
            print(len(self.bullets))
            self.send_bullets()
            self.opposing_bullets = receive_msg(self.client_socket).split("|")
            for bullet_pos in self.opposing_bullets:
                pos = bullet_pos.split(',')
                print(pos)
                if pos[0] != '':
                    bullet = Bullet(0, float(pos[0]), float(pos[1][1::]))
                    bullet.draw()
            print(f"opposing_bullets: {self.opposing_bullets}")
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
                if action_num == 0:  # right or left
                    print(f" door 0, angle: {bullet.angle}")
                    if 0 < bullet.angle < 90:
                        bullet.angle *= -1
                    elif 90 < bullet.angle < 180:
                        bullet.angle = 180 - bullet.angle
                    elif 270 < bullet.angle < 360:
                        bullet.angle = 360 - bullet.angle
                    print(bullet.angle)
                elif action_num == 1:  # above or below
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
            hit, color_hit = self.did_hit((bullet.col, bullet.row))
            if hit:
                if color_hit != self.color:
                    # if hit the other tank
                    self.score += 1
                    self.score_text = pygame.font.Font(None, 36).render(f'{self.color} Score: {self.score}', True, (0, 0, 0))
                    self.score_board()
                    print(self.score)
                    if self.score == 5:
                        screen.fill(WHITE)  # fill screen with white color
                        self.winning_screen()
                        self.win_reset(True)
                    else:
                        self.win_reset(False)
                elif time_a - bullet.start_time > 0.23:
                    for tank in Tanks:
                        if self.color != tank.color:
                            tank.score += 1
                            tank.score_text = pygame.font.Font(None, 36).render(f'{tank.color} Score: {tank.score}', True, (0, 0, 0))
                            self.score_board()
                            print(tank.score)
                        if tank.score == 5:

                            screen.fill(WHITE)  # fill screen with white color
                            self.winning_screen()
                            self.win_reset(True)
                        else:
                            self.win_reset(False)
            if time_a - bullet.start_time > KillTime:
                self.bullets.pop(self.bullets.index(bullet))

    def handle_blue_keys(self):
        has_key_been_pressed = False
        rad = math.radians(self.angle)
        key = pygame.key.get_pressed()
        if key[pygame.K_UP]:
            has_key_been_pressed = True
            future_pos = (self.x + PlayerSpeed * math.sin(rad), self.y + PlayerSpeed * math.cos(rad))
            if not self.collision_tank(future_pos, 16):
                self.y += PlayerSpeed * math.cos(rad)
                self.x += PlayerSpeed * math.sin(rad)
        if key[pygame.K_DOWN]:
            has_key_been_pressed = True
            future_pos = (self.x - PlayerSpeed * math.sin(rad), self.y - PlayerSpeed * math.cos(rad))
            if not self.collision_tank(future_pos, 16):
                self.y -= PlayerSpeed * math.cos(rad)
                self.x -= PlayerSpeed * math.sin(rad)
        if key[pygame.K_RIGHT]:
            has_key_been_pressed = True
            self.angle = (self.angle + 3) % 360
        if key[pygame.K_LEFT]:
            has_key_been_pressed = True
            self.angle = (self.angle - 3) % 360
        if key[pygame.K_SPACE] and time.time() - self.time_last_bullet > CoolDown:
            if len(self.bullets) < MaxBullets:
                self.shoot()
                bullet = self.bullets[-1]
                msg = f"{bullet.angle},{bullet.col},{bullet.row}"
                send_msg(self.client_socket, msg)
                self.time_last_bullet = time.time()
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    def handle_green_keys(self):
        has_key_been_pressed = False
        rad = math.radians(self.angle)
        key = pygame.key.get_pressed()
        if key[pygame.K_w]:
            has_key_been_pressed = True
            future_pos = (self.x + PlayerSpeed * math.sin(rad), self.y + PlayerSpeed * math.cos(rad))
            if not self.collision_tank(future_pos, 16):
                self.y += PlayerSpeed * math.cos(rad)
                self.x += PlayerSpeed * math.sin(rad)
        if key[pygame.K_s]:
            has_key_been_pressed = True
            future_pos = (self.x - PlayerSpeed * math.sin(rad), self.y - PlayerSpeed * math.cos(rad))
            if not self.collision_tank(future_pos, 4):
                self.y -= PlayerSpeed * math.cos(rad)
                self.x -= PlayerSpeed * math.sin(rad)
        if key[pygame.K_d]:
            has_key_been_pressed = True
            self.angle = (self.angle + 3) % 360
        if key[pygame.K_a]:
            has_key_been_pressed = True
            self.angle = (self.angle - 3) % 360
        if key[pygame.K_q] and time.time() - self.time_last_bullet > CoolDown:
            if len(self.bullets) < MaxBullets:
                self.shoot()
                self.time_last_bullet = time.time()
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    def shoot(self):
        self.bullets.append(Bullet(self.angle, self.x, self.y))

    def did_hit(self, current_pos):  # did one of the bullets hit a tank
        for tank in Tanks:
            if tank.x <= current_pos[0] <= tank.x + 35 and tank.y <= current_pos[1] <= tank.y + 31:
                return True, tank.color
        return False, "red"

    def winning_screen(self):
        screen.blit(self.win_text, (384, 206))
        screen.blit(pygame.font.Font(None, 36).render("Press any key to have another game...", True, (0, 0, 0)),
                    (384, 216))
        pygame.key.get_pressed()  # wait until a key is pressed

    def win_reset(self, Win):
        self.bullets.clear()
        for Tank_obj in tanks_layer:  # Loop through the tiles till last tile
            for Tank in Tanks:
                if Tank_obj.name == "BlueTank" and Tank.color == "blue":
                    Tank.x = Tank_obj.x
                    Tank.y = Tank_obj.y
                    Tank.angle = 0
                elif Tank_obj.name == "GreenTank" and Tank.color == "green":
                    Tank.x = Tank_obj.x
                    Tank.y = Tank_obj.y
                    Tank.angle = 0
                if Win:
                    Tank.score = 0
                    Tank.score_text = pygame.font.Font(None, 36).render(f'{Tank.color} Score: {Tank.score}', True, (0, 0, 0))

    def collision_bullet(self, current_pos, future_pos):
        collision_tolerance = 5
        for pos in pos_list:
            if pos[0] < future_pos[0] < pos[0] + 16 and pos[1] < future_pos[1] < pos[1] + 16:  # if there is a collision
                if abs(pos[0] + 16 - future_pos[0]) < collision_tolerance or abs(
                        pos[0] - future_pos[0] + 11) < collision_tolerance:
                    print('right or left')
                    return True, 0
                if abs(pos[1] - future_pos[1] + 12) < collision_tolerance or abs(
                        pos[1] + 16 - future_pos[1]) < collision_tolerance:
                    print('above or below')
                    return True, 1
                '''
                if pos[0] + 16 < future_pos[0] + 12 or pos[0] > current_pos[0]:
                    print('right or left')
                    return True, 0
                if pos[1] + 16 < future_pos[1] + 11 or pos[1] > current_pos[1]:
                    print('above or below')
                    return True, 1

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
            if pos[0] - offset < future_pos[0] < pos[0] + 16 + offset and pos[1] - offset < future_pos[1] < pos[1] + 16 + offset:
                return True
        return False

    def score_board(self):
        if self.color == "Blue":
            screen.blit(self.score_text, (50, 40))
        else:
            screen.blit(self.score_text, (235, 40))

    def draw(self):
        screen.blit(self.rotated_image, self.rect)

    def draw_opposing(self):
        screen.blit(self.rotated_opposing, self.rect_opposing)


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


random_number = random.randint(1, 20)
Tanks = []


class WallTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)


c = Client(socket.socket())
c.connect()

tmx_data = load_pygame('C:/Users/yahel/tiled/TankTroubleMap.tmx')
sprite_group = pygame.sprite.Group()  # Create sprite group
print(tmx_data.layers)  # Print layers in tmx_data
wall_layer = tmx_data.get_layer_by_name("Walls")  # get layer named "Walls"
pos_list = []
matrix = []
matrix_line = []
for x, y, surf in wall_layer.tiles():  # Loop through the tiles till last tile
    pos = (x * 16, y * 16)  # Initialize pos variable
    if x == 47:
        matrix.append(matrix_line)
        matrix_line.clear()
    matrix_line.append(pos)
    pos_list.append(pos)
    WallTile(pos=pos, surf=surf, groups=sprite_group)  # Create wall tile
print(f"matrix: {matrix}")
tanks_layer = tmx_data.get_layer_by_name("Tanks")  # get layer named "Tanks"
for Tank_obj in tanks_layer:  # Loop through the tiles till last tile
    if Tank_obj.name == "BlueTank" and c.color == "blue":
        tank = Tank(Tank_obj.x, Tank_obj.y, c.client_socket, c.color)
        Tanks.append(tank)  # Append Tank in Tanks
    elif Tank_obj.name == "GreenTank" and c.color == "green":
        tank = Tank(Tank_obj.x, Tank_obj.y, c.client_socket, c.color)
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
    pygame.display.flip()  # Flip the pygame screen
    clock.tick(FPS) / 1000  # Tick the clock




