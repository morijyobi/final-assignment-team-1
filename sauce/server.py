
import socket
import threading
import pickle
from config import SERVER_HOST, SERVER_PORT

positions = [(100, 300), (600, 300)]

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def client_thread(conn, player_id):
    conn.send(pickle.dumps(positions[player_id]))
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            positions[player_id] = data
            other_id = 1 - player_id
            conn.send(pickle.dumps(positions[other_id]))
        except:
            break
    conn.close()

def main():
    local_ip = get_local_ip()
    print(f"★ 闘拳伝説サーバー 起動")
    print(f"★ 接続用IPアドレス: {local_ip}")
    print(f"★ ポート番号       : {SERVER_PORT}")
    print("★ クライアント接続待機中...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(2)

    player_id = 0
    while player_id < 2:
        conn, addr = server.accept()
        print(f"プレイヤー{player_id} が接続: {addr}")
        threading.Thread(target=client_thread, args=(conn, player_id)).start()
        player_id += 1

if __name__ == "__main__":
    main()
