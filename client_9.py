import socket
import pygame
import math

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Настраиваем сокет
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Отключаем пакетирование
sock.connect(("localhost", 10000))

pygame.init()

WIDTH = 800
HEIGHT = 600
radius = 50
CC = (WIDTH // 2, HEIGHT // 2)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Бактерии")

# Переменные для вектора
old = (0, 0)

run = True
while run:
    for event in pygame.event.get():
        if event == pygame.QUIT:
            run = False

        # Получение состояния от сервера
        data = sock.recv(1024).decode()
        print("Получил:", data)

    # Проверка фокуса мыши и расчёт вектора
    if pygame.mouse.get_focused():
        pos = pygame.mouse.get_pos()
        vector = pos[0] - CC[0], pos[1] - CC[1]

        lenv = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
        if lenv <= radius:
            vector = 0, 0

        elif lenv > 0:  # избегаем деления на ноль
            vector = (vector[0] / lenv, vector[1] / lenv)

        if vector != old:
            old = vector
            msg = f"<{vector[0]},{vector[1]}>"
            sock.send(msg.encode())



    screen.fill('gray')
    pygame.draw.circle(screen, (255, 0, 0), CC, radius)
    pygame.display.update()

pygame.quit()