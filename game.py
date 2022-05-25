import pygame
from random import randint
from math import sqrt
import sys
import socket
import threading

HEIGTH, WIDTH = 300, 300
FPS = 60
SIZE = 30
SPEED = 10
IP = "localhost"
PORT = 1235


class Player(pygame.sprite.Sprite):
    def __init__(self,posx,posy):
        super().__init__()
        self.surf = pygame.Surface((SIZE, SIZE))
        self.surf.fill([randint(0, 255) for _ in range(3)])
        self.rect = self.surf.get_rect()
        self.rect.x= posx
        self.rect.y = posy

    def move(self,client):
        pressed_keys = pygame.key.get_pressed()
        if pygame.KEYDOWN:
            send = False
            x, y = 0, 0
            if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_RIGHT]\
            or pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_DOWN]:
                send = True
            if pressed_keys[pygame.K_LEFT]:
                x = -SPEED
            if pressed_keys[pygame.K_RIGHT]:
                x = SPEED

            if pressed_keys[pygame.K_UP]:
                y = -SPEED
            if pressed_keys[pygame.K_DOWN]:
                y = SPEED
            if x != 0 and y != 0:
                x = x * (sqrt(2) / 2)
                y = y * (sqrt(2) / 2)
            self.rect.x += x
            self.rect.y += y
            if send:
                print(f"send{self.rect.x},{self.rect.y}")
                client.send(f'{self.rect.x},{self.rect.y}'.encode())

def recv_data(conn:socket.socket):
    while True:
        data = conn.recv(1024)
        if data:
            print(data.decode())
        else:
            break

#if are impostor set red else random color, and get id_
def main(client):
    pygame.init()
    threading.Thread(target=recv_data,args=(client,)).start()
    clock = pygame.time.Clock()
    window = pygame.display.set_mode((WIDTH, HEIGTH))
    all_sprites = pygame.sprite.Group()
    p1 = Player(10,50)
    all_sprites.add(p1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        window.fill((0, 0, 0))

        p1.move(client)
        
        for entity in all_sprites:
            window.blit(entity.surf, entity.rect)
        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        client.connect((IP,PORT))
    except ConnectionRefusedError:
        print("Error, can't not connect")
        sys.exit(1)
    print("Waiting to server...")
    confirmation = client.recv(5).decode()
    if confirmation == "START":
        main(client)
