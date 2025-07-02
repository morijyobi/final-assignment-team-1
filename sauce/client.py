import socket
import pickle
import time
import random

def main():
    HOST = input("接続先IPを入力: ")
    PORT = 51515

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        print(f"[接続成功] {HOST}:{PORT}")

        init_data = client.recv(1024)
        info = pickle.loads(init_data)
        print(f"[初期情報] {info}")
        player_id = info["player_id"]

        simulated_keys = ['w', 'a', 's', 'd', 'j', 'k']

        for i in range(10):
            # ランダムに2つのキーを押したと仮定
            pressed = random.sample(simulated_keys, 2)
            key_dict = {k: True for k in pressed}

            # 送信
            client.send(pickle.dumps(key_dict))

            # 相手のキー情報を受信
            data = client.recv(1024)
            opponent_keys = pickle.loads(data)

            print(f"[送信] {key_dict} | [受信] {opponent_keys}")
            time.sleep(1)

if __name__ == "__main__":
    main()


# テスト用
# import socket
# import pickle

# def main():
#     HOST = input("接続先サーバーのIPアドレスを入力してください: ")
#     PORT = 51515

#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
#             client.connect((HOST, PORT))
#             print(f"[接続成功] サーバー {HOST}:{PORT} に接続しました。")

#             # 初期位置データを受け取る
#             data = client.recv(1024)
#             position = pickle.loads(data)
#             print(f"[受信] サーバーからの初期位置データ: {position}")

#     except Exception as e:
#         print(f"[エラー] サーバーへの接続に失敗しました: {e}")

# if __name__ == "__main__":
#     main()
