import socket
import struct


MAX_MESSAGE_SIZE = 10 * 1024 * 1024


def recv_exact(s, size):
    data = b""

    while len(data) < size:
        part = s.recv(size - len(data))

        if not part:
            raise ConnectionError("Соединение закрыто")

        data += part

    return data


def send_message(s, command, data):
    command = command.encode("utf-8")

    if len(command) != 4:
        raise ValueError("Команда должна быть длиной 4 байта")

    if len(data) > MAX_MESSAGE_SIZE:
        raise ValueError("Сообщение слишком большое")

    header = command + struct.pack("!I", len(data))

    s.sendall(header)
    s.sendall(data)


def recv_message(s):
    header = s.recv(8)

    if not header:
        return None

    if len(header) < 8:
        header += recv_exact(s, 8 - len(header))

    command = header[:4].decode("utf-8")
    size = struct.unpack("!I", header[4:8])[0]

    if size > MAX_MESSAGE_SIZE:
        raise ValueError("Сообщение слишком большое")

    data = recv_exact(s, size)

    return command, data
