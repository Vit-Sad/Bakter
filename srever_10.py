import socket
import pygame
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


def find(vector: str):
    first = None
    for num, sign in enumerate(vector):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            result = map(int, vector[first + 1:second].split(","))
            return result
    return ""


# Настройка БД
engine = create_engine("postgresql+psycopg2://postgres:1111@localhost/rebotica")
Session = sessionmaker(bind=engine)
Base = declarative_base()
s = Session()


class Player(Base):
    __tablename__ = "gamers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250))
    address = Column(String)
    x = Column(Integer, default=500)
    y = Column(Integer, default=500)
    size = Column(Integer, default=50)
    errors = Column(Integer, default=0)
    abs_speed = Column(Integer, default=2)
    speed_x = Column(Integer, default=2)
    speed_y = Column(Integer, default=2)

    def __init__(self, name, address):
        self.name = name
        self.address = address


class LocalPlayer:
    def __init__(self, id, name, sock, addr):
        self.id = id
        self.db: Player = s.get(Player, self.id)
        self.sock = sock
        self.name = name
        self.address = addr
        self.x = 500
        self.y = 500
        self.size = 50
        self.errors = 0
        self.abs_speed = 2
        self.speed_x = 2
        self.speed_y = 2

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def change_speed(self, vector):
        vector = find(vector)
        if vector[0] == 0 and vector[1] == 0:
            self.speed_x = self.speed_y = 0
        else:
            vector = vector[0] * self.abs_speed, vector[1] * self.abs_speed
            self.speed_x = vector[0]
            self.speed_y = vector[1]


Base.metadata.create_all(engine)

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(("localhost", 10000))
main_socket.setblocking(False)
main_socket.listen(5)
print("Сокет создался")

players = {}

pygame.init()
WIDHT_ROOM, HEIGHT_ROOM = 4000, 4000
WIDHT_SERVER, HEIGHT_SERVER = 300, 300
FPS = 100
screen = pygame.display.set_mode((WIDHT_SERVER, HEIGHT_SERVER))
pygame.display.set_caption("Сервер")
clock = pygame.time.Clock()

server_works = True
while server_works:
    clock.tick(FPS)

    try:
        new_socket, addr = main_socket.accept()
        print('Подключился', addr)
        new_socket.setblocking(False)
        player = Player("Имя", str(addr))
        s.merge(player)
        s.commit()

        addr_str = str(addr)
        data = s.query(Player).filter(Player.address == addr_str)
        for user in data:
            player = LocalPlayer(user.id, "Имя", new_socket, addr_str)
            players[user.id] = player

    except BlockingIOError:
        pass

    # Считываем команды игроков
    for id in list(players):
        try:
            data = players[id].sock.recv(1024).decode()
            print("Получил", data)
            players[id].change_speed(data)
        except:
            pass

    # Обновление позиций игроков
    for id in list(players):
        players[id].update()

    # Отрисовка серверного окна
    screen.fill('black')
    for id in players:
        player = players[id]
        x = player.x * WIDHT_SERVER // WIDHT_ROOM
        y = player.y * HEIGHT_SERVER // HEIGHT_ROOM
        size = player.size * WIDHT_SERVER // WIDHT_ROOM
        pygame.draw.circle(screen, "yellow2", (x, y), size)

    pygame.display.update()

    # Обработка событий Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server_works = False

    # Отправка статуса игрового поля
    for id in list(players):
        try:
            players[id].sock.send("Игра".encode())
        except:
            players[id].sock.close()
            del players[id]
            s.query(Player).filter(Player.id == id).delete()
            s.commit()
            print("Сокет закрыт")

pygame.quit()
main_socket.close()
s.query(Player).delete()
s.commit()