import pygame
import sys
import random
import socket
import pickle
import os
from config import WIDTH, HEIGHT, FPS

# --- 初期化と定数 ---
script_dir = os.path.dirname(__file__)
img_dir = os.path.join(script_dir, '..', 'img')

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("闘拳伝説")
clock = pygame.time.Clock()

WHITE, RED, BLUE, GREEN, GRAY, BLACK = (255,255,255), (255,0,0), (0,0,255), (0,180,0), (150,150,150), (0,0,0)
HADOUKEN_COLOR, KAMEHAMEHA_COLOR = (0,100,255), (0,200,255)

try:
    FONT_S = pygame.font.SysFont("meiryo", 28)
    FONT_M = pygame.font.SysFont("meiryo", 40)
    FONT_L = pygame.font.SysFont("meiryo", 64)
except:
    FONT_S = pygame.font.SysFont(None, 32)
    FONT_M = pygame.font.SysFont(None, 48)
    FONT_L = pygame.font.SysFont(None, 72)

characters = [{"name": "青龍", "color": BLUE}, {"name": "赤虎", "color": RED}, {"name": "緑風", "color": GREEN}]
try:
    backgrounds = [{"name": name, "image": pygame.transform.scale(pygame.image.load(os.path.join(img_dir, f_name)), (WIDTH, HEIGHT))}
                   for name, f_name in [("道場", "dojo.png"), ("古代寺", "temple.png"), ("森", "forest.png")]]
except Exception as e:
    print(f"背景画像エラー: {e}"); backgrounds = []

# --- ネットワーククラス ---
class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = ""
        self.port = 51515
        self.player_id = -1

    def connect(self, host):
        self.host = host
        try:
            self.client.connect((self.host, self.port))
            initial_info = pickle.loads(self.client.recv(4096))
            self.player_id = initial_info["player_id"]
            print(f"[接続成功] サーバー: {self.host}:{self.port}, あなたはプレイヤー{self.player_id}です。")
            return True
        except Exception as e:
            print(f"[接続エラー] {e}"); return False

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            reply = pickle.loads(self.client.recv(4096))
            return reply
        except socket.error: return None
            
    def close(self):
        self.client.close()

# --- 描画関数 ---
def draw_text(text, font, color, surface, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x,y)
    surface.blit(textobj, textrect)

def draw_title_screen(screen, selected_mode):
    screen.fill(BLACK)
    draw_text("闘拳伝説", FONT_L, WHITE, screen, WIDTH // 2, HEIGHT // 4)
    cpu_color = WHITE if selected_mode == "cpu" else GRAY
    online_color = WHITE if selected_mode == "online" else GRAY
    draw_text("CPU対戦", FONT_M, cpu_color, screen, WIDTH // 2, HEIGHT // 2)
    draw_text("オンライン対戦", FONT_M, online_color, screen, WIDTH // 2, HEIGHT // 2 + 60)
    draw_text("↑↓キーで選択, Enterで決定", FONT_S, WHITE, screen, WIDTH // 2, HEIGHT - 50)

def draw_ip_input_screen(screen, ip_address, message=""):
    screen.fill(BLACK)
    draw_text("サーバーのIPアドレスを入力", FONT_M, WHITE, screen, WIDTH // 2, 100)
    input_box = pygame.Rect(WIDTH // 2 - 150, 200, 300, 50)
    pygame.draw.rect(screen, WHITE, input_box, 2)
    draw_text(ip_address, FONT_M, WHITE, screen, WIDTH // 2, 225)
    draw_text("Enterキーで接続", FONT_S, WHITE, screen, WIDTH // 2, 300)
    if message:
        draw_text(message, FONT_S, RED, screen, WIDTH // 2, 350)

def draw_waiting_screen(screen, message):
    screen.fill(BLACK)
    draw_text(message, FONT_M, WHITE, screen, WIDTH // 2, HEIGHT // 2)

def draw_character_select(screen, my_index, opponent_index, my_ready):
    screen.fill(BLACK)
    title = "キャラを選んでください" if not my_ready else "相手の選択を待っています..."
    draw_text(title, FONT_M, WHITE, screen, WIDTH // 2, 50)
    for i, char in enumerate(characters):
        if i == my_index:
            pygame.draw.rect(screen, WHITE, (150 + i * 200 - 4, 146, 108, 108), 4)
        if i == opponent_index:
            pygame.draw.rect(screen, RED, (150 + i * 200 - 4, 146, 108, 108), 2)
        
        rect = pygame.Rect(150 + i * 200, 150, 100, 100)
        pygame.draw.rect(screen, char["color"], rect)
        draw_text(char["name"], FONT_S, WHITE, screen, rect.centerx, rect.bottom + 20)

def draw_stage_select(screen, selected_index, can_select):
    screen.fill(BLACK)
    title = "ステージを選んでください" if can_select else "P1がステージを選択中..."
    draw_text(title, FONT_M, WHITE, screen, WIDTH // 2, 50)
    for i, bg in enumerate(backgrounds):
        rect = pygame.Rect(150 + i * 200, 150, 100, 100)
        if bg.get("image"):
            screen.blit(pygame.transform.scale(bg["image"], (100,100)), rect.topleft)
        pygame.draw.rect(screen, WHITE, rect, 4 if i == selected_index else 1)
        draw_text(bg["name"], FONT_S, WHITE, screen, rect.centerx, rect.bottom + 20)

def draw_result_screen(screen, winner_text):
    screen.fill(BLACK)
    draw_text(winner_text, FONT_L, WHITE, screen, WIDTH // 2, HEIGHT // 3)
    draw_text("Rキー: リトライ / Tキー: タイトルへ", FONT_S, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 50)

def draw_hp_bar(s, x, y, hp):
    pygame.draw.rect(s, RED, (x, y, 200, 20))
    pygame.draw.rect(s, GREEN, (x, y, max(0, 2 * hp), 20))

# --- ゲームクラス ---
class Hadouken:
    WIDTH, HEIGHT, SPEED = 30, 15, 12
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.direction = direction
        self.active = True
    def update(self):
        self.rect.x += self.SPEED if self.direction == 'right' else -self.SPEED
        self.active = not(self.rect.right < 0 or self.rect.left > WIDTH)
    def draw(self, screen):
        pygame.draw.ellipse(screen, HADOUKEN_COLOR, self.rect)

class Kamehameha:
    WIDTH, HEIGHT, SPEED, DAMAGE = 60, 25, 8, 8
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.direction = direction
        self.active = True
    def update(self):
        self.rect.x += self.SPEED if self.direction == 'right' else -self.SPEED
        self.active = not(self.rect.right < 0 or self.rect.left > WIDTH)
    def draw(self, screen):
        pygame.draw.rect(screen, KAMEHAMEHA_COLOR, self.rect)

class Player:
    WIDTH, HEIGHT, SPEED, JUMP_POWER, GRAVITY = 40, 80, 5, 15, 1
    def __init__(self, x, y, color, is_cpu=False):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.color = color
        self.vel_y = 0
        self.on_ground = True
        self.hp = 100
        self.is_attacking = False
        self.attack_cooldown = 0
        self.is_guarding = False
        self.is_crouch = False
        self.facing_right = True
        self.is_cpu = is_cpu
        self.command_buffer = []
        self.command_timer = 0
        self.command_timeout = 30
        self.attack_type = 'weak'
        self.hadouken_list = []
        self.kamehameha_list = []
        self.attack_hit_done = True
        self.is_shoryuken = False
        self.shoryuken_timer = 0
        self.is_tatsumaki = False
        self.tatsumaki_timer = 0
        self.tatsumaki_duration = 30
        self.tatsumaki_speed = 10

    def handle_input(self, input_state, opponent=None):
        """プレイヤーの入力を処理する（修正版）"""
        if self.is_cpu:
            self.ai_behavior(opponent)
            return

        # is_dictフラグで、入力が辞書か（ネットワーク経由か）どうかを判断
        is_dict = isinstance(input_state, dict)

        # ガードとしゃがみ状態をリセット
        self.is_guarding = False
        self.is_crouch = False

        # 竜巻旋風脚の最中は他の入力を受け付けない
        if self.is_tatsumaki:
            return

        # --- 入力の種類に応じてキーの状態を取得 ---
        # is_dict が True (ネットワーク) なら 'left', False (ローカル) なら pygame.K_LEFT でチェック
        move_left = input_state.get('left', False) if is_dict else input_state[pygame.K_LEFT]
        move_right = input_state.get('right', False) if is_dict else input_state[pygame.K_RIGHT]
        jump = input_state.get('up', False) if is_dict else input_state[pygame.K_UP]
        crouch = input_state.get('down', False) if is_dict else input_state[pygame.K_DOWN]
        guard = input_state.get('d', False) if is_dict else input_state[pygame.K_d]
        weak_attack = input_state.get('a', False) if is_dict else input_state[pygame.K_a]
        strong_attack = input_state.get('s', False) if is_dict else input_state[pygame.K_s]
        ki_attack = input_state.get('k', False) if is_dict else input_state[pygame.K_k]

        # --- 取得したキー状態に基づいて処理 ---
        if move_left:
            self.rect.x -= self.SPEED
            self.facing_right = False
            self.add_command('←')
        if move_right:
            self.rect.x += self.SPEED
            self.facing_right = True
            self.add_command('→')

        if jump and self.on_ground:
            self.vel_y = -self.JUMP_POWER
            self.on_ground = False
            self.add_command('↑')
        if crouch and self.on_ground:
            self.is_crouch = True
            self.add_command('↓')

        if guard:
            self.is_guarding = True

        if weak_attack and self.attack_cooldown == 0:
            if self.check_shoryuken_command():
                self.attack_cooldown = 30; self.attack_type = 'shoryuken'; self.is_attacking = True
                self.attack_hit_done = False; self.is_shoryuken = True; self.shoryuken_timer = 15; self.command_buffer.clear()
            else:
                self.attack_cooldown = 15; self.attack_type = 'weak'; self.is_attacking = True; self.attack_hit_done = False
        
        elif strong_attack and self.attack_cooldown == 0:
            if self.check_hadouken_command():
                self.fire_hadouken(); self.attack_cooldown = 30; self.command_buffer.clear()
            elif self.check_tatsumaki_command():
                self.attack_cooldown = 40; self.attack_type = 'tatsumaki'; self.is_attacking = True
                self.attack_hit_done = False; self.is_tatsumaki = True; self.tatsumaki_timer = self.tatsumaki_duration; self.command_buffer.clear()
            else:
                self.attack_cooldown = 20; self.attack_type = 'strong'; self.is_attacking = True; self.attack_hit_done = False
        
        elif ki_attack and self.attack_cooldown == 0:
            self.fire_kamehameha(); self.attack_cooldown = 60; self.attack_type = 'kamehameha'

        if self.command_timer > 0:
            self.command_timer -= 1
        else:
            self.command_buffer.clear()


    def add_command(self, cmd):
        self.command_buffer.append(cmd)
        self.command_timer = self.command_timeout

    def check_hadouken_command(self):
        return '↓→' in ''.join(self.command_buffer)[-3:]

    def check_shoryuken_command(self):
        return '→↓→' in ''.join(self.command_buffer)[-5:]

    def check_tatsumaki_command(self):
        return '←↓→' in ''.join(self.command_buffer)[-5:]

    def fire_hadouken(self):
        h = self.HEIGHT // 2 if self.is_crouch else self.HEIGHT
        x = self.rect.right if self.facing_right else self.rect.left - Hadouken.WIDTH
        y = self.rect.bottom - h + h // 2 - Hadouken.HEIGHT // 2
        direction = 'right' if self.facing_right else 'left'
        self.hadouken_list.append(Hadouken(x, y, direction))

    def fire_kamehameha(self):
        h = self.HEIGHT // 2 if self.is_crouch else self.HEIGHT
        x = self.rect.right if self.facing_right else self.rect.left - Kamehameha.WIDTH
        y = self.rect.bottom - h + h // 2 - Kamehameha.HEIGHT // 2
        direction = 'right' if self.facing_right else 'left'
        self.kamehameha_list.append(Kamehameha(x, y, direction))

    def ai_behavior(self, opponent):
        if opponent.rect.centerx > self.rect.centerx + 50:
            self.rect.x += self.SPEED // 2; self.facing_right = True
        elif opponent.rect.centerx < self.rect.centerx - 50:
            self.rect.x -= self.SPEED // 2; self.facing_right = False
        else:
            action = random.randint(0, 100)
            if action < 10 and self.attack_cooldown == 0:
                self.attack_cooldown = 15; self.attack_type = 'weak'; self.is_attacking = True; self.attack_hit_done = False
            elif action < 20:
                self.is_guarding = True
            elif action < 25 and self.attack_cooldown == 0:
                self.fire_hadouken(); self.attack_cooldown = 30

    def update(self):
        self.vel_y += self.GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom >= HEIGHT - 30:
            self.rect.bottom = HEIGHT - 30; self.vel_y = 0; self.on_ground = True
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        else:
            self.is_attacking = False; self.is_shoryuken = False; self.is_tatsumaki = False
        if self.is_shoryuken:
            self.shoryuken_timer -= 1
            if self.shoryuken_timer > 7:
                self.vel_y = -self.JUMP_POWER // 2
        if self.is_tatsumaki:
            self.tatsumaki_timer -= 1
            self.rect.x += self.tatsumaki_speed if self.facing_right else -self.tatsumaki_speed
            self.rect.y += -2 if self.tatsumaki_timer % 10 < 5 else 2
            self.is_tatsumaki = self.tatsumaki_timer > 0
        for p in self.hadouken_list + self.kamehameha_list:
            p.update()
        self.hadouken_list = [p for p in self.hadouken_list if p.active]
        self.kamehameha_list = [p for p in self.kamehameha_list if p.active]

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY if self.is_guarding else self.color, self.rect)
        for p in self.hadouken_list: p.draw(screen)
        for p in self.kamehameha_list: p.draw(screen)

def check_attack(attacker, defender):
    if attacker.is_attacking and not attacker.attack_hit_done:
        attack_rect = attacker.rect.copy()
        if attacker.attack_type == 'weak':
            attack_rect.width += 20
            if not attacker.facing_right: attack_rect.x -= 20
        elif attacker.attack_type == 'strong':
            attack_rect.width += 30
            if not attacker.facing_right: attack_rect.x -= 30
        elif attacker.attack_type == 'shoryuken':
            attack_rect.y -= 20; attack_rect.height += 40
        
        if attack_rect.colliderect(defender.rect):
            attacker.attack_hit_done = True
            if not defender.is_guarding: defender.hp -= 10

def check_projectile_hit(attacker, defender):
    for p in attacker.hadouken_list:
        if p.rect.colliderect(defender.rect):
            p.active = False
            if not defender.is_guarding: defender.hp -= 8
    for p in attacker.kamehameha_list:
        if p.rect.colliderect(defender.rect):
            p.active = False
            if not defender.is_guarding: defender.hp -= p.DAMAGE

# --- メイン関数 ---
def main():
    game_state = "title"
    game_mode = "cpu"
    selected_mode = "cpu"
    network = None
    ip_address = ""
    ip_input_message = ""
    my_char_index, my_stage_index, my_char_ready = 0, 0, False
    player1, player2, selected_background, game_over, winner_text = None, None, None, False, ""
    
    running = True
    while running:
        opponent_data = {}
        # 1. 通信 (オンラインモードかつ、選択画面以降)
        if game_mode == "online" and network and game_state not in ["title", "ip_input", "waiting_connect"]:
            my_data = {"char_index": my_char_index, "stage_index": my_stage_index, "ready": my_char_ready, "keys": {}}
            if game_state == "in_game" and not game_over:
                keys = pygame.key.get_pressed()
                my_data["keys"] = {'left':keys[pygame.K_LEFT],'right':keys[pygame.K_RIGHT],'up':keys[pygame.K_UP],'down':keys[pygame.K_DOWN],'a':keys[pygame.K_a],'s':keys[pygame.K_s],'d':keys[pygame.K_d],'k':keys[pygame.K_k]}
            
            opponent_data = network.send(my_data)
            if opponent_data is None:
                print("相手の接続が切れました。タイトルに戻ります。")
                game_state = "title"; network.close(); network = None; continue

        # 2. イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if game_state == "title":
                    if event.key in (pygame.K_UP, pygame.K_DOWN): selected_mode = "online" if selected_mode == "cpu" else "cpu"
                    elif event.key == pygame.K_RETURN:
                        game_mode = selected_mode
                        game_state = "char_select" if game_mode == "cpu" else "ip_input"
                elif game_state == "ip_input":
                    if event.key == pygame.K_RETURN: game_state = "waiting_connect"
                    elif event.key == pygame.K_BACKSPACE: ip_address = ip_address[:-1]
                    else: ip_address += event.unicode
                elif game_state == "char_select" and not my_char_ready:
                    if event.key == pygame.K_LEFT: my_char_index = (my_char_index - 1) % len(characters)
                    elif event.key == pygame.K_RIGHT: my_char_index = (my_char_index + 1) % len(characters)
                    elif event.key == pygame.K_RETURN: my_char_ready = True
                elif game_state == "stage_select" and (game_mode == "cpu" or (network and network.player_id == 0)):
                    if event.key == pygame.K_LEFT: my_stage_index = (my_stage_index - 1) % len(backgrounds)
                    elif event.key == pygame.K_RIGHT: my_stage_index = (my_stage_index + 1) % len(backgrounds)
                    elif event.key == pygame.K_RETURN: game_state = "start_game"
                elif game_state == "result":
                    if event.key == pygame.K_t:
                        game_state, game_mode, selected_mode = "title", "cpu", "cpu"
                        if network: network.close(); network = None
                        my_char_index, my_stage_index, my_char_ready = 0, 0, False
                        player1, player2, game_over = None, None, False
                    elif event.key == pygame.K_r and game_mode == "cpu":
                        game_state = "char_select"; my_char_ready = False; player1, player2, game_over = None, None, False

        # 3. 画面描画とロジック
        screen.fill(BLACK)
        if game_state == "title":
            draw_title_screen(screen, selected_mode)
        elif game_state == "ip_input":
            draw_ip_input_screen(screen, ip_address, ip_input_message)
        elif game_state == "waiting_connect":
            draw_waiting_screen(screen, "サーバーに接続中..."); pygame.display.flip()
            network = Network()
            if network.connect(ip_address):
                game_state = "char_select"
                ip_input_message = ""
            else:
                game_state = "ip_input"
                ip_input_message = "接続失敗"
        elif game_state == "char_select":
            if (game_mode == "cpu" and my_char_ready) or \
               (game_mode == "online" and my_char_ready and opponent_data.get("ready")):
                game_state = "stage_select"
            draw_character_select(screen, my_char_index, opponent_data.get("char_index", 0), my_char_ready)
        elif game_state == "stage_select":
            can_select = game_mode == "cpu" or (network and network.player_id == 0)
            if not can_select:
                my_stage_index = opponent_data.get("stage_index", 0)
            if game_mode == "online" and opponent_data.get("stage_index", -1) != -1:
                 game_state = "start_game"
            draw_stage_select(screen, my_stage_index, can_select)
        elif game_state == "start_game":
            p1_idx = my_char_index
            p2_idx = opponent_data.get("char_index", 0) if game_mode == "online" else random.randint(0, len(characters)-1)
            p1_char, p2_char = characters[p1_idx], characters[p2_idx]
            if game_mode == "cpu":
                player1 = Player(100, HEIGHT - 110, p1_char["color"])
                player2 = Player(600, HEIGHT - 110, p2_char["color"], True)
            else:
                if network.player_id == 0:
                    player1, player2 = Player(100,HEIGHT-110,p1_char["color"]), Player(600,HEIGHT-110,p2_char["color"])
                else:
                    player1, player2 = Player(600,HEIGHT-110,p1_char["color"]), Player(100,HEIGHT-110,p2_char["color"])
            if backgrounds:
                selected_background = backgrounds[my_stage_index]["image"]
            game_state = "in_game"
        elif game_state == "in_game":
            if selected_background:
                screen.blit(selected_background, (0,0))
            if not game_over:
                keys = pygame.key.get_pressed()
                player1.handle_input(keys, player2)
                if game_mode == "cpu":
                    player2.handle_input(None, player1)
                else:
                    player2.handle_input(opponent_data.get("keys", {}), player1)
                player1.update()
                player2.update()
                check_attack(player1, player2)
                check_attack(player2, player1)
                check_projectile_hit(player1, player2)
                check_projectile_hit(player2, player1)
                if player1.hp <= 0 or player2.hp <= 0:
                    winner_text = "Player 1 WINS" if player2.hp <= 0 else "Player 2 WINS"
                    game_over = True
                    game_state = "result"
            player1.draw(screen)
            player2.draw(screen)
            draw_hp_bar(screen, 50, 20, player1.hp)
            draw_hp_bar(screen, 550, 20, player2.hp)
        elif game_state == "result":
            draw_result_screen(screen, winner_text)

        pygame.display.flip()
        clock.tick(FPS)

    if network:
        network.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()