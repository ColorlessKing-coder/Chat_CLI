import socket
import threading
from rich import print
import os
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
        self.password = ""
        self.encode = "utf-8"

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

    def start_http_server(self,file_name):
            # Python HTTP server başlat
            server_cmd = f'python -m http.server 8080 --bind 0.0.0.0 --directory "{file_name}"'
            subprocess.Popen(["powershell", "-Command", server_cmd])
            print("[green]HTTP Server Started![/green]")

    def start_http_server_linux(self, file_name):
        server_cmd = ["python3", "-m", "http.server", "8080", "--bind", "0.0.0.0", "--directory", file_name]
        subprocess.Popen(server_cmd)
        print("[green]Linux HTTP server started![/green]")




    def start_ffmpeg(self,file_name):
             #FFmpeg başlat (video klasörüne stream.m3u8 kaydediyor)
             #ffmpeg çalışması için env olarak windowsta eklenmesi gerekir
             ffmpeg_cmd = f'ffmpeg -f gdigrab -framerate 30 -i desktop -c:v libx264 -preset ultrafast -crf 28 -f hls -hls_time 2 -hls_list_size 5 -hls_flags delete_segments "{os.path.join(file_name, "stream.m3u8")}"'
             subprocess.Popen(["powershell", "-Command", ffmpeg_cmd])
             print("Kayıt Başladı")

    def start_ffmpeg_linux(self, file_name):
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "x11grab", "-framerate", "30", "-i", ":0.0",  # ekran
            "-f", "pulse", "-i", "default",  # ses (mikrofon veya sistem)
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-c:a", "aac",
            "-f", "hls",
            "-hls_time", "2",
            "-hls_list_size", "5",
            "-hls_flags", "delete_segments",
            os.path.join(file_name, "stream.m3u8")
        ]
        subprocess.Popen(ffmpeg_cmd)
        print("[green]Linux FFmpeg recording started![/green]")

    def connect_to_server(self):
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((self.ip_address, self.port))
                print(f"[green]Connected to server {self.ip_address}:{self.port}[/green]")
                full_message = f"{self.nickname} {self.password}"
                self.connection.send(full_message.encode())
            except Exception as e:
                print(f"[red]Connection Error:[/red] {e}")

    # Serverdan Bilgi alırken İstemci Tarafından Mesajı send_message İle Gönderip
    # Serverdan Gelen Bilgiyide Recevie_message İle İşlemelisin
    def send_message(self):
        if self.connection:
            try:
                while True:
                    # panel_expand_true = Panel(message, expand=False)
                    message = Prompt.ask(self.prompt)
                    # self.console.print(panel_expand_true,justify="left")

                    if message[0:8] == "users:":
                        command, receiver_name, content = message.split(
                            maxsplit=2)  # İl İki Değer Ayrılır Sonraki Deperler Tek Bir Değer Olarka Tutulur
                        full_message = f"RECEIVER_MESSAGE_NAME {receiver_name} {content}"
                        self.connection.send(full_message.encode(
                            self.encode))  # type: ignore #kullanarak, metni UTF-8 formatında bytes türüne dönüştürdük. Bu
                        print("Mesaj Başarıyla Gönderildis")
                    elif message.startswith("users"):
                        full_message = f'GET_USERS {self.nickname}'
                        self.connection.send(full_message.encode())



                    elif message.startswith("cmd"):
                        try:
                            command = message.split(maxsplit=1)[1]  # cmd <komut>
                            # Windows ise cmd, değilse bash
                            shell = "cmd" if os.name == "nt" else "bash"
                            # Komutu subprocess ile çalıştır, sadece kendi local makinede

                            process = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True,encoding="latin1")
                            output, error = process.communicate()  # Komut tamamlanana kadar bekle
                            if output:
                                print(f"[green]Output:[/green]\n{output}")
                            if error:
                                print(f"[red]Error:[/red]\n{error}")
                        except Exception as e:
                            print(f"[red]Command execution error:[/red] {e}")


                    elif message.startswith("start_video_screen"):
                        if os.name == "nt":
                            try:
                                file_name = "video"

                                # Klasör yoksa oluştur
                                if not os.path.exists(file_name):
                                    os.makedirs(file_name)

                                # index.html yaz
                                with open(os.path.join(file_name, "index.html"), "w", encoding="utf-8") as video_file:
                                    video_file.write("""
                                    <!DOCTYPE html>
                                    <html>
                                    <head>
                                      <meta charset="UTF-8">
                                      <title>Canlı Ekran Yayını</title>
                                    </head>
                                    <body>
                                      <video id="video" controls autoplay width="800"></video>
                                      <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
                                      <script>
                                      if (Hls.isSupported()) {
                                        const video = document.getElementById('video');
                                        const hls = new Hls();
                                        // Aynı origin/host/port üzerinden otomatik çözülsün:
                                        hls.loadSource('stream.m3u8');
                                        hls.attachMedia(video);
                                        hls.on(Hls.Events.MANIFEST_PARSED, function () { video.play(); });
                                      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                                        video.src = 'stream.m3u8'; // native HLS (Safari vs.)
                                        video.addEventListener('loadedmetadata', function () { video.play(); });
                                      }
                                    </script>
                                    </body>
                                    </html>
                                    """)
                                    threading.Thread(target=self.start_http_server, args=(file_name,),daemon=True).start()
                                    self.connection.sendall(f"Record_Url http://{self.ip_address}:8080/{file_name}/index.html".encode())
                                    threading.Thread(target=self.start_ffmpeg,args=(file_name,),daemon=True).start()
                                    print("[green]FFMPEG Was Started:[/green]")
                            except Exception as e:
                                print("Erorr : ", e)

                        elif os.name == "posix":  # Linux, macOS
                            try:
                                file_name = "video"
                                if not os.path.exists(file_name):
                                    os.makedirs(file_name)

                                with open(os.path.join(file_name, "index.html"), "w", encoding="utf-8") as video_file:
                                    video_file.write("""
                                    <!DOCTYPE html>
                                    <html>
                                    <head>
                                      <meta charset="UTF-8">
                                      <title>Canlı Ekran Yayını</title>
                                    </head>
                                    <body>
                                      <video id="video" controls autoplay width="800"></video>
                                      <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
                                      <script>
                                      if (Hls.isSupported()) {
                                        const video = document.getElementById('video');
                                        const hls = new Hls();
                                        hls.loadSource('stream.m3u8');
                                        hls.attachMedia(video);
                                        hls.on(Hls.Events.MANIFEST_PARSED, function () { video.play(); });
                                      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                                        video.src = 'stream.m3u8';
                                        video.addEventListener('loadedmetadata', function () { video.play(); });
                                      }
                                      </script>
                                    </body>
                                    </html>
                                    """)

                                # Linux için HTTP server ve ffmpeg başlat
                                threading.Thread(target=self.start_http_server_linux, args=(file_name,),daemon=True).start()
                                self.connection.sendall(f"Record_Url http://{self.ip_address}:8080/{file_name}/index.html".encode())
                                threading.Thread(target=self.start_ffmpeg_linux, args=(file_name,), daemon=True).start()
                                print("[green]Linux FFmpeg was started![/green]")
                            except Exception as e:
                                print("Error:", e)






                    elif message.startswith("stop_video_screen"):
                        if os.name == "nt":
                            #shell Truda # tek string, pipe shell tarafından yorumlanır
                            nstat = subprocess.run(
                                "netstat -ano | findstr 8080",  # tek string, pipe shell tarafından yorumlanır
                                shell=True,
                                capture_output=True,
                                text=True
                            )

                            print(nstat.stdout)
                            print("returncode:", nstat.returncode)
                            """
                            #value = [] 
                            #for x in nstat.stdout.split(): split zaten array olarak dönüştğryor nu sebeple append yapmaya gerek yok ama yinede buda çalışır 
                            #    value.append(x)

                            #if "LISTENING" in value:
                             """

                            for line in nstat.stdout.splitlines():
                                if "LISTENING" in line:
                                    try:
                                        pid = line.split()[-1]
                                        tkill =     subprocess.run(f"taskkill /F /PID {pid}", shell=True,capture_output=True,text=True)
                                        print(tkill.stdout)
                                    except Exception as e:
                                        print("Error : " ,e )
                        if os.name == "nt":
                            ffmep = subprocess.run(
                                "tasklist | findstr ffmpeg ",  # tek string, pipe shell tarafından yorumlanır
                                shell=True,
                                capture_output=True,
                                text=True
                            )
                            print(ffmep.stdout)
                            print("returncode:", ffmep.returncode)

                            for line in ffmep.stdout.splitlines():
                                try:
                                    pid = line.split()[-1]
                                    tkill = subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True,text=True)
                                    print(tkill.stdout)
                                except Exception as e:
                                    print("Error : ", e)

                            #frfmepg çıktısını yaxdırmaya gerek yok sıkıntı sürekli işeniyor
                            #kapatma konusuna gelince daha bakılması gerek kapanmıyor


                        if os.name == "posix":  # Linux, macOS
                            try:
                                # 1) HTTP server'ı kapat (8080 portunu kullanan processleri bul ve öldür)
                                nstat = subprocess.run(
                                    "lsof -t -i:8080",  # sadece PID'leri döndürür
                                    shell=True,
                                    capture_output=True,
                                    text=True
                                )
                                print(nstat.stdout)
                                if nstat.stdout.strip():
                                    for pid in nstat.stdout.splitlines():
                                        try:
                                            tkill = subprocess.run(f"kill -9 {pid}", shell=True,
                                                                   capture_output=True, text=True)
                                            print(tkill.stdout)
                                        except Exception as e:
                                            print("Error killing http.server:", e)
                            except Exception as e:
                                print("Error:", e)
                        if os.name == "posix":
                                try:
                                    # 2) FFmpeg işlemini kapat
                                    ffmpeg_proc = subprocess.run(
                                        "pgrep ffmpeg",  # ffmpeg çalışan PID'leri döndürür
                                        shell=True,
                                        capture_output=True,
                                        text=True
                                    )
                                    print(ffmpeg_proc.stdout)
                                    if ffmpeg_proc.stdout.strip():
                                        for pid in ffmpeg_proc.stdout.splitlines():
                                            try:
                                                tkill = subprocess.run(f"kill -9 {pid}", shell=True,
                                                                       capture_output=True, text=True)
                                                print(tkill.stdout)
                                            except Exception as e:
                                                print("Error killing ffmpeg:", e)

                                    print("[red]Linux video screen stopped![/red]")
                                except Exception as e:
                                    print("Error:", e)










                    elif message.startswith("cls"):
                        os.system("cls" if os.name == "nt" else "clear")
                    elif message.startswith("upload"):
                        command, user_name, path = message.split()
                        content = self.upload(path)  # Upload Edilecek Veri Kontrol Ediliyor ve encode ediliyor
                        if content:
                            file_name = os.path.basename(path)
                            upload_message = f"UPLOAD {user_name} {file_name} {content}"

                            self.connection.send(upload_message.encode())
                    elif message.lower().strip() in ["exit", "q"]:
                        self.connection.send('exit'.encode())
                        break

                    else:
                        self.connection.sendall(message.encode())  # Sendall İle Tüm Veri Gönderilir

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
                try:
                    response = self.connection.recv(4096)
                    if not response:
                        print("Server disconnected.")
                        break
                    response = response.decode(errors="ignore").strip()
                except ConnectionResetError:
                    print("Connection reset by server.")
                    break

                if response.startswith("TAKE_USERS"):
                    _, user_list = response.split(" ", 1)  # Komutu ve listeyi ayır
                    print(f"Active Users:\n{user_list}")


                elif response.startswith("TAKE_SPECIAL_MESSAGE"):
                    _, special_message = response.split(" ", 1)
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
                    # self.console.print(message)  # Diğer mesajları direkt yazdır
                    # panel2 = Panel.fit(message, border_style="white")
                    # self.console.print(panel2)

                    aligned_message = Align.center(message,vertical="top")  # 1. İçeriği ortala (Align ile) # Metin veya içerik panelin (veya kutunun) üst kısmına hizalanır.
                    panel2 = Panel(aligned_message, border_style="white",width=20)  # With 20 Yaparak Genişik Olursa Alta Kayıcak
                    self.console.print(panel2, justify="center")

        except Exception as e:
            print(f"[red]Error while receiving message: {e}[/red]")
            self.connection.close()  # type: ignore







    def main(self):
        self.nickname = input("Please enter a nickname: ")
        self.password = input("Please enter a password: ")
        self.ip_address = "127.0.0.1"
        self.port = 45123
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
