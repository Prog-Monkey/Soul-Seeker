import pygame   #Importing Concepts
import random   #Random Math
import math     #Calculating Enemy Position
# Importing Keyboard Key Movement
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_UP,
    K_LEFT,
    K_RIGHT,
    K_w,
    K_a,
    K_d,
    K_x,
    KEYUP,
    MOUSEBUTTONDOWN
)

# Initialize pygame and Music
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("Music FromSoftware 2011.mp3")
pygame.mixer.music.play(loops=1001, start=10, fade_ms=100)
pygame.mixer.music.set_volume(2)

# Define constants for the screen width and height
info = pygame.display.Info()    # The users display info
screen_width = info.current_w
screen_height = info.current_h
screen_size = screen_width, screen_height #Setting the screen size
# Create the screen object
screen = pygame.display.set_mode(screen_size)
# Platform and character sizes
platform_width = 200
platform_height = 30
character_width = 50
character_height = 50

# Load the character image
player = pygame.image.load('images/Hydra.png')  # Player Image
player = pygame.transform.scale(player, (character_width, character_height))    #Player Image Setting
god = pygame.image.load("images/God.png")    #God Image
god = pygame.transform.scale(god, (character_width, character_height))    #God Image Setting
grave = pygame.image.load("images/grave_stone.png")   #Grave Image 
grave = pygame.transform.scale(grave, (character_width + 50, character_height + 50))    #Grave Image Setting
enemy = pygame.image.load("images/Reaper.png").convert_alpha()  #Enemy Image
enemy = pygame.transform.scale(enemy, (64, 64)) #Enemy Image Setting
icon = enemy    #Icon Image
icon = pygame.transform.scale(icon, (80, 50))   #Icon Image Setting
pygame.display.set_caption("Reaper Ravage")     #Setting the Name
pygame.display.set_icon(icon)   #Setting the icon 

# Define gravity and initial velocities
gravity = 0.5
jump_velocity = -12

# Load the background images
backgrounds = [
    pygame.transform.scale(pygame.image.load(f"images/background{i}.png").convert(), screen_size)
    for i in range(1, 5)
]
platform_image = pygame.image.load("images/Platform.png").convert()

backgroundGame = random.choice(backgrounds)
platform_image = pygame.image.load("images/Platform.png").convert()

# Define font and create a text surface
font1 = pygame.font.Font("fonts/Micro5-Regular.ttf", 70)
font2 = pygame.font.Font("fonts/Micro5-Regular.ttf", 50)
game_over_textE = font1.render("Sacrificed For Reaper", True, (255, 0, 0))
game_over_textG = font1.render("Forgiven By GOD", True, (255, 0, 0))
restart_text = font2.render("Press X to Restart", True, (0, 255, 20))

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image):
        super().__init__()
        
        if image:
            self.image = platform_image
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            self.image = pygame.Surface([width, height])
            self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Function to generate random platforms
def generate_random_platforms():
    platforms = pygame.sprite.Group()

    # Add platform covering the entire ground
    ground_platform = Platform(0, screen_height - platform_height, screen_width, platform_height, platform_image)
    platforms.add(ground_platform)

    # Generate random platforms
    num_platforms = random.randint(10, 15)
    for _ in range(num_platforms):
        x = random.randint(0, screen_width - platform_width)
        y = random.randint(100, screen_height - platform_height - 50)
        platform = Platform(x, y, platform_width, platform_height, "images/Platform.png")
        platforms.add(platform)

    return platforms

# Create initial platforms
platforms = generate_random_platforms()

# Custom Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity_x = 0
        self.velocity_y = 0

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y


# enemy AI class


# enemy AI class
class enemyAI(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity_x = 0
        self.velocity_y = 0
        self.touching_platform = False
        self.touching_platform_timer = 0
        self.phase_platform = False

    def update(self, player, platforms):
        # Calculate distance and direction towards player
        dist_x = player.rect.centerx - self.rect.centerx
        dist_y = player.rect.centery - self.rect.centery
        distance = math.hypot(dist_x, dist_y)

        # Normalize the direction
        if distance != 0:
            dx = dist_x / distance
            dy = dist_y / distance
        else:
            dx, dy = 0, 0

        # Set enemy speed
        enemy_speed = 4.5

        # Move towards the player
        self.velocity_x = dx * enemy_speed
        self.velocity_y = dy * enemy_speed

        # Update position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Check for collision with platforms
        self.check_platforms_collision(platforms)

        # Check for collision with player
        if self.rect.colliderect(player.rect):
            player_life = False

    def check_platforms_collision(self, platforms):
        # Check if the enemy is touching a platform
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        if collisions:
            self.touching_platform = True
            self.touching_platform_timer += 1
            if self.touching_platform_timer >= 200:  # 3 seconds (60 frames per second)    
                for platform in collisions:
                    platforms.remove(platform)
                    self.phase_platform = True
        else:
            self.touching_platform = False
            self.touching_platform_timer = 0

        # If enemy is phasing through platforms, stop phasing after a while
        if self.phase_platform:
            self.touching_platform_timer += 1
            if self.touching_platform_timer >= 180:  # 3 seconds (60 frames per second)
                self.phase_platform = False
                self.touching_platform_timer = 0



player_sprite = Player(player, screen_width // 2, screen_height // 2)
enemy_sprite = enemyAI(enemy, screen_width // 4, screen_height // 2)
player_life = True
player_won = False
running = True

# Define menu variables
menu_font = pygame.font.Font("fonts/StalinistOne-Regular.ttf", 48)
font_copyright = pygame.font.Font("fonts/StalinistOne-Regular.ttf", 10)
font_owner = pygame.font.Font(None, 30)
play_text = menu_font.render("Play", True, (255, 255, 255))
play_rect = play_text.get_rect(center=(screen_width // 2, screen_height // 2))
title_text = menu_font.render("REAPER RAVAGE", True, (255, 0, 0))
title_rect = play_text.get_rect(center=(350, screen_height // 7))
menu_background = pygame.image.load("images/Game_Menu.png")
menu_background = pygame.transform.scale(menu_background, (screen_width, screen_height))
menu_rect = menu_background.get_rect(center=(screen_width//2,screen_height//2))
copyright_text = font_copyright.render("Composer: Motoi Sakuraba Track #22 Japanese Collector's Edition of Dark Souls ©2011 FromSoftware", True, (255, 255, 255))
copyright_rect = copyright_text.get_rect(center=(500,630))
owner_text = font_owner.render("made by the champion", True, (255, 255, 255))
owner_rect = owner_text.get_rect(center=(screen_width//2,400))
# Menu loop
menu_running = True
while menu_running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.type == QUIT:
                menu_running = False
                running = False
            elif event.key == K_ESCAPE:
                menu_running = False
                running = False
        elif event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if play_rect.collidepoint(mouse_pos):
                menu_running = False
                clock = pygame.time.Clock()
                start_ticks = pygame.time.get_ticks()  # Get the current time in milliseconds
                countdown_seconds = 20
    
    screen.blit(menu_background,menu_rect)
    screen.blit(copyright_text, copyright_rect)
    screen.blit(owner_text, owner_rect)
    screen.blit(play_text, play_rect)
    screen.blit(title_text,title_rect)
   
    pygame.display.flip()

# Main game loop
while running and not menu_running:
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN and not player_won and player_life:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_LEFT:
                player_sprite.velocity_x = -9
            elif event.key == K_RIGHT:
                player_sprite.velocity_x = 9
            elif event.key == K_UP and not jumping_player:
                jumping_player = True
                player_sprite.velocity_y = jump_velocity

           
        elif event.type == KEYUP:
            if event.key == K_LEFT or event.key == K_RIGHT:
                player_sprite.velocity_x = 0
          
        # Check for key press to restart the game
        if event.type == KEYDOWN and event.key == K_x and not player_life:
            # Reset the game
            player_sprite.rect.center = (screen_width // 2, screen_height // 2)
            enemy_sprite.rect.center = (screen_width // 7, enemy_sprite.rect.width // 2)
            player_life = True
            player_won = False
            jumping_player = False
            jumping_enemy = False
            player_sprite.image = player  # Change player back to player image
            enemy_sprite.image = enemy  # Change enemy back to enemy image
            background = random.randint(0,5)
            if background == 1:
                backgroundGame = pygame.transform.scale(backgrounds[0], screen_size)
                platform_image = pygame.image.load("images/Platform.png").convert()
            elif background==2:
                backgroundGame = pygame.transform.scale(backgrounds[1], screen_size)
                platform_image = pygame.image.load("images/Platform.png").convert()
            elif background==3:
                backgroundGame = pygame.transform.scale(backgrounds[2], screen_size)
                platform_image = pygame.image.load("images/Platform.png").convert()
            elif background==4:
                backgroundGame = pygame.transform.scale(backgrounds[3], screen_size)
                platform_image = pygame.image.load("images/Platform1.png").convert_alpha()
            platforms = generate_random_platforms()
            start_ticks = pygame.time.get_ticks()  # Reset the timer
        if event.type == KEYDOWN and event.key == K_x and player_won:
            # Reset the game
            player_sprite.rect.center = (screen_width // 2, screen_height // 2)
            enemy_sprite.rect.center = (screen_width // 7, enemy_sprite.rect.width // 2)
            player_life = True
            player_won = False
            jumping_player = False
            jumping_enemy = False
            player_sprite.image = player  # Change player back to player image
            enemy_sprite.image = enemy  # Change enemy back to enemy image
            background = random.randint(0,5)
            if background == 1:
                backgroundGame = pygame.transform.scale(backgrounds[0], screen_size)
                platform_image = pygame.image.load("images/Platform.png").convert_alpha()
            elif background==2:
                backgroundGame = pygame.transform.scale(backgrounds[1], screen_size)
                platform_image = pygame.image.load("images/Platform.png").convert_alpha()
            elif background==3:
                backgroundGame = pygame.transform.scale(backgrounds[2], screen_size)
                platform_image = pygame.image.load("images/Platform.png").convert_alpha()
            elif background==4:
                backgroundGame = pygame.transform.scale(backgrounds[3], screen_size)
                platform_image = pygame.image.load("images/Platform1.png").convert_alpha()
            platforms = generate_random_platforms()
            start_ticks = pygame.time.get_ticks()  # Reset the timer

    if not player_won and player_life:
        elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000

        # Calculate remaining time
        remaining_seconds = countdown_seconds - elapsed_seconds

        if remaining_seconds <= 0:
            remaining_seconds = 0  # Stop the timer from going negative
            player_won = True  # player wins after 30 seconds

    # Apply gravity to player and enemy
    player_sprite.velocity_y += gravity
    enemy_sprite.velocity_y += gravity

    # Update player positions
    if not player_won and player_life:
        player_sprite.update()
    
        enemy_sprite.update(player_sprite,platforms)

    # Check for collisions with platforms
    player_collided_platforms = pygame.sprite.spritecollide(player_sprite, platforms, False)
    for platform in player_collided_platforms:
        if player_sprite.velocity_y > 0:  # Check if player is moving downwards
            player_sprite.rect.bottom = platform.rect.top  # Set player bottom to top of platform
            player_sprite.velocity_y = 0  # Stop player vertical movement
            jumping_player = False  # player is no longer jumping
        elif player_sprite.velocity_y < 0:  # Check if player is moving upwards
            player_sprite.rect.top = platform.rect.bottom  # Set player top to bottom of platform
            player_sprite.velocity_y = 0  # Stop player vertical movement

    enemy_collided_platforms = pygame.sprite.spritecollide(enemy_sprite, platforms, False)
    for platform in enemy_collided_platforms:
        if enemy_sprite.velocity_y > 0:  # Check if enemy is moving downwards
            enemy_sprite.rect.bottom = platform.rect.top  # Set enemy's bottom to top of platform
            enemy_sprite.velocity_y = 0  # Stop enemy's vertical movement
            jumping_enemy = False  # enemy is no longer jumping
        elif enemy_sprite.velocity_y < 0:  # Check if enemy is moving upwards
            enemy_sprite.rect.top = platform.rect.bottom  # Set enemy's top to bottom of platform
            enemy_sprite.velocity_y = 0  # Stop enemy's vertical movement

    # Limit the player and enemy within the screen boundaries
    player_sprite.rect.x = max(0, min(player_sprite.rect.x, screen_width - player_sprite.rect.width))
    player_sprite.rect.y = max(0, min(player_sprite.rect.y, screen_height - player_sprite.rect.height))

    enemy_sprite.rect.x = max(0, min(enemy_sprite.rect.x, screen_width - enemy_sprite.rect.width))
    enemy_sprite.rect.y = max(0, min(enemy_sprite.rect.y, screen_height - enemy_sprite.rect.height))

    # Fill the screen with the background color
    screen.blit(backgroundGame, (0, 0))

    # Blit the platforms
    for platform in platforms:
        screen.blit(platform.image, platform.rect)

    # Blit the characters
    screen.blit(player_sprite.image, player_sprite.rect)
    
    screen.blit(enemy_sprite.image, enemy_sprite.rect)

    if player_sprite.rect.colliderect(enemy_sprite.rect):
        player_life = False

    # Display "Game Over" text if player is dead
    if not player_life:
        screen.blit(grave, player_sprite.rect)  # Change player to grave image
        player_sprite.image = grave  # Blit grave image

        game_over_rect = game_over_textE.get_rect(center=(screen_width // 2, screen_height // 2 - 30))
        screen.blit(game_over_textE, game_over_rect)

        restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 30))
        screen.blit(restart_text, restart_rect)
        
    if player_won:
        player_sprite.image = god  # Change player image to god

        god_rect = god.get_rect(center=player_sprite.rect.center)
        screen.blit(god, god_rect)  # Blit reaper image

        game_over_rect = game_over_textG.get_rect(center=(screen_width // 2, screen_height // 2 - 30))
        screen.blit(game_over_textG, game_over_rect)

        restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 30))
        screen.blit(restart_text, restart_rect)
      
    timer_text = font2.render(f"Time: {remaining_seconds}", True, (255, 255, 255))
    screen.blit(timer_text, (10, 10))
    # Update the display
    pygame.display.update()

    # Cap the frame rate
    clock.tick(60)
    

pygame.quit() 