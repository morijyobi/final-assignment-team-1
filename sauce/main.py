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

# チュートリアル表示関数
def draw_tutorial(screen):
    tutorial_lines = [
        "=== 操作方法チュートリアル ===",
        "← / → ：移動",
        "↑：ジャンプ",
        "↓：しゃがみ",
        "Aキー：弱攻撃（昇龍拳コマンド →↓→ + A）",
        "Sキー：強攻撃（波動拳コマンド ↓→ + S、竜巻旋風脚 ←↓→ + S）",
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

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.SPEED
            self.facing_right = False
            self.add_command('←')
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.SPEED
            self.facing_right = True
            self.add_command('→')

        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = -self.JUMP_POWER
            self.on_ground = False
            self.add_command('↑')
        if keys[pygame.K_DOWN] and self.on_ground:
            self.is_crouch = True
            self.add_command('↓')

        if keys[pygame.K_d]:
            self.is_guarding = True

        if keys[pygame.K_a] and self.attack_cooldown == 0:
            if self.check_shoryuken_command():
                self.attack_cooldown = 30
                self.attack_type = 'shoryuken'
                self.is_attacking = True
                self.attack_hit_done = False
                self.is_shoryuken = True
                self.shoryuken_timer = 15
                self.command_buffer.clear()
            else:
                self.attack_cooldown = 15
                self.attack_type = 'weak'
                self.is_attacking = True
                self.attack_hit_done = False

        elif keys[pygame.K_s] and self.attack_cooldown == 0:
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

        if attack_rect.colliderect(defender.rect) and not defender.is_guarding:
            defender.hp -= 10
            attacker.attack_hit_done = True
        elif attack_rect.colliderect(defender.rect) and defender.is_guarding:
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


def main():
    player = Player(100, HEIGHT - 110, BLUE, is_cpu=False)
    cpu = Player(600, HEIGHT - 110, RED, is_cpu=True)

    show_tutorial = False
    running = True
    show_title = True

    while running:
        screen.fill((30, 30, 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if show_title:
                    if event.key == pygame.K_SPACE:
                        show_title = False
                        player.hp = 100
                        cpu.hp = 100
                        player.rect.x, player.rect.y = 100, HEIGHT - 110
                        cpu.rect.x, cpu.rect.y = 600, HEIGHT - 110
                        player.is_attacking = False
                        cpu.is_attacking = False
                        player.hadouken_list.clear()
                        player.kamehameha_list.clear()
                        cpu.hadouken_list.clear()
                        cpu.kamehameha_list.clear()
                else:
                    if event.key == pygame.K_ESCAPE:
                        show_tutorial = not show_tutorial

        if show_title:
            draw_title_screen(screen)
        elif show_tutorial:
            draw_tutorial(screen)
        else:
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
                text = font.render("CPUの勝ち！", True, WHITE)
                screen.blit(text, (WIDTH // 2 - 80, HEIGHT // 2))
            elif cpu.hp <= 0:
                text = font.render("プレイヤーの勝ち！", True, WHITE)
                screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
