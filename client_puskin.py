import socket
import time

# Стихотворение: первая строфа "Я помню чудное мгновенье..."
lines = [
    "Я помню чудное мгновенье:",
    "Передо мной явилась ты,",
    "Как мимолётное виденье,",
    "Как гений чистой красоты.",
    "В томленьях грусти безнадежной,",
    "В тревогах шумной суеты,",
    "Звучал мне долго голос нежный",
    "И снились милые черты."
]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(("localhost", 10000))

print("Подключён к серверу. Отправляю строки стихотворения...")


for line in lines:
    sock.send(line.encode())
    print(f"→ Отправлено: {line}")
    time.sleep(1)  # небольшая задержка, чтобы сервер успевал обработать
