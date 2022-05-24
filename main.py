import math
import socket
import sys
import pygame
import threading
import pickle

HEIGTH,WIDTH = 300,300
FPS = 60
SIZE = 30
SPEED = 10
IP = "localhost"
PORT = 1237

class Player(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.surf = pygame.Surface((SIZE, SIZE))
        self.surf.fill((128,255,40))
        self.rect = self.surf.get_rect()
        self.pos = pygame.math.Vector2((10, 385))

    def move(self,conn:socket.socket):
        send = False
        pressed_keys = pygame.key.get_pressed()
        x,y = 0,0
        if pressed_keys[pygame.K_LEFT]:
            x = -SPEED
            send = True
        if pressed_keys[pygame.K_RIGHT]:
            x = SPEED
            send = True
        
        if pressed_keys[pygame.K_UP]:
            y = -SPEED
            send = True
        if pressed_keys[pygame.K_DOWN]:
            y = SPEED
            send = True
        if x != 0 and y!=0:
            x = x*(math.sqrt(2)/2)
            y = y*(math.sqrt(2)/2)
        
        if self.rect.x > WIDTH-SIZE:
            x = 0
            self.rect.x = WIDTH- SIZE

        if self.rect.x < 0:
            self.rect.x = 0
            x = 0
        
        if self.rect.y > HEIGTH-SIZE:
            y = 0
            self.rect.y = HEIGTH - SIZE


        if self.rect.y < 0:
            self.rect.y = 0
            y = 0

        self.rect.x += x
        self.rect.y += y

        if send:
            conn.send(pickle.dumps(self.rect))

def recv_data(conn:socket.socket):
    while True:
        data = conn.recv(1024)
        if data:
            print(pickle.loads(data))
        else:
            break

def main_funct(client):
    pygame.init()
    clock = pygame.time.Clock()
    window = pygame.display.set_mode((WIDTH,HEIGTH))
    pygame.display.set_caption("Las traes")
    all_sprites = pygame.sprite.Group()
    P1 = Player()
    all_sprites.add(P1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        window.fill((0,0,0))
    
        P1.move(client)
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
    rect_th = threading.Thread(target=recv_data,args=(client,))
    rect_th.start()
    main_th = threading.Thread(target=main_funct,args=(client,))
    main_th.start()

    