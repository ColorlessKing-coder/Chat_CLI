import socket
import threading
from rich import print
import os
import platform
import subprocess
import base64

class Sender:
    def __init__(self) -> None:
        self.connection = None
        self.ip_address = ""
        self.port = 0
        self.nickname = ""
        self.selected_color = "white"
        self.colors_windows = {
            "black": "0",
            "blue": "1",
            "green": "2",
            "aqua": "3",
            "red": "4",
            "purple": "5",
            "yellow": "6",
            "white": "7",
            "gray": "8",
            "light_blue": "9",
            "light_green": "A",
            "light_aqua": "B",
            "light_red": "C",
            "light_purple": "D",
            "light_yellow": "E",
            "bright_white": "F"
        }
        self.colors_linux = {
            "black":    "setaf 0",
            "red":      "setaf 1",
            "green":    "setaf 2",
            "yellow":   "setaf 3",
            "blue":     "setaf 4",
            "purple":   "setaf 5",
            "light_blue": "setaf 6",
            "white":    "setaf 7"
        }
        self.encode = "utf8"
    def upload(self, path):
        try:
            if os.path.exists(path):
                print("File Exists!!")
                with open(path, "rb") as upload_file:
                    print(f"[green]File {path} found and being sent![/green]")
                    return base64.b64encode(upload_file.read()).decode("utf-8")  # Encode and convert to string
            else:
                print(f"[red]File {path} not found![/red]")
                return None
        except Exception as e:
            print(f"[red]Error while reading the file: {e}[/red]")
            return None

    def connect_to_server(self):
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self.ip_address, self.port))
            print(f"[green]Connected to server {self.ip_address}:{self.port}[/green]")
            self.connection.send(self.nickname.encode())
        except Exception as e:
            print(f"[red]Connection Error:[/red] {e}")

#Serverdan Bilgi alırken İstemci Tarafından Mesajı send_message İle Gönderip
# Serverdan Gelen Bilgiyide Recevie_message İle İşlemelisin 
    def send_message(self):
        if self.connection:
            try:
                while True:
                    print("[red]<[/red]([green]**[/green])[red]>[/red]", end=' ')
                    message = input()
                    


                    if message[0:8] == "<users>:":
                        command , receiver_name , content = message.split(maxsplit=2)#İl İki Değer Ayrılır Sonraki Deperler Tek Bir Değer Olarka Tutulur 
                        full_message = f"RECEIVER_MESSAGE_NAME {receiver_name} {content}"
                        self.connection.send(full_message.encode(self.encode)) #kullanarak, metni UTF-8 formatında bytes türüne dönüştürdük. Bu
                        print("Mesaj Başarıyla Gönderildis")

                    elif message.startswith("<users>"):
                        full_message = f'GET_USERS {self.nickname}'
                        self.connection.send(full_message.encode())
           
                    elif message.startswith("<color>"):

                        command = message.split()
                        if len(command) == 2:
                            selected_color = command[1].lower()
                            if platform.system() == "Windows":
                                if selected_color in self.colors_windows:
                                    self.selected_color = selected_color
                                    print(f'[green]{self.selected_color} is activated![/green]')
                                    os.system(f'color {self.colors_windows[self.selected_color]}')
                                else:
                                    print('[red]Unsupported color![/red]')
                            elif platform.system() == "Linux":
                                if selected_color in self.colors_linux:
                                    self.selected_color = selected_color
                                    print(f'[green]{self.selected_color} is activated![/green]')
                                    os.system(f"tput {self.colors_linux[self.selected_color]}")
                                else:
                                    print('[red]Unsupported color![/red]')
                        continue

                    elif message.startswith("<cmd>"):
                        command = message.split(maxsplit=1)[1]
                        shell = "cmd" if os.name == "nt" else "bash"
                        process = subprocess.Popen(shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="latin1")
                        process.stdin.write(command + "\n")
                        process.stdin.flush()
                        output, error = process.communicate()
                        if output:
                            print("Output:\n", output)
                        if error:
                            print("Error:\n", error)
                        process.terminate()

                    elif message.startswith("<cls>"):
                        os.system("cls" if os.name == "nt" else "clear")

                    elif message.startswith("<upload>"):
                        command, user_name, path = message.split()
                        content = self.upload(path)#Upload Edilecek Veri Kontrol Ediliyor ve encode ediliyor
                        if content:
                            file_name = os.path.basename(path)
                            upload_message = f"UPLOAD {user_name} {file_name} {content}"

                            self.connection.send(upload_message.encode())
                         

                    elif message.lower().strip() in ["exit", "q"]:
                        self.connection.send('exit'.encode())
                        break
                    else:
                        self.connection.sendall(message.encode())
            except Exception as e:
                print(f"[red]Error sending message:[/red] {e}")
            finally:
                self.connection.close()
                print("[cyan]Connection closed.[/cyan]")
        else:
            print("[red]No connection to server. Please connect first.[/red]")

    
    def receive_message(self):
        try:
            while True:
                response = self.connection.recv(4096).decode().strip()
                if response.startswith("TAKE_USERS"):
                    _, user_list = response.split(" ", 1)  # Komutu ve listeyi ayır
                    print(f"Active Users:\n{user_list}")
               
                
                elif response.startswith("TAKE_SPECIAL_MESSAGE"):
                    _,special_message = response.split(" ",1)
                    print(special_message)

                elif response.startswith("TAKE_UPLOADED_DATA"):
                    try:
                        _, file_name, file_content = response.split(maxsplit=2)
                        file_content = base64.b64decode(file_content)  # Gelen içerik Base64 decode edilir
                        with open(file_name, "wb") as file_uploaded_received:
                            file_uploaded_received.write(file_content)
                    except Exception as e:
                        print("Error:", e)





                else:
                    print(response)  # Diğer mesajları direkt yazdır
        except Exception as e:
            print(f"[red]Error while receiving message: {e}[/red]")
            self.connection.close()



    def main(self):
        self.nickname = input("Please enter a nickname: ")
        self.ip_address = "127.0.0.1"
        self.port = 50001
        self.connect_to_server()

        send_thread = threading.Thread(target=self.send_message)
        receive_thread = threading.Thread(target=self.receive_message)

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()



if __name__ == "__main__":
    sender = Sender()
    sender.main()
