import socket
import threading
from rich import print
from datetime import datetime
import base64
import random
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt




class Listener:
    def __init__(self) -> None:
        self.team = {"Admin":"DG4LE9LT0NN","Wise":"123"}
        self.clients = {}  # keys = connection || values = user_name
        self.log_file = "log_file.txt"
        self.encode = "utf-8"
        self.users_color = {}  # keys = username || values == colors
        self.colors = ["red", "green", "yellow", "blue", "magenta", "cyan"]
        self.prompt = ""
        self.console = Console()
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
                    other_connection.send(message.encode(self.encode))
                except:
                    self.disconnect_client(other_connection)

    def handle_client(self, connection, address):
        try:
            # Kullanıcıdan gelen mesaj: "username password"
            received_data = connection.recv(1024).decode().strip().split()
            if len(received_data) < 2:#Mesajın Mikatrını Belirliyorum sadece İki Adet Gidicek Username VE Password
                connection.send("[red]Invalid login format.[/red]".encode(self.encode))
                connection.close()
                return

            username, password = received_data[0], received_data[1]#
            #received_data = list(self.team.keys()[0) # Bu Şekildede Keys Valuse Erişebilirim Ama Split İle Ayırmam Gereke Gelen Veriyi

            if username in self.clients.values():
                connection.send("[red]Nickname already taken. Please try again.[/red]".encode())
                connection.close()
                return

            # Kullanıcı doğrulama
            if username in self.team and self.team[username] == password:
                connection.send(f"[green]Login successful! Welcome {username}[/green]".encode(self.encode))
            else:
                connection.send("[red]Invalid username or password.[/red]".encode(self.encode))
                connection.close()
                return



            # Kullanıcıyı client listesine ekle
            self.clients[connection] = username #Burada Bağlantıyı Username Değişkeninde Tutuyoruz Bundan Sonra
            self.assign_color(username)# Bağlantıya Renk Veriyoruz
            join_message = f"[{self.users_color[username]}]{username} has joined the chat.[/]"
            self.log_message(join_message)
            self.broadcast(join_message, connection)

            # Konsolda bilgi göster
            panel = Panel(f"[green]{username} connected from {address[0]}:{address[1]}[/green]", border_style="white")
            self.console.print(panel)


            #Üst Taaf Genel Bağlantı
            #-----------------------------------------------------------------------------------------------------------
            # Alt Taraf İse Kullanıcı Bir İstekte bulunur İse Ona Cevap Veriyoruz İstediklerini Veriyoruz
            while True:
                message = connection.recv(4096).decode().strip()

                # Kullanıcı listesi isteği
                if message.startswith("GET_USERS"):
                    try:
                        _, requester = message.split()
                        if requester in self.clients.values():
                            user_list = self.users_info()
                            connection.send(f"TAKE_USERS {user_list.decode()}".encode())
                    except ValueError:
                        connection.send("Invalid GET_USERS format. Use: GET_USERS <username>".encode())
                    continue

                # Özel mesaj
                if message.startswith("RECEIVER_MESSAGE_NAME"):
                    try:
                        _, receiver_name, content = message.split(maxsplit=2)
                        full_message = f"[red]{username}:[/red] {content}"
                        for conn, name in self.clients.items():
                            if name == receiver_name:
                                conn.send(f"TAKE_SPECIAL_MESSAGE {full_message}".encode(self.encode))
                    except Exception as e:
                        print("Error:", e)
                    continue

                # Dosya gönderimi
                if message.startswith("UPLOAD"):
                    try:
                        _, receiver_name, file_name, content = message.split(maxsplit=3)
                        for conn, name in self.clients.items():
                            if name == receiver_name:
                                conn.send(f"TAKE_UPLOADED_DATA {file_name} {content}".encode(self.encode))
                                break
                    except Exception as e:
                        print("[red]UPLOAD parsing error:[/red]", e)
                    continue

                # Çıkış
                if message.lower() in ["exit", "q"]:
                    leave_message = f"[{self.users_color[username]}]{username} has left the chat.[/]"
                    self.log_message(leave_message)
                    self.broadcast(f"[yellow]{leave_message}[/yellow]", connection)
                    break




                # Normal mesaj iletimi
                full_message = f"[{self.users_color[username]}]{username}[/]: {message}"
                self.log_message(full_message)
                self.broadcast(full_message, connection)





        except Exception as e:
            panel = Panel(f"[red]Error handling client {address}:[/red] {e}", style="red")
            self.console.print(panel)

        finally:
            self.disconnect_client(connection)

    def listen_for_connections(self, ip_address, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind((ip_address, port))
                sock.listen()
                panel1 = Panel("[blink][white]Server is listening for connections...[/white][/blink]", title="", subtitle="", border_style="green")
                self.console.print(panel1)

                while True:
                    connection, address = sock.accept()
                    threading.Thread(target=self.handle_client, args=(connection, address)).start()

        except Exception as e:
            print(f"[red]Server Error:[/red] {e}")

    def disconnect_client(self, connection):
        nickname = self.clients.get(connection, "Unknown User")
        if nickname:
            leave_message = f"{nickname} : Has Left The Chat!!"
            panel1 = Panel(leave_message,style="red")
            self.log_message(leave_message)#Log File Dosyasında Mesaj Gözükür
            print(f"[yellow]{self.console.print(panel1)}[/yellow]")#Sadece Canlı Logda Gösterir
            self.broadcast(f"[yellow]{leave_message}[/yellow]", connection)#Herkeze Mesajı Gönderir
            del self.clients[connection]#Kullancı Bağlantıdan Silinir
            connection.close()#Bağlantı Kapanır


def main():
    listener = Listener()
    ip = "127.0.0.1"
    port = 45123
    listener.listen_for_connections(ip, port)

if __name__ == "__main__":
    main()
