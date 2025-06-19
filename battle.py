import pygame
import random
import os

# Initialize pygame
pygame.init()

clock = pygame.time.Clock()
fps = 60

# Game window
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Battle')

# Define game variables
current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 15
clicked = False
game_over = 0

# Define fonts
font = pygame.font.SysFont('Times New Roman', 26)

# Define colours
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
black = (0, 0, 0)

# Create placeholder images if files don't exist
def create_placeholder_surface(width, height, color, text=""):
    surface = pygame.Surface((width, height))
    surface.fill(color)
    if text:
        text_surf = font.render(text, True, black)
        text_rect = text_surf.get_rect(center=(width//2, height//2))
        surface.blit(text_surf, text_rect)
    return surface

# Load images with fallbacks
def load_image_safe(path, fallback_size=(64, 64), fallback_color=white, text=""):
    try:
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
        else:
            print(f"Image not found: {path}, using placeholder")
            return create_placeholder_surface(fallback_size[0], fallback_size[1], fallback_color, text)
    except:
        print(f"Error loading image: {path}, using placeholder")
        return create_placeholder_surface(fallback_size[0], fallback_size[1], fallback_color, text)

# Load images
background_img = load_image_safe('img/Background/background.png', (screen_width, screen_height), (100, 150, 200), "Background")
panel_img = load_image_safe('img/Icons/panel.png', (screen_width, bottom_panel), (50, 50, 50), "Panel")
potion_img = load_image_safe('img/Icons/potion.png', (64, 64), (0, 255, 0), "Potion")
restart_img = load_image_safe('img/Icons/restart.png', (120, 30), (100, 100, 100), "Restart")
victory_img = load_image_safe('img/Icons/victory.png', (300, 100), (255, 255, 0), "VICTORY!")
defeat_img = load_image_safe('img/Icons/defeat.png', (300, 100), (255, 0, 0), "DEFEAT!")
sword_img = load_image_safe('img/Icons/sword.png', (32, 32), (200, 200, 200), "⚔")

# Button class (embedded since button.py might not exist)
class Button():
    def __init__(self, surface, x, y, image, size_x, size_y):
        self.image = pygame.transform.scale(image, (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.surface = surface

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        self.surface.blit(self.image, (self.rect.x, self.rect.y))
        return action

# Draw text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Draw background
def draw_bg():
    screen.blit(background_img, (0, 0))

# Draw panel
def draw_panel():
    screen.blit(panel_img, (0, screen_height - bottom_panel))
    draw_text(f'{knight.name} HP: {knight.hp}', font, white, 100, screen_height - bottom_panel + 10)
    for count, i in enumerate(bandit_list):
        draw_text(f'{i.name} HP: {i.hp}', font, white, 550, (screen_height - bottom_panel + 10) + count * 60)

# Fighter class
class Fighter():
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # Load animations with fallbacks
        animation_names = ['Idle', 'Attack', 'Hurt', 'Death']
        frame_counts = [8, 8, 3, 10]
        
        for anim_idx, anim_name in enumerate(animation_names):
            temp_list = []
            for i in range(frame_counts[anim_idx]):
                img_path = f'img/{self.name}/{anim_name}/{i}.png'
                if os.path.exists(img_path):
                    try:
                        img = pygame.image.load(img_path)
                        img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
                        temp_list.append(img)
                    except:
                        # Create placeholder frame
                        placeholder = create_placeholder_surface(150, 150, 
                            (255, 100, 100) if name == 'Knight' else (100, 100, 255), 
                            f"{name}\n{anim_name}")
                        temp_list.append(placeholder)
                else:
                    # Create placeholder frame
                    placeholder = create_placeholder_surface(150, 150, 
                        (255, 100, 100) if name == 'Knight' else (100, 100, 255), 
                        f"{name}\n{anim_name}")
                    temp_list.append(placeholder)
            
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:  # Death animation
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        rand = random.randint(-5, 5)
        damage = max(1, self.strength + rand)  # Ensure minimum 1 damage
        target.hp -= damage
        target.hurt()
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
        damage_text_group.add(damage_text)
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def reset(self):
        self.alive = True
        self.potions = self.start_potions
        self.hp = self.max_hp
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)

# HealthBar class
class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp
        ratio = self.hp / self.max_hp if self.max_hp > 0 else 0
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))

# DamageText class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.y -= 1
        self.counter += 1
        if self.counter > 30:
            self.kill()

damage_text_group = pygame.sprite.Group()

# Create fighters
knight = Fighter(200, 260, 'Knight', 100, 10, 3)
bandit1 = Fighter(550, 270, 'Bandit', 20, 4, 1)
bandit2 = Fighter(700, 270, 'Bandit', 20, 4, 1)

bandit_list = [bandit1, bandit2]

# Health bars
knight_health_bar = HealthBar(100, screen_height - bottom_panel + 40, knight.hp, knight.max_hp)
bandit1_health_bar = HealthBar(550, screen_height - bottom_panel + 40, bandit1.hp, bandit1.max_hp)
bandit2_health_bar = HealthBar(550, screen_height - bottom_panel + 100, bandit2.hp, bandit2.max_hp)

# Buttons
potion_button = Button(screen, 100, screen_height - bottom_panel + 70, potion_img, 64, 64)
restart_button = Button(screen, 330, 120, restart_img, 120, 30)

# Game loop
run = True
while run:
    clock.tick(fps)
    
    # Draw everything
    draw_bg()
    draw_panel()
    knight_health_bar.draw(knight.hp)
    bandit1_health_bar.draw(bandit1.hp)
    bandit2_health_bar.draw(bandit2.hp)

    knight.update()
    knight.draw()
    for bandit in bandit_list:
        bandit.update()
        bandit.draw()

    damage_text_group.update()
    damage_text_group.draw(screen)

    # Reset action flags
    attack = False
    potion = False
    target = None

    # Handle mouse cursor and targeting
    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()

    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos) and bandit.alive:
            pygame.mouse.set_visible(False)
            screen.blit(sword_img, pos)
            if clicked:
                attack = True
                target = bandit

    # Handle potion button
    if potion_button.draw():
        potion = True

    # Display potion count
    draw_text(str(knight.potions), font, white, 150, screen_height - bottom_panel + 70)

    # Game logic
    if game_over == 0:
        # Player turn
        if knight.alive and current_fighter == 1:
            action_cooldown += 1
            if action_cooldown >= action_wait_time:
                if attack and target and target.alive:
                    knight.attack(target)
                    current_fighter += 1
                    action_cooldown = 0
                elif potion and knight.potions > 0:
                    heal_amount = min(potion_effect, knight.max_hp - knight.hp)
                    knight.hp += heal_amount
                    knight.potions -= 1
                    damage_text = DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), green)
                    damage_text_group.add(damage_text)
                    current_fighter += 1
                    action_cooldown = 0
        elif not knight.alive:
            game_over = -1

        # Enemy turns
        for count, bandit in enumerate(bandit_list):
            if current_fighter == 2 + count:
                if bandit.alive:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        # AI decision: heal if low health and has potions, otherwise attack
                        if (bandit.hp / bandit.max_hp) < 0.5 and bandit.potions > 0:
                            heal_amount = min(potion_effect, bandit.max_hp - bandit.hp)
                            bandit.hp += heal_amount
                            bandit.potions -= 1
                            damage_text = DamageText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), green)
                            damage_text_group.add(damage_text)
                        else:
                            bandit.attack(knight)
                        current_fighter += 1
                        action_cooldown = 0
                else:
                    current_fighter += 1

        # Reset turn counter
        if current_fighter > total_fighters:
            current_fighter = 1

    # Check win/lose conditions
    alive_bandits = sum(b.alive for b in bandit_list)
    if alive_bandits == 0:
        game_over = 1

    # Handle game over screen
    if game_over != 0:
        if game_over == 1:
            screen.blit(victory_img, (250, 50))
        if game_over == -1:
            screen.blit(defeat_img, (290, 50))
        if restart_button.draw():
            knight.reset()
            for bandit in bandit_list:
                bandit.reset()
            current_fighter = 1
            action_cooldown = 0
            game_over = 0

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False

    pygame.display.update()

pygame.quit()