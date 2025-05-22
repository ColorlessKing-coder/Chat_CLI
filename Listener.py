import socket
import threading
from rich import print
from datetime import datetime
import base64
import random

class Listener:
    def __init__(self) -> None:
        self.clients = {}  # keys = connection || values = user_name
        self.log_file = "log_file.txt"
        self.encode = "utf-8"
        self.users_color = {}  # keys = username || values == colors
        self.colors = ["red", "green", "yellow", "blue", "magenta", "cyan"]

    def assign_color(self, nickname):
        if nickname not in self.users_color:
            self.users_color[nickname] = random.choice(self.colors)

    # Upload Edilen Veriyi Kayıt Etmek 
    def save_uploaded_file(self, file_name, content):
        try:
            file_content = base64.b64decode(content)  # Gelen İçeriği Çevirdik
            with open(file_name, "wb") as file:  # Binary olarak yazıyoruz
                file.write(file_content)
            print(f"File {file_name} saved successfully.")
        except Exception as e:
            print("Error:", e)

    def users_info(self):
        # Şimdi İsteği Aldık Tekrar Mesajın İçin Mesaj Yazalım Ki Doğru Mesajı İstemci tarafında Yaalamak Adına
        user_list = " / ".join(self.clients.values())
        return f"{user_list}".encode()

    def log_message(self, message):
        with open(self.log_file, "a") as file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"[{timestamp}] {message}\n")

    def broadcast(self, message, sender_connection=None):
        for other_connection in self.clients.keys():
            if other_connection != sender_connection:  # Gönderen istemci dışında tüm istemcilere gönder
                try:
                    if message == "GET_USERS":
                        pass
                    else:
                        other_connection.send(message.encode(self.encode))
                except:
                    self.disconnect_client(other_connection)

    def handle_client(self, connection, address):
        try:
            nickname = connection.recv(1024).decode().strip()

            if nickname in self.clients.values():
                connection.send("[red]Nickname already taken. Please try again.[/red]".encode())
                connection.close()
                return

            self.clients[connection] = nickname  # Gelen Bağlantıya Kullanıcıyı Atadık, Bağlantıyı nickname Olarak Tutuyoruz
            self.assign_color(nickname)
            join_message = f"[{self.users_color[nickname]}]{nickname} has joined the chat.[/]"
            self.log_message(join_message)
            self.broadcast(f"{join_message}", connection)
            print(f"[green]{nickname} connected from {address[0]}:{address[1]}[/green]")

            while True:
                response_message = connection.recv(4096).decode().strip()

                # Kullanıcı listesini istemek için komut
                if response_message.startswith("GET_USERS"):
                    try:
                        _, user_info = response_message.split()  # Dikkat User_info mesajı gönderen kişiyi temsil ediyor burada
                        for connect, user_name in self.clients.items():
                            if user_name == user_info:  # Bağlantıyı kullanıcı adına göre bul
                                user_list = self.users_info()
                                connection.send(f"TAKE_USERS {user_list.decode()}".encode())  # İlgili bağlantıya kullanıcı listesini gönder
                    except ValueError:
                        connection.send("Invalid GET_USERS format. Use: GET_USERS <username>".encode())
                    continue

                if response_message.startswith("RECEIVER_MESSAGE_NAME"):
                    try:
                        _ , user_name , content = response_message.split(maxsplit=2)  # Dikkat user_name Mesajı Kime Göndereceğini Temsil Ediyor
                        full_message = f'[red]{nickname}:[/red]{content}'  # NickName Mesajı Gönderen Bağlantının İsmi
                        for connect , user in self.clients.items():
                            if self.clients[connect] == user_name:
                                connect.send(f'TAKE_SPECIAL_MESSAGE {full_message}'.encode(self.encode))  # kullanarak, metni UTF-8 formatında bytes türüne dönüştürdük.

                    except Exception as e:
                        print("Error : " ,e)
                    continue  

                if response_message.startswith("UPLOAD"):
                    try:
                        _, receiver_name, file_name, content = response_message.split(maxsplit=3)
                        for client_conn, client_name in self.clients.items():
                            if client_name == receiver_name:
                                client_conn.send(f"TAKE_UPLOADED_DATA {file_name} {content}".encode(self.encode))
                                break
                    except Exception as e:
                        print("[red]UPLOAD parsing error:[/red]", e)


                if response_message.lower() in ["exit", "q"]:
                    leave_message = f"[{self.users_color[nickname]}]{nickname} has left the chat.[/]"
                    self.log_message(leave_message)
                    self.broadcast(f"[yellow]{leave_message}[/yellow]", connection)
                    break

                # Normal mesaj iletimi
                full_message = f"[{self.users_color[nickname]}]{nickname}[/]: {response_message}"
                self.log_message(full_message)
                self.broadcast(full_message, connection)

        except Exception as e:
            print(f"[red]Error handling client {address}:[/red] {e}")
        finally:
            self.disconnect_client(connection)

    def listen_for_connections(self, ip_address, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind((ip_address, port))
                sock.listen()
                print("[green]Server is listening for connections...[/green]")

                while True:
                    connection, address = sock.accept()
                    threading.Thread(target=self.handle_client, args=(connection, address)).start()

        except Exception as e:
            print(f"[red]Server Error:[/red] {e}")

    def disconnect_client(self, connection):
        nickname = self.clients.get(connection, "Unknown User")
        if nickname:
            leave_message = f"{nickname} has left the chat."
            self.log_message(leave_message)
            print(f"[yellow]{leave_message}[/yellow]")
            self.broadcast(f"[yellow]{leave_message}[/yellow]", connection)
            del self.clients[connection]
            connection.close()


def main():
    listener = Listener()
    ip = "127.0.0.1"
    port = 50001
    listener.listen_for_connections(ip, port)

if __name__ == "__main__":
    main()
