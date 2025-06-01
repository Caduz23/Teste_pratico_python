import pgzrun
from pygame import Rect

# Constantes do jogo
WIDTH = 800
HEIGHT = 600
TITLE = "Pixel Adventurer"
GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 5

# Estados do jogo
MENU = 0
PLAYING = 1
VICTORY = 2
game_state = MENU

# Controle de som e música
sound_on = True

class AnimatedSprite:
    def __init__(self, images, animation_speed=0.1):
        self.images = images
        self.current_image = 0
        self.animation_speed = animation_speed
        self.animation_time = 0

    def update(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_image = (self.current_image + 1) % len(self.images)

    def draw(self, x, y):
        img = self.images[self.current_image]
        screen.blit(img, (x, y))

class Player:
    def __init__(self, x, y):
        self.idle_right = ["hero_idle1", "hero_idle2"]
        self.run_right = ["hero_walk1", "hero_walk2"]
        self.jump_right = ["hero_idle1"]

        self.idle_left = ["hero_idle_left1", "hero_idle_left2"]
        self.run_left = ["hero_walk_left1", "hero_walk_left2"]
        self.jump_left = ["hero_idle_left1"]

        self.animation = AnimatedSprite(self.idle_right, 0.2)
        self.current_state = "idle"
        self.facing_right = True

        self.rect = Rect(x, y, 50, 27)
        self.prev_rect = self.rect.copy()
        self.velocity_y = 0
        self.on_ground = False

    def update(self, dt):
        self.prev_rect = self.rect.copy()

        if keyboard.left:
            self.rect.x -= PLAYER_SPEED
            self.facing_right = False
            if self.on_ground:
                self.current_state = "run"
        elif keyboard.right:
            self.rect.x += PLAYER_SPEED
            self.facing_right = True
            if self.on_ground:
                self.current_state = "run"
        else:
            if self.on_ground:
                self.current_state = "idle"

        if keyboard.space and self.on_ground:
            self.velocity_y = JUMP_STRENGTH
            self.on_ground = False
            self.current_state = "jump"
            if sound_on:
                sounds.jump.play()

        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Colisão com chão
        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.velocity_y = 0
            self.on_ground = True

        # Colisão com plataformas (corrigido com verificação da posição anterior)
        for platform in platforms:
            if self.rect.colliderect(platform) and self.velocity_y >= 0:
                if self.prev_rect.bottom <= platform.top:
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.on_ground = True

        # Limitar dentro da tela horizontalmente
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.current_state == "idle":
            frames = self.idle_right if self.facing_right else self.idle_left
        elif self.current_state == "run":
            frames = self.run_right if self.facing_right else self.run_left
        else:
            frames = self.jump_right if self.facing_right else self.jump_left

        if self.animation.images != frames:
            self.animation.images = frames
            self.animation.current_image = 0
            self.animation.animation_time = 0

        self.animation.update(dt)

    def draw(self):
        self.animation.draw(self.rect.x, self.rect.y)

class Enemy:
    def __init__(self, x, y, patrol_range=100):
        self.frames = ["enemy1", "enemy2"]
        self.animation = AnimatedSprite(self.frames, 0.15)
        self.rect = Rect(x, y, 50, 50)
        self.start_x = x
        self.patrol_range = patrol_range
        self.direction = 1
        self.speed = 2

    def update(self, dt):
        self.rect.x += self.speed * self.direction
        if abs(self.rect.x - self.start_x) > self.patrol_range:
            self.direction *= -1
        self.animation.update(dt)

    def draw(self):
        self.animation.draw(self.rect.x, self.rect.y)

class Coin:
    def __init__(self, x, y):
        self.image = "coin"
        self.rect = Rect(x, y, 20, 20)
        self.collected = False

    def draw(self):
        if not self.collected:
            screen.blit(self.image, (self.rect.x, self.rect.y))

class Button:
    def __init__(self, x, y, text, action):
        self.rect = Rect(x, y, 200, 50)
        self.text = text
        self.action = action
        self.color = (100, 100, 200)
        self.hover_color = (150, 150, 250)

    def draw(self):
        color = self.hover_color if self.is_hovered() else self.color
        screen.draw.filled_rect(self.rect, color)
        screen.draw.text(
            self.text,
            center=self.rect.center,
            fontsize=30,
            color="white"
        )

    def is_hovered(self):
        return self.rect.collidepoint(mouse_pos)

    def check_click(self):
        if self.is_hovered():
            return self.action
        return None

def toggle_sound():
    global sound_on
    sound_on = not sound_on
    buttons[1].text = f"Sound: {'ON' if sound_on else 'OFF'}"
    if sound_on:
        music.play("background_music")
    else:
        music.stop()

def set_game_state(state):
    global game_state
    game_state = state

def return_to_menu():
    global coin_count, coins, player
    for coin in coins:
        coin.collected = False
    coin_count = 0
    player.rect.x = 100
    player.rect.y = HEIGHT - 77
    player.velocity_y = 0
    player.on_ground = False
    set_game_state(MENU)

player = Player(100, HEIGHT - 77)
enemies = [
    Enemy(300, HEIGHT - 65, 150),
    Enemy(600, HEIGHT - 65, 100)
]
platforms = [
    Rect(200, 450, 100, 20),
    Rect(400, 400, 100, 20),
    Rect(600, 450, 100, 20)
]
coins = [
    Coin(210, 420),
    Coin(410, 370),
    Coin(610, 420)
]
coin_count = 0

buttons = [
    Button(WIDTH//2 - 100, 200, "Start Game", lambda: set_game_state(PLAYING)),
    Button(WIDTH//2 - 100, 280, "Sound: ON", toggle_sound),
    Button(WIDTH//2 - 100, 360, "Exit", exit)
]

victory_buttons = [
    Button(WIDTH//2 - 100, 300, "Voltar ao Menu", return_to_menu)
]

mouse_pos = (0, 0)

# Som e música
sound_on = True
music.set_volume(0.3)
music.play("background_music")

def set_victory_state():
    set_game_state(VICTORY)

def update(dt):
    global coin_count
    if game_state == PLAYING:
        player.update(dt)
        for enemy in enemies:
            enemy.update(dt)
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                if sound_on:
                    sounds.hit.play()
                player.rect.x = 100
                player.rect.y = HEIGHT - 77
        for coin in coins:
            if player.rect.colliderect(coin.rect) and not coin.collected:
                if sound_on:
                    sounds.coin.play()
                coin.collected = True
                coin_count += 1

        if all(coin.collected for coin in coins):
            clock.schedule(set_victory_state, 0.1)

def draw():
    screen.fill((50, 50, 80))
    if game_state == MENU:
        screen.draw.text(
            TITLE,
            center=(WIDTH//2, 100),
            fontsize=60,
            color="white"
        )
        for button in buttons:
            button.draw()
    elif game_state == PLAYING:
        for platform in platforms:
            screen.draw.filled_rect(platform, (100, 200, 100))
        screen.draw.filled_rect(Rect(0, HEIGHT - 50, WIDTH, 50), (150, 100, 50))
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for coin in coins:
            coin.draw()
        screen.draw.text(
            "Moedas: " + str(coin_count),
            (10, 40),
            color="yellow"
        )
        screen.draw.text(
            "Use as setinhas para se mover e espaço para pular",
            (10, 10),
            color="white"
        )
    elif game_state == VICTORY:
        screen.fill((30, 120, 60))
        screen.draw.text(
            "Você venceu!",
            center=(WIDTH//2, 150),
            fontsize=60,
            color="white"
        )
        for button in victory_buttons:
            button.draw()

def on_mouse_move(pos):
    global mouse_pos
    mouse_pos = pos

def on_mouse_down(pos):
    if game_state == MENU:
        for button in buttons:
            if button.rect.collidepoint(pos):
                action = button.check_click()
                if action:
                    action()
    elif game_state == VICTORY:
        for button in victory_buttons:
            if button.rect.collidepoint(pos):
                action = button.check_click()
                if action:
                    action()

pgzrun.go()
