# config.py
# ゲームとサーバーで共通の設定ファイル

# 画面サイズ
WIDTH, HEIGHT = 800, 400
FPS = 30

# 地面のY座標（プレイヤーが立つ場所）
GROUND_Y = HEIGHT - 30

# 相対座標変換（画面中央＆地面を原点に）
def to_relative(x, y):
    return x - WIDTH // 2, y - GROUND_Y

def to_absolute(rx, ry):
    return rx + WIDTH // 2, ry + GROUND_Y
