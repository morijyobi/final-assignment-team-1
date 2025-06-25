from main import main

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
