import socket
import threading
from rich import print
import os
import platform
import subprocess
import base64
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt
from rich.align import Align

class Sender:
    def __init__(self) -> None:
        self.console = Console()
        self.prompt = "[bold red]<[/bold red][bold green]^[/bold green][bold red]>[/bold red] "
        self.connection = None
        self.ip_address = ""
        self.port = 0
        self.nickname = ""
        self.selected_color = "white"
       
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
                    #panel_expand_true = Panel(message, expand=False)
                    message = Prompt.ask(self.prompt)
                    #self.console.print(panel_expand_true,justify="left")
                    
                    
                    if message[0:8] == "<users>:":
                        command , receiver_name , content = message.split(maxsplit=2)#İl İki Değer Ayrılır Sonraki Deperler Tek Bir Değer Olarka Tutulur 
                        full_message = f"RECEIVER_MESSAGE_NAME {receiver_name} {content}"
                        self.connection.send(full_message.encode(self.encode)) # type: ignore #kullanarak, metni UTF-8 formatında bytes türüne dönüştürdük. Bu
                        print("Mesaj Başarıyla Gönderildis")



                    elif message.startswith("<users>"):
                        full_message = f'GET_USERS {self.nickname}'
                        self.connection.send(full_message.encode())
           
                   

                    elif message.startswith("<cmd>"):
                        command = message.split(maxsplit=1)[1]
                        shell = "cmd" if os.name == "nt" else "bash"
                        process = subprocess.Popen(shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="latin1")
                        process.stdin.write(command + "\n") # type: ignore
                        process.stdin.flush() # type: ignore
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
                        self.connection.sendall(message.encode())# Sendall İle Tüm Veri Gönderilir 
                        
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
                response = self.connection.recv(4096).decode().strip() # type: ignore
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
                    message = response
                    print()           
                    #self.console.print(message)  # Diğer mesajları direkt yazdır
                    #panel2 = Panel.fit(message, border_style="white")
                    #self.console.print(panel2)
                    
                    aligned_message = Align.center(message, vertical="top")# 1. İçeriği ortala (Align ile) # Metin veya içerik panelin (veya kutunun) üst kısmına hizalanır.
                    # 2. Panel içine koy
                    panel2 = Panel(aligned_message, border_style="white", width=20)#With 20 Yaparak Genişik Olursa Alta Kayıcak 
                    # 3. Paneli de ortala (opsiyonel ama genelde gerekmez)
                    self.console.print(panel2, justify="center")   

        except Exception as e:
            print(f"[red]Error while receiving message: {e}[/red]")
            self.connection.close() # type: ignore



    def main(self):
        self.nickname = input("Please enter a nickname: ")
        self.ip_address = "192.168.1.230"
        self.port = 10000
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
