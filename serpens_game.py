import pygame
import random
import json
import os

# ===================== CHECKPOINT =====================
def load_checkpoint():
    if os.path.exists("checkpoint.json"):
        with open("checkpoint.json", "r") as f:
            return json.load(f)
    return {}

def save_checkpoint(player_name, level):
    checkpoint = load_checkpoint()
    checkpoint[player_name] = level
    with open("checkpoint.json", "w") as f:
        json.dump(checkpoint, f)

def get_saved_level(player_name):
    checkpoint = load_checkpoint()
    return checkpoint.get(player_name, 1)

def delete_checkpoint(player_name):
    checkpoint = load_checkpoint()
    if player_name in checkpoint:
        del checkpoint[player_name]
        with open("checkpoint.json", "w") as f:
            json.dump(checkpoint, f)

# ===================== PYGAME AYARLARI =====================
pygame.init()
width  = 600
height = 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Serpens")
clock = pygame.time.Clock()

ui_font    = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 28)
try:
    game_font_big   = pygame.font.Font("PressStart2P-Regular.ttf", 30)
    game_font_small = pygame.font.Font("PressStart2P-Regular.ttf", 16)
except:
    game_font_big   = pygame.font.Font(None, 48)
    game_font_small = pygame.font.Font(None, 28)

# ===================== SABİTLER =====================
snake_size = 25
food_size  = 10

LEVEL_SETTINGS = {
    1: {"target": 15, "speed": 10, "obstacles": False, "moving_food": False, "food_speed": 0},
    2: {"target": 10, "speed": 15, "obstacles": False, "moving_food": False, "food_speed": 0},
    3: {"target": 5,  "speed": 15, "obstacles": True,  "moving_food": False, "food_speed": 0},
    4: {"target": 3,  "speed": 15, "obstacles": True,  "moving_food": True,  "food_speed": 2},
    5: {"target": 1,  "speed": 15, "obstacles": False, "moving_food": True,  "food_speed": 12},
}
MAX_LEVEL = 5

OBSTACLES = [
    pygame.Rect(100, 80,  20,  130),
    pygame.Rect(300, 60,  120, 20),
    pygame.Rect(460, 180, 20,  140),
    pygame.Rect(140, 270, 140, 20),
    pygame.Rect(260, 160, 20,  100),
]

# ===================== GLOBAL OYUN DEĞİŞKENLERİ =====================
# Ekran durumu:
#   "name_input"   -> isim giriş ekranı
#   "continue_ask" -> kaldığın yerden devam et?
#   "playing"      -> oyun
#   "game_over"    -> game over
#   "game_won"     -> kazandın
screen_state = "name_input"

player_name_text = ""
player_name      = "Player"
input_box        = pygame.Rect(width // 2 - 200, height // 2 - 25, 400, 50)
box_color        = pygame.Color('dodgerblue2')

snake_x = snake_y = width // 2
dx = speed = 10
dy = 0
snake        = []
snake_length = 1
food_x = food_y = 0
food_dx = food_dy = 0
current_level   = 1
foods_collected = 0
food_stunned    = 0   # sersem kalan frame sayısı (>0 ise donuk)
level_timer     = 0   # level başından beri geçen saniye (15fps ile artar)

# Butonlar (her frame yeniden çizilir, tıklama burada tutulur)
btn_A = pygame.Rect(0, 0, 0, 0)
btn_B = pygame.Rect(0, 0, 0, 0)

# ===================== YARDIMCI FONKSİYONLAR =====================
HUD_HEIGHT = 32  # HUD şeridinin yüksekliği

def safe_food_position(obstacles_active):
    for _ in range(300):
        fx = random.randint(0, width  - food_size)
        fy = random.randint(HUD_HEIGHT + 2, height - food_size)  # HUD alanına düşmesin
        if obstacles_active:
            food_rect = pygame.Rect(fx, fy, food_size, food_size)
            if not any(food_rect.colliderect(o) for o in OBSTACLES):
                return fx, fy
        else:
            return fx, fy
    return width // 3, height // 2


def reset_game(level=1):
    global snake_x, snake_y, dx, dy, speed, snake, snake_length
    global food_x, food_y, food_dx, food_dy, food_stunned, level_timer, current_level, foods_collected

    current_level   = level
    foods_collected = 0
    snake_x = width  // 2
    snake_y = height // 2
    speed   = LEVEL_SETTINGS[level]["speed"]
    dx      = speed
    dy      = 0
    snake        = []
    snake_length = 1
    food_x, food_y = safe_food_position(LEVEL_SETTINGS[level]["obstacles"])
    fs = LEVEL_SETTINGS[level]["food_speed"]
    food_dx = random.choice([-fs, fs]) if fs else 0
    food_dy = random.choice([-fs, fs]) if fs else 0
    food_stunned = 0
    level_timer  = 0


def draw_level_transition():
    screen.fill((15, 15, 40))
    l1 = game_font_big.render(f"LEVEL {current_level}", True, (255, 215, 0))
    l2 = game_font_small.render("GET READY!", True, (255, 255, 255))
    screen.blit(l1, (width // 2 - l1.get_width() // 2, height // 2 - 60))
    screen.blit(l2, (width // 2 - l2.get_width() // 2, height // 2 + 10))
    pygame.display.update()
    pygame.time.wait(2000)


def draw_hud():
    target    = LEVEL_SETTINGS[current_level]["target"]
    # Siyah arka plan şeridi
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, width, HUD_HEIGHT))
    pygame.draw.line(screen, (60, 60, 60), (0, HUD_HEIGHT), (width, HUD_HEIGHT), 1)

    # Sol: Level
    lv = small_font.render(f"Level: {current_level}/{MAX_LEVEL}", True, (255, 255, 255))
    screen.blit(lv, (8, 4))

    # Orta: Score X/Y formatında
    sc = small_font.render(f"Score: {foods_collected}/{target}", True, (255, 255, 255))
    screen.blit(sc, (width // 2 - sc.get_width() // 2, 4))

    # Sağ: Süre (level 5'te geri sayım gibi göster)
    total_secs = int(level_timer)
    mins = total_secs // 60
    secs = total_secs % 60
    time_str = f"{mins:02d}:{secs:02d}"
    tc = small_font.render(f"Time: {time_str}", True, (200, 200, 200))
    screen.blit(tc, (width - tc.get_width() - 8, 4))




def draw_button(rect, bg, border, text, font):
    pygame.draw.rect(screen, bg,     rect)
    pygame.draw.rect(screen, border, rect, 3)
    s = font.render(text, True, (255, 255, 255))
    screen.blit(s, (rect.centerx - s.get_width() // 2, rect.centery - s.get_height() // 2))


# ===================== ANA DÖNGÜ =====================
running = True
while running:
    mouse_clicked = False
    mouse_pos     = (0, 0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # İSİM GİRİŞİ
        if screen_state == "name_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    typed = player_name_text.strip()
                    # --- GİZLİ KOD: dev1 .. dev5 ---
                    if typed.lower() in ("dev1","dev2","dev3","dev4","dev5"):
                        target_level = int(typed[-1])
                        player_name  = "DEV"
                        reset_game(target_level)
                        draw_level_transition()
                        screen_state = "playing"
                    else:
                        player_name = typed or "Player"
                        saved = get_saved_level(player_name)
                        if saved > 1:
                            screen_state = "continue_ask"
                        else:
                            reset_game(1)
                            draw_level_transition()
                            screen_state = "playing"
                elif event.key == pygame.K_BACKSPACE:
                    player_name_text = player_name_text[:-1]
                else:
                    if len(player_name_text) < 16:
                        player_name_text += event.unicode

        # MOUSE
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True
            mouse_pos     = event.pos

        # OYUN KONTROLLERİ
        if screen_state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP    and dy <= 0: dx = 0;      dy = -speed
                elif event.key == pygame.K_DOWN  and dy >= 0: dx = 0;      dy = speed
                elif event.key == pygame.K_LEFT  and dx <= 0: dx = -speed; dy = 0
                elif event.key == pygame.K_RIGHT and dx >= 0: dx = speed;  dy = 0
                elif event.key == pygame.K_LSHIFT:
                    boost = LEVEL_SETTINGS[current_level]["speed"] * 2
                    if dx > 0: dx = boost
                    elif dx < 0: dx = -boost
                    if dy > 0: dy = boost
                    elif dy < 0: dy = -boost
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    base = LEVEL_SETTINGS[current_level]["speed"]
                    if dx > 0: dx = base
                    elif dx < 0: dx = -base
                    if dy > 0: dy = base
                    elif dy < 0: dy = -base

    # ======================================================
    # EKRAN: İSİM GİRİŞİ
    # ======================================================
    if screen_state == "name_input":
        screen.fill((30, 30, 30))
        screen.blit(title_font.render("SERPENS", True, (255,215,0)),
                    (width//2 - title_font.render("SERPENS",True,(0,0,0)).get_width()//2, height//2 - 150))
        screen.blit(ui_font.render("Enter Your Name", True, (255,255,255)),
                    (width//2 - ui_font.render("Enter Your Name",True,(0,0,0)).get_width()//2, height//2 - 90))
        screen.blit(small_font.render("Press Enter to continue", True, (180,180,180)),
                    (width//2 - small_font.render("Press Enter to continue",True,(0,0,0)).get_width()//2, height//2 + 40))
        t = ui_font.render(player_name_text + "|", True, (255,255,255))
        screen.blit(t, (input_box.x + 10, input_box.y + 10))
        pygame.draw.rect(screen, box_color, input_box, 2)
        clock.tick(30)

    # ======================================================
    # EKRAN: DEVAM ET Mİ?
    # ======================================================
    elif screen_state == "continue_ask":
        saved_lvl = get_saved_level(player_name)
        screen.fill((20, 20, 40))
        t1 = ui_font.render(f"Welcome back, {player_name}!", True, (255,215,0))
        t2 = small_font.render(f"You reached Level {saved_lvl} last time.", True, (200,200,200))
        screen.blit(t1, (width//2 - t1.get_width()//2, height//2 - 110))
        screen.blit(t2, (width//2 - t2.get_width()//2, height//2 - 65))

        btn_A = pygame.Rect(width//2 - 150, height//2 - 15, 300, 50)
        btn_B = pygame.Rect(width//2 - 150, height//2 + 55, 300, 45)
        draw_button(btn_A, (0,100,0),  (0,0,0), f"Continue (Level {saved_lvl})", small_font)
        draw_button(btn_B, (120,0,0),  (0,0,0), "Start from Level 1",            small_font)

        if mouse_clicked:
            if btn_A.collidepoint(mouse_pos):
                reset_game(saved_lvl)
                draw_level_transition()
                screen_state = "playing"
            elif btn_B.collidepoint(mouse_pos):
                delete_checkpoint(player_name)
                reset_game(1)
                draw_level_transition()
                screen_state = "playing"
        clock.tick(30)

    # ======================================================
    # EKRAN: OYUN
    # ======================================================
    elif screen_state == "playing":
        settings = LEVEL_SETTINGS[current_level]

        # Sayaç: her frame 1/15 saniye geçiyor (15 FPS)
        level_timer += 1 / 15

        # Hareketli yiyecek
        if settings["moving_food"]:
            food_x += food_dx
            food_y += food_dy

            if food_x <= 0:
                food_x = 0
                food_dx = abs(food_dx)
            elif food_x + food_size >= width:
                food_x = width - food_size
                food_dx = -abs(food_dx)
            if food_y <= HUD_HEIGHT:
                food_y = HUD_HEIGHT
                food_dy = abs(food_dy)
            elif food_y + food_size >= height:
                food_y = height - food_size
                food_dy = -abs(food_dy)

        # Hareket
        snake_x += dx
        snake_y += dy

        # Çarpışma kontrolleri
        if snake_x < 0 or snake_x + snake_size > width or snake_y < 0 or snake_y + snake_size > height:
            screen_state = "game_over"

        if [snake_x, snake_y] in snake[:-1]:
            screen_state = "game_over"

        snake.append([snake_x, snake_y])
        if len(snake) > snake_length:
            snake.pop(0)

        if settings["obstacles"]:
            sr = pygame.Rect(snake_x, snake_y, snake_size, snake_size)
            if any(sr.colliderect(o) for o in OBSTACLES):
                screen_state = "game_over"

        # Yiyecek yeme
        if (snake_x < food_x + food_size and snake_x + snake_size > food_x and
                snake_y < food_y + food_size and snake_y + snake_size > food_y):
            snake_length    += 1
            foods_collected += 1

            if foods_collected >= settings["target"]:
                if current_level < MAX_LEVEL:
                    current_level  += 1
                    foods_collected = 0
                    snake_length = 1          # <<<< YILAN BOYUTU SIFIRLA
                    snake = []                # <<<< GÖVDE TEMİZLE
                    speed = LEVEL_SETTINGS[current_level]["speed"]
                    if dx > 0: dx = speed
                    elif dx < 0: dx = -speed
                    if dy > 0: dy = speed
                    elif dy < 0: dy = -speed
                    food_x, food_y = safe_food_position(LEVEL_SETTINGS[current_level]["obstacles"])
                    fs = LEVEL_SETTINGS[current_level]["food_speed"]
                    food_dx = random.choice([-fs, fs]) if fs else 0
                    food_dy = random.choice([-fs, fs]) if fs else 0
                    food_stunned = 0
                    level_timer  = 0
                    save_checkpoint(player_name, current_level)  # <<<< KAYDET
                    draw_level_transition()
                else:
                    delete_checkpoint(player_name)  # Oyun bitti, checkpoint sil
                    screen_state = "game_won"
            else:
                food_x, food_y = safe_food_position(settings["obstacles"])

        # ÇİZİM
        screen.fill((50, 150, 100))
        if settings["obstacles"]:
            for obs in OBSTACLES:
                pygame.draw.rect(screen, (180, 40, 40), obs)
                pygame.draw.rect(screen, (100, 0,  0),  obs, 2)

        if settings["moving_food"]:
            food_color = (255, 80, 80)
        else:
            food_color = (220, 30, 30)
        pygame.draw.rect(screen, food_color, (food_x, food_y, food_size, food_size))

        for i, block in enumerate(snake):
            pygame.draw.rect(screen,
                             (10,10,80) if i < len(snake)-1 else (40,40,160),
                             (block[0], block[1], snake_size, snake_size))

        name_s = small_font.render(player_name, True, (255,255,0))
        screen.blit(name_s, (snake_x + snake_size//2 - name_s.get_width()//2, snake_y - 22))
        draw_hud()
        clock.tick(15)

    # ======================================================
    # EKRAN: GAME OVER
    # ======================================================
    elif screen_state == "game_over":
        screen.fill((50, 150, 100))
        t = game_font_big.render("GAME OVER", True, (255,255,255))
        screen.blit(t, (width//2 - t.get_width()//2, height//2 - 90))
        ls = small_font.render(f"Reached Level {current_level}", True, (200,200,200))
        screen.blit(ls, (width//2 - ls.get_width()//2, height//2 - 40))

        btn_A = pygame.Rect(width//2 - 170, height//2 + 5,  340, 52)
        btn_B = pygame.Rect(width//2 - 170, height//2 + 72, 340, 52)
        draw_button(btn_A, (0,0,150),  (0,0,0), "RESTART (same level)", game_font_small)
        draw_button(btn_B, (100,0,0),  (0,0,0), "START OVER",           game_font_small)

        if mouse_clicked:
            if btn_A.collidepoint(mouse_pos):    # Aynı leveldan devam
                reset_game(current_level)
                draw_level_transition()
                screen_state = "playing"
            elif btn_B.collidepoint(mouse_pos):  # Baştan başla
                delete_checkpoint(player_name)
                reset_game(1)
                draw_level_transition()
                screen_state = "playing"
        clock.tick(15)

    # ======================================================
    # EKRAN: KAZANDIN
    # ======================================================
    elif screen_state == "game_won":
        screen.fill((10, 10, 50))
        t1 = game_font_big.render("YOU WIN!", True, (255,215,0))
        t2 = game_font_small.render(f"Score: {snake_length - 1}", True, (255,255,255))
        screen.blit(t1, (width//2 - t1.get_width()//2, height//2 - 80))
        screen.blit(t2, (width//2 - t2.get_width()//2, height//2 - 20))

        btn_A = pygame.Rect(width//2 - 110, height//2 + 30, 220, 50)
        draw_button(btn_A, (0,120,0), (0,0,0), "PLAY AGAIN", game_font_small)

        if mouse_clicked and btn_A.collidepoint(mouse_pos):
            reset_game(1)
            draw_level_transition()
            screen_state = "playing"
        clock.tick(15)

    pygame.display.update()

pygame.quit()
