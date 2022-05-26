import signal
import socket
import sys
import threading
from functools import partial
from json import JSONDecodeError, dumps, loads
from math import sqrt

import pygame

HEIGTH, WIDTH = 800, 800
FPS = 60
SIZE = 10
SPEED = 10
IP = "172.30.16.199"
PORT = 1235
RUN = True


def signal_handler(
    client: socket.socket,
    sig,
    frame,
):
    client.send("DISCONNECT".encode())
    print("\nClosing server ")
    client.close()
    sys.exit(1)


class Player(pygame.sprite.Sprite):
    def __init__(self, is_killer, is_player=False):
        super().__init__()
        self.surf = pygame.Surface((SIZE, SIZE))
        if is_killer:
            color = (255, 0, 0)
        elif is_player:
            color = (32, 252, 3)
        else:
            color = (255, 255, 255)
        self.surf.fill(color)
        self.rect = self.surf.get_rect()
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGTH // 2

    def move(self, client, id_client):
        pressed_keys = pygame.key.get_pressed()
        if pygame.KEYDOWN:
            send = False
            x, y = 0, 0
            if (
                pressed_keys[pygame.K_LEFT]
                or pressed_keys[pygame.K_RIGHT]
                or pressed_keys[pygame.K_UP]
                or pressed_keys[pygame.K_DOWN]
            ):
                send = True
            if pressed_keys[pygame.K_LEFT]:
                x = -SPEED
            if pressed_keys[pygame.K_RIGHT]:
                x = SPEED

            if pressed_keys[pygame.K_UP]:
                y = -SPEED
            if pressed_keys[pygame.K_DOWN]:
                y = SPEED
            # Normalize diagonal
            if x != 0 and y != 0:
                x = x * (sqrt(2) / 2)
                y = y * (sqrt(2) / 2)
            if self.rect.x > WIDTH:
                self.rect.x = 0
            if self.rect.x < 0:
                self.rect.x = WIDTH

            if self.rect.y > HEIGTH:
                self.rect.y = 0
            if self.rect.y < 0:
                self.rect.y = HEIGTH

            self.rect.x += x
            self.rect.y += y
            if send:
                client.send(
                    bytes(
                        dumps(
                            {"id_client": id_client, "x": self.rect.x, "y": self.rect.y}
                        ),
                        encoding="utf-8",
                    )
                )


def recv_data(conn: socket.socket, all_sprites, id_user):
    while True:
        data = conn.recv(1024)
        if data == b"bye":
            break
        if data:
            try:
                data = loads(data.decode("utf-8"))
            except JSONDecodeError:
                continue
            id_conn, pox, posy = data["id_client"], data["x"], data["y"]
            if id_conn != id_user:
                user = all_sprites[id_conn]
                user.rect.x = pox
                user.rect.y = posy
        else:
            break


# if are impostor set red else random color, and get id_
def main(client, data):
    id_user, room_size, is_killer, id_killer = (
        data["id"],
        data["room_size"],
        data["killer"],
        data["id_killer"],
    )
    pygame.init()
    signal.signal(signal.SIGINT, partial(signal_handler, client))

    clock = pygame.time.Clock()
    window = pygame.display.set_mode((WIDTH, HEIGTH))

    all_sprites = []
    p1 = Player(is_killer, True)
    for i in range(room_size):
        # If is different add other players
        if i != id_user:
            # use id_killer to assing red color
            if i == id_killer:
                all_sprites.append(Player(True))
            else:
                all_sprites.append(Player(False))
        else:
            all_sprites.append(p1)

    threading.Thread(target=recv_data, args=(client, all_sprites, id_user)).start()
    posx,posy = 0,0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.send("DISCONNECT".encode())
                RUN = False
                pygame.quit()
                sys.exit()

        window.fill((0, 0, 0))

        p1.move(client, id_user)
        for entity in all_sprites:
            if entity is p1:
                posx,posy = entity.rect.x,entity.rect.y
            else:
                pygame.draw.line(window,(255,255,255),(posx,posy),(entity.rect.x,entity.rect.y),3)
            
            window.blit(entity.surf, entity.rect)
        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((IP, PORT))
    except ConnectionRefusedError:
        print("Error, can't not connect")
        sys.exit(1)

    print("Waiting to server...")
    try:
        data = loads(client.recv(1024).decode("utf-8"))
    except JSONDecodeError:
        print("Exit")
        sys.exit(1)
    main(client, data)
