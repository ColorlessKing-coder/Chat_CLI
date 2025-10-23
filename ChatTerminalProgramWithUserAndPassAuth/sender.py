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
from rich.columns import Columns




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
        self.active_sessions = []
        self.active_users = []
        self.receiving_file = True
        self.file_obj = None
        self.true_message = []
        self.false_message = []
        self.rich_prompt = Prompt()
        self.general_panel_color = "light_sky_blue1"
        self.special_message_panel_color = "medium_purple3"
        self.colors = [
            "red", "green", "yellow",
            "blue", "magenta", "cyan", "white", "bright_red", "bright_green", "bright_yellow", "bright_blue",
            "bright_magenta",
            "bright_cyan", "orange1", "orange3", "dark_orange", "orange_red1", "gold1", "gold3", "gold4",
            "deep_pink1", "deep_pink2", "deep_pink3", "hot_pink", "hot_pink2", "hot_pink3",
            "violet", "violet_red", "medium_purple", "medium_purple2", "blue_violet",
            "dodger_blue1", "dodger_blue2", "dodger_blue3", "sky_blue1", "sky_blue2", "sky_blue3",
            "spring_green1", "spring_green2", "spring_green3", "sea_green1", "sea_green2", "sea_green3",
            "turquoise2", "turquoise4", "dark_turquoise", "medium_turquoise",
            "chartreuse1", "chartreuse2", "chartreuse3", "chartreuse4",
            "aquamarine1", "aquamarine2", "aquamarine3", "pale_green1", "pale_green3",
            "khaki1", "khaki3", "khaki4", "light_goldenrod1", "light_goldenrod3",
            "salmon1", "indian_red", "orchid", "plum1", "plum3",
            "slate_blue1", "slate_blue3", "steel_blue1", "steel_blue3"
        ]



    def start_http_server(self,file_name):
            # Python HTTP server başlat
            server_cmd = f'python -m http.server 8080 --bind 0.0.0.0 --directory "{file_name}"'
            subprocess.Popen(["powershell", "-Command", server_cmd])
            print("[green]HTTP Server Started![/green]")

    def start_http_server_linux(self, file_name):
        server_cmd = ["python3", "-m", "http.server", "8080", "--bind", "0.0.0.0", "--directory", file_name]
        subprocess.Popen(server_cmd)
        print("[green]Linux HTTP server started![/green]")

    def show_help(self):
        """Rich ile güzel görünümlü help paneli gösterir."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Command", style="bold cyan", no_wrap=True)
        table.add_column("Description", style="white")

        commands = [
            ("help", "For Help Menu."),
            ("exit / q", "Exit The Application."),
            ("cls", "Clear The Console (Windows: cls, Unix: clear)."),
            ("list_panel_colors", "That Command Will Show You All Supported Colors For Change To Panel's Colors. "),
            ("panel_color <color>", "That Command Changed The Special Message Panel Color"),
            ("users", "The Command Take Active Users From The Server ."),
            ("users: <receiver> <message>", "Message To USer: Example; users: Ahmet Merhaba"),
            ("select <k1> <k2> ...", "Bir veya birden fazla kullanıcıyla özel/çoklu oturum başlatma talebi gönderir."),
            ("exit <users>", "Sunucuya özel oturumdan çıkış bildirir (istemci exit ile de tetiklenir)."),
            ("cmd <komut>", "Yerel makinede komut çalıştırır (Windows: cmd, Unix: bash)."),
            ("start_video_screen","Start a Video Recorder With HTTP Protocols"),
            ("stop_video_screen", "That Command Will Stop Video Screen"),
            ("upload <file_path> <file_name>", "How To Upload File to General Chat")

        ]

        for cmd, desc in commands:
            table.add_row(cmd, desc)

        footer = Text.assemble(("Not: ", "bold yellow"),
        ("The execution of commands depends on the server’s protocol. Pay attention to the special message", "white"))
        panel = Panel.fit(Align.center(table),title="[bold green]Commands — Help[/bold green]",border_style="bright_blue",padding=(1, 2))

        # Konsola yazdır
        self.console.print(panel)
        self.console.print(Panel(footer, border_style="yellow", padding=(0, 1)))

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
                    message = Prompt.ask(self.prompt)
                    if self.active_sessions:
                        if message.lower() in ["return", "chat"] and self.active_sessions:
                            #print(f"[yellow]Exiting private session with {', '.join(self.active_sessions)}[/yellow]")
                            #Gerek Yok Artık Sağ Tarafta Genel Mesajda Gözüküceke
                            for target in self.active_sessions:
                                self.connection.send(f"EXIT_SESSION {target}".encode(self.encode))
                            self.active_sessions = []  # session temizlenir
                            continue
                        if message.startswith("exit") and self.active_sessions:
                            _,user_exit = message.split(" ", 1)
                            #user_exit = ''.join(c for c in user_exit if c.isprintable()).strip()
                            for c in ''.join(user_exit):
                                if c.isprintable():
                                    c.strip()
                            if user_exit in self.active_sessions:
                                self.active_sessions.remove(user_exit)
                                self.connection.send(f"REMOVE_USER {user_exit}".encode(self.encode))
                                text = f"The User Delete in Group Conversation {user_exit}"
                                panel = Panel(Text.from_markup(text, justify="center"),border_style=self.special_message_panel_color, title=f"Colors Option ",padding=(0, 2), width=30)
                                self.console.print(panel, justify="right")


                    if message.startswith("panel_color"):
                        _, panel_color = message.split(" ", 2)
                        if panel_color in self.colors:
                            text = f"The Panel Color Changed to {panel_color}"
                            panel = Panel(Text.from_markup(text, justify="center"),border_style=self.special_message_panel_color, title=f"Colors Option ",padding=(0, 2),width=30)
                            self.console.print(panel,justify="right")
                            self.special_message_panel_color = panel_color
                        else:
                            text = f" Sorry Unknow Colors {panel_color}/n See All The Color (list_panel_colors)"
                            panel = Panel(Text.from_markup(text, justify="center"),border_style=self.special_message_panel_color, title=f"Colors Option ",padding=(0, 2), width=30)
                            self.console.print(panel,justify="right")
                    if message.lower() == "list_panel_colors":
                        text = '()'.join(self.colors)
                        panel = Panel(Text.from_markup(text, justify="center"),border_style=self.special_message_panel_color, title=f"Colors Option ",padding=(0, 2), width=30)
                        self.console.print(panel,justify="right")
                    if message.startswith("select"):
                        _, *users = message.split()  # select komutundan sonraki tüm kullanıcıları alır
                        self.active_sessions = users  # doğrudan listeye ata

                        # Tek mesajda tüm kullanıcıları gönder
                        user_list_str = " ".join(users)## Ahmet Yusuf Şeklinde Göndericek
                        self.connection.send(f"SELECTED_USER {user_list_str}".encode())
                        #print(f"[green]Requesting private session with: {', '.join(self.active_sessions)}[/green]")
                        #Buna Gerek Yok Şunalık
                    if message[0:6] == "users:":
                        command, receiver_name, content = message.split(maxsplit=2)  # İl İki Değer Ayrılır Sonraki Deperler Tek Bir Değer Olarka Tutulur
                        full_message = f"RECEIVER_MESSAGE_NAME {receiver_name} {content}"
                        self.connection.send(full_message.encode(self.encode))

                        text = "The Message has been sent."
                        panel = Panel(Text(text, justify="center"), border_style=self.special_message_panel_color,title=f"Upload Alert", padding=(0, 2),width=30)
                        self.console.print(panel, justify="right")
                    if message.startswith("users"):
                        full_message = f'GET_USERS {self.nickname}'
                        self.connection.send(full_message.encode())
                    if message.startswith("cmd"):
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
                    if message.startswith("start_video_screen"):
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
                    if message.startswith("stop_video_screen"):
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
                    if message.startswith("cls"):
                        os.system("cls" if os.name == "nt" else "clear")
                    if message.startswith("help"):
                        self.show_help()
                        continue
                    if message.startswith("upload"):
                        try:
                            _, directory, file_name = message.split(" ", 2)
                            full_path = os.path.join(directory, file_name)

                            if not os.path.exists(full_path):
                                self.false_message.append("[red]The file does not exist! Please check the path.[/red]")
                                continue
                            size = os.path.getsize(full_path)
                            self.true_message.append(f"[green]The file '{file_name}' exists. Sending To Server [The File Size:{size}][/green]")
                            self.connection.send(f"U_START {directory} {file_name} {size}\n".encode(self.encode))#Dosya Bilgileri Gönderildi
                            with open(full_path,"rb") as f:  # Dosya Açıldı Okunan Veriler Kontrollu Şekilde Gönderilicek
                                while True:
                                    chunk = f.read(4096)
                                    if not chunk:
                                        break
                                    self.connection.sendall(chunk)

                            #Mesaj Sağda Gözüksün Diye
                            self.true_message.append(f"[bold green]File '{file_name}' successfully to Send Server [/bold green]")
                            edited_text = Text.from_markup(" ".join(self.true_message), justify="center")  # Metini Editlemek İçin
                            message = Align.center(edited_text, vertical="top")  # Konsola Hizalamak İçin
                            panel_conf = Panel(message, border_style="orange1", title="File Uploading ...",width=30)  # Paneli Editlemek İçin
                            self.console.print(panel_conf, justify="right")
                            self.true_message.clear()

                        except Exception as e:
                            self.false_message.append(f"[red]Upload error:[/red] {e}")
                            edited_text = Text.from_markup(" ".join(self.false_message), justify="center")  # Metini Editlemek İçin
                            message = Align.center(edited_text, vertical="top")  # Konsola Hizalamak İçin
                            panel_conf = Panel(message, border_style="orange1", title="File Uploading Failed",width=30)  # Paneli Editlemek İçin
                            self.console.print(panel_conf, justify="right")
                            self.false_message.clear()
                    if message.lower().strip() in ["exit", "q"]:
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
                        response = self.connection.recv(4096).decode(errors="ignore").strip()
                        if not response:
                            print("Server disconnected.")
                            break
                    except ConnectionResetError:
                        print("Connection reset by server.")
                        break
                        #Çok Önemli Not Severddan Gelen Mesaj TAKE_USERS ile başladığından aynı anda active users panelide geliyor
                        # İlk Once Kişiye Bağlantı İsteği Gönderildi Server Bağlantı Gönderdi Şimdi İşleyip Kullanıcıya Mesaj Atıcam Taki Exit Diyene Kadar
                    if response.startswith("TAKE_USERS_SESSION"):
                        _, user_connections = response.split(" ", 1)# 'user_connections' örnek: ["Yasir/Talha/Reyyan"]
                        self.active_sessions = [user.strip() for user in user_connections.split("/")]
                        #["Yasir","Reyyan","Talha"]
                        #print(f"[green]Active session started with: {', '.join(self.active_sessions)}[/green]")
                        #İstemcide Active User Geçtikten Sonra İsim Benzerliğinden Dolayı Active Users Geliyor Zaten O Sebeple Yukarıdakini Yazmaya Gerek Yok Ama Yazmak Gerekse Bilde Panel İle Sağ Tarafta Yazdırmayı Unutma


                    if response.startswith("TAKE_USERS"):
                        _, user_list = response.split(" ", 1)
                        user_list = ''.join(c for c in user_list if c.isprintable()).strip()  # bazen strip bile göremeyebilir
                        panel = Panel(Text(user_list, justify="center"),border_style=self.special_message_panel_color,title=f"The Active Users",padding=(0, 2),width=30)
                        print()#Boşluk Olması Gerek Çünkü Panel Kayıyor
                        self.console.print(panel,justify="right")
                        continue


                    if response.startswith("TAKE_SPECIAL_MESSAGE"):
                        _, special_message = response.split(" ", 1)
                        message = special_message.strip()
                        print()#Boşluk Olması Gerek Çünkü Panel Kayıyor
                        panel = Panel(Text.from_markup(message, justify="center"), border_style=self.special_message_panel_color,title=f"Upload Alert", padding=(0, 2),width=30)  ##Buradaki padding panelde hafif sol taraftaki boşlu kapatmıyor ama ortalıyor
                        self.console.print(panel, justify="right")
                        continue


                    if response.startswith("UPLOAD_MESSAGE"):#Sade Kullanıcıya Gelen Mesaj Ekran Basılıyor
                        _, question = response.split(maxsplit=1)#Yukarıda Zaten Decode Edildi
                        #print(f"DEBUG FULL RESPONSE: {repr(question)}")  # repr ile mesajın tam olarak nasıl geldiği açık olarak gösterilir
                        message = ''.join(c for c in question if c.isprintable()).strip()
                        panel = Panel(Text(message, justify="center"),border_style=self.special_message_panel_color,title=f"Upload Alert",padding=(0, 2),width=30)  ##Buradaki padding panelde hafif sol taraftaki boşlu kapatmıyor ama ortalıyor
                        self.console.print(panel, justify="right")


                        answer = input("Please Answer The Question : ( Yes/Or Anything ) " )
                        if answer.lower() == "yes":#Kullanıcı Yes Dediyse Server Yes Olanlara Tekrar Mesaj İleticek
                            self.connection.send(answer.encode())#
                        else:
                            text = f"[red]You Don't Take The Upload![/red]"

                            panel = Panel(Text(text, justify="center"),border_style=self.special_message_panel_color,title=f"Upload Warning",padding=(0, 2),width=30)
                            self.console.print(panel, justify="right")
                        continue


                    if response.startswith("UPLOAD_FILE"):
                        _, file_name = response.split(" ", 1)
                        self.file_obj = open(file_name, "wb")
                        # Sunucuya "hazırım" sinyali gönder
                        self.connection.send(b"ready")# Burda Bana Verileri Gönder Diyorum
                        while True:
                            chunk = self.connection.recv(4096)
                            if b"END" in chunk:
                                chunk = chunk.replace(b"END", b"")
                                self.file_obj.write(chunk)
                                self.file_obj.close()
                                self.receiving_file = False
                                self.file_obj = None
                                break

                            self.file_obj.write(chunk)


                    else:
                        message = response
                        print()

                        aligned_message = Align.center(message, vertical="top")
                        text = Panel(aligned_message, border_style=self.general_panel_color,width=20)  # With 20 Yaparak Genişik Olursa Alta Kayıcak
                        self.console.print(text, justify="center")

        except Exception as e:
            print(f"[red]Error while receiving message: {e}[/red]")
            self.connection.close()  # type: ignore

    def main(self):
        self.nickname = input("Please enter a nickname: ")
        self.password = input("Please enter a password: ")
        self.ip_address = "127.0.0.1"
        self.port = 10600
        self.connect_to_server()

        receive_thread = threading.Thread(target=self.receive_message, daemon=True)
        receive_thread.start()

        send_thread = threading.Thread(target=self.send_message)
        send_thread.start()

        send_thread.join()  # kullanıcı çıkana kadar bekler


if __name__ == "__main__":
    sender = Sender()
    sender.main()
