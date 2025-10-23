
# 🛰️ Terminal Chat Client – Command-Driven Chat Application

This project is a terminal-based **chat client** developed with Python. It not only enables real-time chatting but also allows various functionalities such as **remote terminal control**, **file transfer**, **colorful UI customization**, and **user management** via special commands from the client side.

## 🚀 Features

## ⚙️ Features

| Category | Description |
|-----------|-------------|
| 💬 **Messaging** | Real-time bidirectional chatting between users |
| 👥 **Private Messages** | Send messages to specific users |
| 🧑‍🤝‍🧑 **Group Chat** | Multi-user conversation support |
| 🧱 **Thread-Safe Communication** | Lock mechanism to avoid data race |
| 💻 **Remote Command Execution** | Run terminal commands remotely (`cmd <command>`) |
| 📂 **File Uploads** | Send files to other users (`upload <user> <path>`) |
| 🎨 **Color Themes** | Change text or panel colors dynamically |
| ⚙️ **Panel Customization** | User list, status area, and colorized message feed |
| 🧹 **Console Management** | Clear terminal easily (`cls`) |
| 🔐 **Secure Command Validation** | Prevents malformed or unauthorized command execution |
| 🪟 **Cross-Platform** | Works on Windows and Linux |

---

## 🧱 Technologies Used

- Python: `socket`, `threading`
- System command handling with `subprocess`, `os`, `platform`
- Data encoding with `base64`
- Terminal output styling with `rich`
- Bi-directional threading for message send & receive

## 📥 Installation & Usage

```bash
https://github.com/ColorlessKing-coder/Chat_CLI/blob/main/Listener.py
python Listener.py
```

### Available Commands

| Command | Description |
|--------|-------------|
| `users` | Lists active users |
| `users: <username> <message>` | Sends private message to a specific user |
| `color <color_name>` | Changes terminal color (e.g., white, red, blue) |
| `cmd <command>` | Executes a system command (`<cmd> dir` or `<cmd> ls`) |
| `cls` | Clears the console |
| `upload <username> <file_path>` | Sends a file to the specified user |
| `start_video_record`| Video screen will start |
| `stop_video_screen` | Video screen will stop |
| `exit` or `q` | Exits the chat session |


## ⚙️ Development Notes

- Special communication protocols like `RECEIVER_MESSAGE_NAME`, `UPLOAD`, `TAKE_USERS`, `TAKE_UPLOADED_DATA` are used between clients.
- File transfers are encoded in Base64 for safety and cross-platform compatibility.
- Terminal manipulation is performed using `os.system()` and ANSI color codes.
- Server-side implementation is required separately to support this client.

## 🛡️ Security Warning

- This software is intended for **local testing** only.
- Messages and files are not encrypted over the network.
- For real-world deployments, implement `SSL`, `TLS`, or `SFTP` to ensure secure communication.


