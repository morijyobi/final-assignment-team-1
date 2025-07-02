import socket
import threading
import pickle

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 51515

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def client_thread(conn, player_id, inputs, connections):
    initial_data = {"player_id": player_id}
    conn.send(pickle.dumps(initial_data))

    other_id = 1 - player_id

    while True:
        try:
            data_raw = conn.recv(2048)
            if not data_raw:
                print(f"[切断] プレイヤー{player_id}")
                break

            # クライアントから送られたキー入力情報を保存
            inputs[player_id] = pickle.loads(data_raw)

            # 相手の入力情報を送り返す
            conn.sendall(pickle.dumps(inputs[other_id]))

        except Exception as e:
            print(f"[切断] プレイヤー{player_id} ({e.__class__.__name__})")
            break

    try:
        connections[other_id].close()
    except:
        pass

    print(f"スレッド (プレイヤー{player_id}) を終了")

def main():
    print(f"★ 闘拳伝説サーバー 起動")
    print(f"★ IP: {get_local_ip()} | ポート: {SERVER_PORT}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(2)

    while True:
        print("\n★ クライアント接続待ち...")
        connections = []
        threads = []
        inputs = [{}, {}]

        for i in range(2):
            conn, addr = server.accept()
            connections.append(conn)
            print(f"プレイヤー{i} 接続: {addr}")

        print("★ 2人揃ったのでゲームセッション開始")

        for i in range(2):
            thread = threading.Thread(target=client_thread, args=(connections[i], i, inputs, connections))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print("★ セッション終了")

if __name__ == "__main__":
    main()