import socket
import threading

from protocol import send_message, recv_message


HOST = '127.0.0.1'
PORT = 9090


def get_messages(s):
    try:
        while True:
            message = recv_message(s)

            if message is None:
                print("Сервер закрыл соединение")
                break

            command, data = message
            text = data.decode("utf-8")

            if command == "TEXT":
                print()
                print(text)

            elif command == "LIST":
                print()
                print("Сейчас в чате:")
                print(text)

            elif command == "ERR!":
                print()
                print(f"Ошибка: {text}")

    except ConnectionResetError:
        print("Соединение было сброшено")

    except BrokenPipeError:
        print("Соединение разорвано")

    except ConnectionError:
        print("Соединение закрыто")

    except OSError as error:
        print(f"Ошибка: {error}")


name = input("Введите имя: ")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect((HOST, PORT))

    print("Соединение с сервером установлено")

    send_message(
        s,
        "JOIN",
        name.encode("utf-8")
    )

    thread = threading.Thread(
        target=get_messages,
        args=(s,),
        daemon=True
    )

    thread.start()

    print()
    print("Команды:")
    print("/list - посмотреть пользователей")
    print("/quit - выйти")
    print()

    while True:
        text = input("> ")

        if text == "/list":
            send_message(
                s,
                "LIST",
                b""
            )

        elif text == "/quit":
            send_message(
                s,
                "QUIT",
                b""
            )
            break

        elif text:
            send_message(
                s,
                "TEXT",
                text.encode("utf-8")
            )

except ConnectionRefusedError:
    print("Не удалось подключиться к серверу")

except ConnectionResetError:
    print("Соединение было сброшено")

except BrokenPipeError:
    print("Соединение разорвано")

except OSError as error:
    print(f"Ошибка: {error}")

finally:
    s.close()
