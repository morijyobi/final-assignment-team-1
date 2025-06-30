import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("闘拳伝説CPU戦")

clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 180, 0)
GRAY = (150, 150, 150)
HADOUKEN_COLOR = (0, 100, 255)
KAMEHAMEHA_COLOR = (0, 200, 255)

backgrounds = [
    {"name": "道場", "image": pygame.image.load("img/dojo.png")},
    {"name": "古代寺", "image": pygame.image.load("img/temple.png")},
    {"name": "森", "image": pygame.image.load("img/forest.png")},
]

selected_index = 0
selected_stage = 0
show_title = True
show_character_select = False
show_stage_select = False

def draw_stage_select(screen, selected_stage):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont("meiryo", 40)
    title = font.render("ステージを選んでください", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    for i, bg in enumerate(backgrounds):
        name = bg["name"]
        rect = pygame.Rect(150 + i * 200, 150, 100, 100)
        pygame.draw.rect(screen, WHITE, rect, 4 if i == selected_stage else 1)
        text = font.render(name, True, WHITE)
        screen.blit(text, (rect.centerx - text.get_width() // 2, rect.bottom + 10))
        
def draw_character_select(screen, selected_index):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont("meiryo", 40)
    title = font.render("キャラを選んでください", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    for i, char in enumerate(characters):
        color = char["color"]
        name = char["name"]
        rect = pygame.Rect(150 + i * 200, 150, 100, 100)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, WHITE, rect, 4 if i == selected_index else 1)

        text = font.render(name, True, WHITE)
        screen.blit(text, (rect.centerx - text.get_width() // 2, rect.bottom + 10))

def draw_tutorial(screen):
    tutorial_lines = [
        "=== 操作方法チュートリアル ===",
        "← / → ：移動",
        "↑：ジャンプ",
        "↓：しゃがみ",
        "Aキー：弱攻撃（昇龍拳 →↓→ + A）",
        "Sキー：強攻撃（波動拳 ↓→ + S、竜巻旋風脚 ←↓→ + S）",
        "Dキー：ガード（押しっぱなし）",
        "Kキー：かめはめ波（遠距離攻撃）",
        "ESCキー：チュートリアルを閉じる",
        "",
        "体力が0になると敗北です！"
    ]
    font = pygame.font.SysFont("meiryo", 28)  
    bg_rect = pygame.Rect(100, 50, 600, 300)
    pygame.draw.rect(screen, (0, 0, 0), bg_rect)
    pygame.draw.rect(screen, WHITE, bg_rect, 2)

    for i, line in enumerate(tutorial_lines):
        text = font.render(line, True, WHITE)
        screen.blit(text, (120, 70 + i * 30))

def draw_title_screen(screen):
    screen.fill((0, 0, 0))
    font_big = pygame.font.SysFont("meiryo", 64)
    font_small = pygame.font.SysFont("meiryo", 28)

    title_text = font_big.render("闘拳伝説CPU戦", True, WHITE)
    instruction_text = font_small.render("スペースキーでゲーム開始", True, WHITE)

    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
    screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2))

def draw_result_screen(screen, winner_text):
    screen.fill((0, 0, 0))
    font_title = pygame.font.SysFont("meiryo", 48)
    font_menu = pygame.font.SysFont("meiryo", 28)

    result = font_title.render(winner_text, True, WHITE)
    retry = font_menu.render("Rキー：リトライ", True, WHITE)
    to_title = font_menu.render("Tキー：タイトルへ戻る", True, WHITE)

    screen.blit(result, (WIDTH // 2 - result.get_width() // 2, HEIGHT // 3))
    screen.blit(retry, (WIDTH // 2 - retry.get_width() // 2, HEIGHT // 2))
    screen.blit(to_title, (WIDTH // 2 - to_title.get_width() // 2, HEIGHT // 2 + 40))
    
class Hadouken:
    WIDTH, HEIGHT = 30, 15
    SPEED = 12

    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.direction = direction
        self.active = True

    def update(self):
        if self.direction == 'right':
            self.rect.x += self.SPEED
        else:
            self.rect.x -= self.SPEED

        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.active = False

    def draw(self, screen):
        pygame.draw.ellipse(screen, HADOUKEN_COLOR, self.rect)


class Kamehameha:
    WIDTH, HEIGHT = 60, 25
    SPEED = 8
    DAMAGE = 8

    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.direction = direction
        self.active = True

    def update(self):
        if self.direction == 'right':
            self.rect.x += self.SPEED
        else:
            self.rect.x -= self.SPEED

        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.active = False

    def draw(self, screen):
        pygame.draw.rect(screen, KAMEHAMEHA_COLOR, self.rect)


class Player:
    WIDTH, HEIGHT = 40, 80
    SPEED = 5
    JUMP_POWER = 15
    GRAVITY = 1

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
        self.is_raigekiken = False
        self.raigekiken_timer = 0

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

    def handle_input(self, keys=None, opponent=None):
        if self.is_cpu:
            self.ai_behavior(opponent)
            return

        self.is_guarding = False
        self.is_crouch = False

        if self.is_tatsumaki:
            return

        if keys[pygame.K_a]:
            self.rect.x -= self.SPEED
            self.facing_right = False
            self.add_command('←')
        if keys[pygame.K_d]:
            self.rect.x += self.SPEED
            self.facing_right = True
            self.add_command('→')

        if keys[pygame.K_w] and self.on_ground:
            self.vel_y = -self.JUMP_POWER
            self.on_ground = False
            self.add_command('↑')
        if keys[pygame.K_s] and self.on_ground:
            self.is_crouch = True
            self.add_command('↓')

        if keys[pygame.K_h]:
            self.is_guarding = True

        if keys[pygame.K_j] and self.attack_cooldown == 0:
            if self.check_shoryuken_command():
                self.attack_cooldown = 30
                self.attack_type = 'shoryuken'
                self.is_attacking = True
                self.attack_hit_done = False
                self.is_shoryuken = True
                self.shoryuken_timer = 15
                self.command_buffer.clear()
            elif self.check_raigekiken_command():
                self.attack_cooldown = 40
                self.attack_type = 'raigekiken'
                self.is_attacking = True
                self.attack_hit_done = False
                self.is_raigekiken = True
                self.raigekiken_timer = 20
                self.command_buffer.clear()
            else:
                self.attack_cooldown = 15
                self.attack_type = 'weak'
                self.is_attacking = True
                self.attack_hit_done = False

        elif keys[pygame.K_l] and self.attack_cooldown == 0:
            if self.check_hadouken_command():
                self.fire_hadouken()
                self.attack_cooldown = 30
                self.command_buffer.clear()
            elif self.check_tatsumaki_command():
                self.attack_cooldown = 40
                self.attack_type = 'tatsumaki'
                self.is_attacking = True
                self.attack_hit_done = False
                self.is_tatsumaki = True
                self.tatsumaki_timer = self.tatsumaki_duration
                self.command_buffer.clear()
            else:
                self.attack_cooldown = 20
                self.attack_type = 'strong'
                self.is_attacking = True
                self.attack_hit_done = False

        elif keys[pygame.K_k] and self.attack_cooldown == 0:
            self.fire_kamehameha()
            self.attack_cooldown = 60  # クールダウン長め
            self.attack_type = 'kamehameha'

        if self.command_timer > 0:
            self.command_timer -= 1
        else:
            self.command_buffer.clear()

    def add_command(self, cmd):
        self.command_buffer.append(cmd)
        if len(self.command_buffer) > 10:
            self.command_buffer.pop(0)
        self.command_timer = self.command_timeout

    def check_hadouken_command(self):
        cmd_str = ''.join(self.command_buffer)
        return '↓→' in cmd_str[-3:] or '↓→' in cmd_str

    def check_shoryuken_command(self):
        return '→↓→' in ''.join(self.command_buffer)[-5:]

    def check_tatsumaki_command(self):
        return '←↓→' in ''.join(self.command_buffer)[-5:]
    
    def check_raigekiken_command(self):
        return '↓←→' in ''.join(self.command_buffer)[-5:]

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
        self.is_guarding = False
        self.is_crouch = False

        if opponent.rect.centerx > self.rect.centerx + 50:
            self.rect.x += self.SPEED // 2
            self.facing_right = True
            self.add_command('→')
        elif opponent.rect.centerx < self.rect.centerx - 50:
            self.rect.x -= self.SPEED // 2
            self.facing_right = False
            self.add_command('←')
        else:
            action = random.randint(0, 100)
            if action < 10 and self.attack_cooldown == 0:
                self.attack_cooldown = 15
                self.attack_type = 'weak'
                self.is_attacking = True
                self.attack_hit_done = False
            elif action < 20:
                self.is_guarding = True
            elif action < 25 and self.attack_cooldown == 0:
                self.fire_hadouken()
                self.attack_cooldown = 30

    def update(self):
        self.vel_y += self.GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom >= HEIGHT - 30:
            self.rect.bottom = HEIGHT - 30
            self.vel_y = 0
            self.on_ground = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        else:
            self.is_attacking = False
            self.is_shoryuken = False
            self.is_tatsumaki = False

        if self.is_shoryuken:
            self.shoryuken_timer -= 1
            if self.shoryuken_timer > 7:
                self.vel_y = -self.JUMP_POWER // 2

        if self.is_tatsumaki:
            self.tatsumaki_timer -= 1
            self.rect.x += self.tatsumaki_speed if self.facing_right else -self.tatsumaki_speed
            self.rect.y += -2 if self.tatsumaki_timer % 10 < 5 else 2
            if self.rect.bottom > HEIGHT - 30:
                self.rect.bottom = HEIGHT - 30
            if self.tatsumaki_timer <= 0:
                self.is_tatsumaki = False
                
        if self.is_raigekiken:
            self.raigekiken_timer -= 1
            if self.raigekiken_timer <= 0:
                self.is_raigekiken = False

        # Update hadouken projectiles
        for h in self.hadouken_list:
            h.update()
        self.hadouken_list = [h for h in self.hadouken_list if h.active]

        # Update kamehameha projectiles
        for k in self.kamehameha_list:
            k.update()
        self.kamehameha_list = [k for k in self.kamehameha_list if k.active]

    def draw(self, screen):
        color = GRAY if self.is_guarding else self.color
        pygame.draw.rect(screen, color, self.rect)

        # Draw projectiles
        for h in self.hadouken_list:
            h.draw(screen)
        for k in self.kamehameha_list:
            k.draw(screen)

        if self.is_raigekiken:
            effect_color = (100, 100, 255)
            effect_rect = pygame.Rect(
                self.rect.right if self.facing_right else self.rect.left - 60,
                self.rect.centery - 10,
                60, 20
            )
            pygame.draw.rect(screen, effect_color, effect_rect)
            pygame.draw.line(screen, (255, 255, 255), 
                            (effect_rect.left, effect_rect.top), 
                            (effect_rect.right, effect_rect.bottom), 2)

def check_attack(attacker, defender):
    if attacker.is_attacking and not attacker.attack_hit_done:
        attack_rect = attacker.rect.copy()
        if attacker.attack_type == 'weak':
            if attacker.facing_right:
                attack_rect.width += 20
            else:
                attack_rect.x -= 20
                attack_rect.width += 20
        elif attacker.attack_type == 'strong':
            if attacker.facing_right:
                attack_rect.width += 30
            else:
                attack_rect.x -= 30
                attack_rect.width += 30
        elif attacker.attack_type == 'shoryuken':
            attack_rect.y -= 20
            attack_rect.height += 40
        elif attacker.attack_type == 'raigekiken':
            if attacker.facing_right:
                attack_rect.width += 50
            else:
                attack_rect.x -= 50
                attack_rect.width += 50
            attack_rect.height += 20

        # ✅ ヒット時の処理（ここが重要！）
        if attack_rect.colliderect(defender.rect):
            if not defender.is_guarding:
                # 攻撃タイプごとにダメージ調整
                if attacker.attack_type == 'weak':
                    defender.hp -= 6
                elif attacker.attack_type == 'strong':
                    defender.hp -= 10
                elif attacker.attack_type == 'shoryuken':
                    defender.hp -= 12
                elif attacker.attack_type == 'raigekiken':
                    defender.hp -= 18
                elif attacker.attack_type == 'tatsumaki':
                    defender.hp -= 10
            # 1回だけ当たるように
            attacker.attack_hit_done = True


def check_projectile_hit(attacker, defender):
    for h in attacker.hadouken_list:
        if h.rect.colliderect(defender.rect):
            if not defender.is_guarding:
                defender.hp -= 8
            h.active = False
    for k in attacker.kamehameha_list:
        if k.rect.colliderect(defender.rect):
            if not defender.is_guarding:
                defender.hp -= k.DAMAGE
            k.active = False


def draw_hp_bar(screen, x, y, hp):
    pygame.draw.rect(screen, RED, (x, y, 200, 20))
    pygame.draw.rect(screen, GREEN, (x, y, 2 * hp, 20))

# 省略（draw_character_select 〜 draw_result_screen, Hadouken, Kamehameha, Playerなどは同じ）
# ...

class Seiryu(Player):
    def __init__(self, x, y, is_cpu=False):
        super().__init__(x, y, BLUE, is_cpu)
        self.SPEED = 5
        self.JUMP_POWER = 15
        self.special_moves = ["shoryuken", "hadouken", "kamehameha"]
        
class Akatora(Player):
    def __init__(self, x, y, is_cpu=False):
        super().__init__(x, y, RED, is_cpu)
        self.SPEED = 7
        self.JUMP_POWER = 13
        self.special_moves = ["tatsumaki", "hadouken"]

class Midorikaze(Player):
    def __init__(self, x, y, is_cpu=False):
        super().__init__(x, y, GREEN, is_cpu)
        self.SPEED = 4
        self.JUMP_POWER = 17
        self.special_moves = ["kamehameha", "hadouken"]

characters = [
    {"name": "青龍", "color": BLUE, "class": Seiryu},
    {"name": "赤虎", "color": RED, "class": Akatora},
    {"name": "緑風", "color": GREEN, "class": Midorikaze},
]

def main():
    global show_title, show_character_select, selected_index, selected_stage, show_stage_select
    player = None
    cpu = None
    selected_background = None

    show_tutorial = False
    running = True
    game_over = False
    show_result = False
    winner_text = ""

    while running:
        screen.fill((30, 30, 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if show_title:
                    if event.key == pygame.K_SPACE:
                        show_title = False 
                        show_character_select = True
                elif show_character_select:
                    if event.key == pygame.K_LEFT:
                        selected_index = (selected_index - 1) % len(characters)
                    elif event.key == pygame.K_RIGHT:
                        selected_index = (selected_index + 1) % len(characters)
                    elif event.key == pygame.K_RETURN:
                        show_character_select = False
                        show_stage_select = True  # ステージ選択へ

                elif show_stage_select:
                    if event.key == pygame.K_LEFT:
                        selected_stage = (selected_stage - 1) % len(backgrounds)
                    elif event.key == pygame.K_RIGHT:
                        selected_stage = (selected_stage + 1) % len(backgrounds)
                    elif show_stage_select:
                        if event.key == pygame.K_RETURN:
                            # 選択済のキャラとステージでゲーム本番を初期化
                            selected_char = characters[selected_index]
                            player = selected_char["class"](100, HEIGHT - 110, is_cpu=False)
                            cpu = Akatora(600, HEIGHT - 110, is_cpu=True)
                            selected_background = backgrounds[selected_stage]["image"]
                            show_stage_select = False
                            game_over = False
                            show_result = False


                elif show_result:
                    if  event.key == pygame.K_r:
                        show_stage_select = True  # ✅ ステージ選択に戻る
                        selected_char = characters[selected_index]
                        player = selected_char["class"](100, HEIGHT - 110, is_cpu=False)
                        cpu = Akatora(600, HEIGHT - 110, is_cpu=True)
                        game_over = False
                        show_result = False
                        show_character_select = False  # これが抜けていると止まる可能性

                    elif event.key == pygame.K_t:
                        show_result = False
                        show_title = True
                        show_character_select = False
                        show_stage_select = False
                        # フロー再利用のためのリセット
                        selected_background = None
                        selected_stage = 0


                else:
                    if event.key == pygame.K_ESCAPE:
                        show_tutorial = not show_tutorial

        if show_title:
            draw_title_screen(screen)
        elif show_character_select:
            draw_character_select(screen, selected_index)
        elif show_stage_select:
            draw_stage_select(screen, selected_stage)
        elif show_tutorial:
            draw_tutorial(screen)
        elif show_result:
            draw_result_screen(screen, winner_text)
        else:
            if selected_background:
                screen.blit(pygame.transform.scale(selected_background, (WIDTH, HEIGHT)), (0, 0))
            else:
                screen.fill((0, 0, 0))

            if not game_over:
                keys = pygame.key.get_pressed()
                player.handle_input(keys, cpu)
                cpu.handle_input(opponent=player)

                player.update()
                cpu.update()

                check_attack(player, cpu)
                check_attack(cpu, player)

                check_projectile_hit(player, cpu)
                check_projectile_hit(cpu, player)

            player.draw(screen)
            cpu.draw(screen)

            draw_hp_bar(screen, 50, 20, player.hp)
            draw_hp_bar(screen, 550, 20, cpu.hp)

            font = pygame.font.SysFont(None, 36)
            if player.hp <= 0:
                winner_text = "CPUの勝ち！"
                game_over = True
                show_result = True
            elif cpu.hp <= 0:
                winner_text = "プレイヤーの勝ち！"
                game_over = True
                show_result = True

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
