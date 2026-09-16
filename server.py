import socket
import threading

from protocol import send_message, recv_message


HOST = '0.0.0.0'
PORT = 9090

users = {}


def work_with_client(conn, addr):
    name = None

    try:
        while True:
            message = recv_message(conn)

            if message is None:
                break

            command, data = message

            if command == "JOIN":
                name = data.decode("utf-8")
                users[conn] = name

                print(f"Новый клиент: {addr}")
                print(f"Имя: {name}")

            elif command == "TEXT":
                text = data.decode("utf-8")

                print(f"{name}: {text}")

                for client in list(users):
                    if client != conn:
                        try:
                            send_message(
                                client,
                                "TEXT",
                                f"{name}: {text}".encode("utf-8")
                            )
                        except ConnectionResetError:
                            print("Клиент отключился")
                        except BrokenPipeError:
                            print("Отправка не выполнена")
                        except OSError as error:
                            print(f"Ошибка: {error}")

            elif command == "LIST":
                names = "\n".join(users.values())

                send_message(
                    conn,
                    "LIST",
                    names.encode("utf-8")
                )

            elif command == "QUIT":
                print(f"{name} вышел")
                break

            else:
                send_message(
                    conn,
                    "ERR!",
                    f"Неизвестная команда: {command}".encode("utf-8")
                )

    except ConnectionResetError:
        print(f"Клиент аварийно отключился: {addr}")

    except BrokenPipeError:
        print(f"Соединение больше недоступно: {addr}")

    except ConnectionError:
        print(f"Соединение закрыто: {addr}")

    except OSError as error:
        print(f"Ошибка: {error}")

    finally:
        users.pop(conn, None)

        conn.close()

        if name:
            for client in list(users):
                try:
                    send_message(
                        client,
                        "TEXT",
                        f"Система: {name} покинул чат".encode("utf-8")
                    )
                except ConnectionResetError:
                    print("Клиент уже отключился")
                except BrokenPipeError:
                    print("Не удалось отправить сообщение")
                except OSError as error:
                    print(f"Ошибка отправки: {error}")

        print(f"Клиент отключен: {addr}")


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((HOST, PORT))
s.listen()

print("Сервер запущен")


try:
    while True:
        conn, addr = s.accept()

        print(f"Подключение: {addr}")

        thread = threading.Thread(
            target=work_with_client,
            args=(conn, addr)
        )

        thread.start()

except KeyboardInterrupt:
    print("Сервер остановлен")

finally:
    s.close()
