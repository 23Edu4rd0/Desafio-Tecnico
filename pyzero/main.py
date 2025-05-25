from pygame import Rect as PygameRect
import pgzrun

TILE_SIZE = 18

class TileMap:
    def __init__(self):
        self.width = 50
        self.height = 35
        self.tiles = [[0] * self.width for _ in range(self.height)]
        for x in range(self.width):
            self.tiles[31][x] = 1
            self.tiles[32][x] = 1
            self.tiles[33][x] = 1
        platforms = [
            (28, 8, 12),
            (25, 20, 10),
            (22, 30, 8),
            (19, 18, 7),
            (16, 24, 8),
            (13, 35, 9),
            (10, 25, 8),
            (7, 10, 12),
            (4, 2, 10)
        ]
        for y, x_start, length in platforms:
            for x in range(x_start, min(x_start + length, self.width)):
                self.tiles[y][x] = 1

    def draw(self):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile == 1:
                    tile_actor = Actor('floor_18x18')
                    tile_actor.x = x * TILE_SIZE + TILE_SIZE // 2
                    tile_actor.y = y * TILE_SIZE + TILE_SIZE // 2
                    tile_actor.draw()
                elif tile == 3:
                    screen.draw.filled_rect(Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), (100, 100, 200))

class Player:
    def __init__(self, tilemap):
        self.actor = Actor('person_indie1')
        self.actor.x = 2 * TILE_SIZE + TILE_SIZE // 2
        self.actor.y = 26 * TILE_SIZE - TILE_SIZE // 2
        self.is_jumping = False
        self.jump_height = 60
        self.velocity_y = 0
        self.facing_left = False
        self.tilemap = tilemap
        self.attack_frames_right = [f'person_attack{i}' for i in range(1, 7)]
        self.attack_frames_left = [f'person_attack{i}_right' for i in range(1, 7)]
        self.idle_frames_right = [f'person_indie{i}' for i in range(1, 8)]
        self.idle_frames_left = [f'person_indie{i}_right' for i in range(1, 8)]
        self.jump_frames_right = [f'person_jump{i}' for i in range(1, 6)]
        self.jump_frames_left = [f'person_jump{i}_right' for i in range(1, 6)]
        self.run_frames_right = [f'person_run{i}' for i in range(1, 9)]
        self.run_frames_left = [f'person_run{i}_right' for i in range(1, 9)]
        self.attack_index = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.idle_index = 0
        self.idle_timer = 0
        self.run_index = 0
        self.run_timer = 0
        self.indie_index = 0
        self.is_indie = False
        self.indie_timer = 0

    def jump(self):
        if game.won or game.lost:
            return
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = -self.jump_height
            sounds.jump.play()

    def move(self):
        tile_x_left = int((self.actor.x - TILE_SIZE // 2) // TILE_SIZE)
        tile_x_right = int((self.actor.x + TILE_SIZE // 2 - 1) // TILE_SIZE)
        tile_y = int(self.actor.y // TILE_SIZE)
        if keyboard.left:
            next_x = self.actor.x - 5
            next_tile_x_left = int((next_x - TILE_SIZE // 2) // TILE_SIZE)
            next_tile_x_right = int((next_x + TILE_SIZE // 2 - 1) // TILE_SIZE)
            if (next_tile_x_left >= 0 and next_tile_x_right < len(self.tilemap.tiles[0]) and self.tilemap.tiles[tile_y][next_tile_x_left] not in (1, 3) and self.tilemap.tiles[tile_y][next_tile_x_right] not in (1, 3)):
                self.actor.x = next_x
            self.facing_left = True
        if keyboard.right:
            next_x = self.actor.x + 5
            next_tile_x_left = int((next_x - TILE_SIZE // 2) // TILE_SIZE)
            next_tile_x_right = int((next_x + TILE_SIZE // 2 - 1) // TILE_SIZE)
            if (next_tile_x_left >= 0 and next_tile_x_right < len(self.tilemap.tiles[0]) and self.tilemap.tiles[tile_y][next_tile_x_left] not in (1, 3) and self.tilemap.tiles[tile_y][next_tile_x_right] not in (1, 3)):
                self.actor.x = next_x
            self.facing_left = False
        if keyboard.space and not self.is_jumping:
            self.jump()
        self.velocity_y += 3
        next_y = self.actor.y + self.velocity_y * 0.2
        if self.velocity_y > 0:
            below_y = int((next_y + TILE_SIZE - 1) // TILE_SIZE)
            if below_y < len(self.tilemap.tiles):
                if (self.tilemap.tiles[below_y][tile_x_left] in (1, 3) or self.tilemap.tiles[below_y][tile_x_right] in (1, 3)):
                    self.actor.y = below_y * TILE_SIZE - (TILE_SIZE // 2)
                    self.velocity_y = 0
                    self.is_jumping = False
                else:
                    self.actor.y = next_y
            else:
                self.actor.y = next_y
        elif self.velocity_y < 0:
            above_y = int(next_y // TILE_SIZE)
            if above_y >= 0:
                if (self.tilemap.tiles[above_y][tile_x_left] in (1, 3) or self.tilemap.tiles[above_y][tile_x_right] in (1, 3)):
                    self.actor.y = (above_y + 1) * TILE_SIZE
                    self.velocity_y = 0
                else:
                    self.actor.y = next_y
            else:
                self.actor.y = next_y
        else:
            self.actor.y = next_y
        if self.actor.y < self.actor.height // 2:
            self.actor.y = self.actor.height // 2

    def attack(self):
        if game.won or game.lost:
            return
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_index = 0
            self.attack_timer = 0
            self.actor.image = self.get_attack_frames()[0]
            sounds.attack.play()

    def get_attack_rect(self):
        if self.facing_left:
            return Rect(self.actor.x - 40, self.actor.y - 20, 40, 40)
        else:
            return Rect(self.actor.x, self.actor.y - 20, 40, 40)

    def indie(self):
        if not self.is_indie:
            self.is_indie = True
            self.indie_index = 0
            self.indie_timer = 0
            self.actor.image = self.get_idle_frames()[0]

    def get_idle_frames(self):
        return self.idle_frames_left if self.facing_left else self.idle_frames_right

    def get_jump_frames(self):
        return self.jump_frames_left if self.facing_left else self.jump_frames_right

    def get_attack_frames(self):
        return self.attack_frames_left if self.facing_left else self.attack_frames_right

    def get_run_frames(self):
        return self.run_frames_left if self.facing_left else self.run_frames_right

    def update(self, enemies=None):
        self.move()
        if self.is_jumping:
            self.actor.image = self.get_jump_frames()[0]
        elif self.is_attacking:
            self.attack_timer += 1
            if self.attack_timer % 5 == 0:
                self.attack_index += 1
                frames = self.get_attack_frames()
                if self.attack_index >= len(frames):
                    self.is_attacking = False
                    self.attack_index = 0
                    self.actor.image = self.get_idle_frames()[self.idle_index]
                else:
                    self.actor.image = frames[self.attack_index]
            if enemies:
                attack_rect = self.get_attack_rect()
                for enemy in enemies:
                    if enemy.alive and not enemy.hurting:
                        enemy_rect = PygameRect(enemy.actor.x - enemy.actor.width // 2, enemy.actor.y - enemy.actor.height // 2, enemy.actor.width, enemy.actor.height)
                        if attack_rect.colliderect(enemy_rect):
                            overlap = attack_rect.clip(enemy_rect)
                            if overlap.width > 0 and overlap.height > 0:
                                enemy.hurt()
        elif self.is_indie:
            self.indie_timer += 1
            if self.indie_timer % 5 == 0:
                self.indie_index += 1
                frames = self.get_idle_frames()
                if self.indie_index >= len(frames):
                    self.is_indie = False
                    self.indie_index = 0
                    self.actor.image = frames[self.idle_index]
                else:
                    self.actor.image = frames[self.indie_index]
        elif keyboard.left or keyboard.right:
            self.run_timer += 1
            if self.run_timer % 5 == 0:
                self.run_index = (self.run_index + 1) % len(self.get_run_frames())
                self.actor.image = self.get_run_frames()[self.run_index]
        else:
            self.idle_timer += 1
            if self.idle_timer % 7 == 0:
                self.idle_index = (self.idle_index + 1) % len(self.get_idle_frames())
                self.actor.image = self.get_idle_frames()[self.idle_index]

    def draw(self):
        self.actor.draw()

    def on_key_down(self, key):
        if key == keys.SPACE:
            if not self.is_jumping:
                self.jump()
        elif key == keys.A:
            self.attack()

class Enemy:
    def __init__(self, x, y, tilemap):
        self.walk_frames = [f'enemy_walk{i}_right' for i in range(1, 5)]
        self.hurt_frames = [f'enemy_hurt{i}_right' for i in range(1, 5)]
        self.walk_index = 0
        self.walk_timer = 0
        self.hurt_index = 0
        self.hurt_timer = 0
        self.actor = Actor(self.walk_frames[0])
        self.actor.x = x
        self.actor.y = y
        self.direction = 1
        self.alive = True
        self.hurting = False
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        while tile_y < len(tilemap.tiles) and tilemap.tiles[tile_y][tile_x] != 1:
            tile_y += 1
        self.platform_y = tile_y
        x_min = tile_x
        while x_min > 0 and tilemap.tiles[self.platform_y][x_min - 1] == 1:
            x_min -= 1
        x_max = tile_x
        while x_max < tilemap.width - 1 and tilemap.tiles[self.platform_y][x_max + 1] == 1:
            x_max += 1
        self.x_min = x_min * TILE_SIZE + TILE_SIZE // 2
        self.x_max = x_max * TILE_SIZE + TILE_SIZE // 2
        self.actor.y = self.platform_y * TILE_SIZE - TILE_SIZE // 2 - 14

    def update(self):
        if not self.alive and not self.hurting:
            return
        if self.hurting:
            self.hurt_timer += 1
            if self.hurt_timer % 7 == 0:
                self.hurt_index += 1
                if self.hurt_index >= len(self.hurt_frames):
                    self.hurting = False
                    self.alive = False
                else:
                    self.actor.image = self.hurt_frames[self.hurt_index]
            return
        self.actor.x += self.direction * 2
        if self.actor.x < self.x_min:
            self.actor.x = self.x_min
            self.direction = 1
            self.walk_frames = [f'enemy_walk{i}_right' for i in range(1, 5)]
            self.hurt_frames = [f'enemy_hurt{i}_right' for i in range(1, 5)]
        if self.actor.x > self.x_max:
            self.actor.x = self.x_max
            self.direction = -1
            self.walk_frames = [f'enemy_walk{i}' for i in range(1, 5)]
            self.hurt_frames = [f'enemy_hurt{i}' for i in range(1, 5)]
        self.walk_timer += 1
        if self.walk_timer % 7 == 0:
            self.walk_index = (self.walk_index + 1) % len(self.walk_frames)
            self.actor.image = self.walk_frames[self.walk_index]

    def hurt(self):
        if self.alive and not self.hurting:
            self.hurting = True
            self.hurt_index = 0
            self.hurt_timer = 0
            self.actor.image = self.hurt_frames[0]

    def draw(self):
        if self.alive or self.hurting:
            self.actor.draw()

class Coin:
    def __init__(self, x, y):
        self.frames = [f'coin_frame{i}' for i in range(1, 5)]
        self.frame_index = 0
        self.frame_timer = 0
        self.actor = Actor(self.frames[self.frame_index])
        self.actor.x = x
        self.actor.y = y
        self.collected = False

    def update(self, player):
        if self.collected:
            return
        self.frame_timer += 1
        if self.frame_timer % 10 == 0:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.actor.image = self.frames[self.frame_index]
        if self.actor.colliderect(player.actor):
            self.collected = True

    def draw(self):
        if not self.collected:
            self.actor.draw()

class UI:
    def __init__(self, game):
        self.game = game
        self.show_start_screen = True
        self.music_on = False

    def draw(self):
        if self.show_start_screen:
            screen.fill((0, 0, 0))
            screen.draw.text("Dragon Hunter", center=(400, 150), fontsize=60, color=(255, 255, 255))
            screen.draw.filled_rect(Rect(300, 250, 200, 60), (50, 50, 50))
            screen.draw.text("Play", center=(400, 280), fontsize=32, color=(0, 255, 0))
            screen.draw.filled_rect(Rect(300, 330, 200, 60), (50, 50, 50))
            screen.draw.text("Toggle Music", center=(400, 360), fontsize=32, color=(255, 255, 0))
            screen.draw.filled_rect(Rect(300, 410, 200, 60), (50, 50, 50))
            screen.draw.text("Exit", center=(400, 440), fontsize=32, color=(255, 0, 0))
        elif self.game.win_message:
            screen.fill((0, 0, 0))
            screen.draw.text(self.game.win_message, center=(400, 200), fontsize=60, color=(255, 255, 255))
            screen.draw.filled_rect(Rect(300, 300, 200, 60), (50, 50, 50))
            screen.draw.text("Exit", center=(400, 330), fontsize=32, color=(255, 255, 255))
        elif self.game.lost:
            screen.fill((0, 0, 0))
            screen.draw.text("You lost!", center=(400, 200), fontsize=60, color=(255, 255, 255))
            screen.draw.filled_rect(Rect(300, 300, 200, 60), (50, 50, 50))
            screen.draw.text("Exit", center=(400, 330), fontsize=32, color=(255, 255, 255))

    def on_mouse_down(self, pos):
        x, y = pos
        if self.show_start_screen:
            if 300 <= x <= 500 and 250 <= y <= 310:
                self.show_start_screen = False
            elif 300 <= x <= 500 and 330 <= y <= 390:
                self.music_on = not self.music_on
                if self.music_on:
                    music.play("bgmusic")
                else:
                    music.stop()
            elif 300 <= x <= 500 and 410 <= y <= 470:
                exit()
        elif self.game.win_message or self.game.lost:
            if 300 <= x <= 500 and 300 <= y <= 360:
                exit()

class Game:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.tilemap = TileMap()
        self.player = Player(self.tilemap)
        self.coin = Coin(5 * TILE_SIZE + TILE_SIZE // 2, 3 * TILE_SIZE - 10)
        self.enemies = [
            Enemy(9 * TILE_SIZE + TILE_SIZE // 2, 28 * TILE_SIZE - TILE_SIZE // 2 - 14, self.tilemap),
            Enemy(36 * TILE_SIZE + TILE_SIZE // 2, 13 * TILE_SIZE - TILE_SIZE // 2 - 14, self.tilemap),
            Enemy(11 * TILE_SIZE + TILE_SIZE // 2, 7 * TILE_SIZE - TILE_SIZE // 2 - 14, self.tilemap)
        ]
        self.win_message = ""
        self.lost = False
        self.won = False
        self.ui = UI(self)

    def update(self):
        if self.ui.show_start_screen:
            return
        self.player.update(self.enemies)
        self.coin.update(self.player)
        for enemy in self.enemies:
            enemy.update()
        if self.coin.collected:
            self.won = True
            self.win_message = "You won!"
        for enemy in self.enemies:
            if enemy.alive and not enemy.hurting:
                player_hitbox = PygameRect(
                    self.player.actor.x - self.player.actor.width // 4,
                    self.player.actor.y - self.player.actor.height // 4,
                    self.player.actor.width // 2,
                    self.player.actor.height // 2
                )
                enemy_hitbox = PygameRect(
                    enemy.actor.x - enemy.actor.width // 4,
                    enemy.actor.y - enemy.actor.height // 4,
                    enemy.actor.width // 2,
                    enemy.actor.height // 2
                )
                if player_hitbox.colliderect(enemy_hitbox):
                    self.lost = True
                    self.win_message = "You lost!"
        if self.won or self.lost:
            music.stop()

    def draw(self):
        screen.clear()
        if not self.ui.show_start_screen:
            self.tilemap.draw()
            self.player.draw()
            for enemy in self.enemies:
                enemy.draw()
            self.coin.draw()
        self.ui.draw()

    def on_key_down(self, key):
        if self.ui.show_start_screen or (self.won or self.lost):
            return
        self.player.on_key_down(key)

game = Game()

def update():
    game.update()

def draw():
    game.draw()

def on_key_down(key):
    game.on_key_down(key)

def on_mouse_down(pos):
    game.ui.on_mouse_down(pos)

pgzrun.go()