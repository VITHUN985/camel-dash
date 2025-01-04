import pygame
import sys
import random
from PIL import Image

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()

# Screen dimensions and settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Camel Dash Enhanced")

# Load assets (ground, air obstacle, player images, etc.)
ground_tile = pygame.image.load("images/ground_tile.png").convert_alpha()
ground_obstacle_img = pygame.image.load("images/ground_obstacle.png").convert_alpha()
air_obstacle_img = pygame.image.load("images/air_obstacle.png").convert_alpha()
player_img = pygame.image.load("images/player.png").convert_alpha()

# Game settings
GROUND_Y = SCREEN_HEIGHT - ground_tile.get_height()
gravity = 0.75
jump_strength = -7
obstacle_speed = 7
min_distance_between_obstacles = 200
obstacle_spacing_variation = 100

# Define a slower frame delay for the paused background GIF
pause_background_frame_delay = 100  # Slower movement, adjust as needed
pause_frame_counter = 0

# Load and prepare GIF frames for the menu and history backgrounds
gif_path = "images/menu_background.gif"
gif = Image.open(gif_path)
background_frames = []
for frame in range(gif.n_frames):
    gif.seek(frame)
    frame_surface = pygame.image.fromstring(gif.tobytes(), gif.size, gif.mode).convert()
    background_frames.append(pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT)))
current_frame = 0
background_frame_delay = 75
frame_counter = 0

# Load and prepare GIF frames for the game background (separate from menu)
game_gif_path = "images/game_background.gif"  # Path to the game background GIF
game_gif = Image.open(game_gif_path)
game_background_frames = []
for frame in range(game_gif.n_frames):
    game_gif.seek(frame)
    frame_surface = pygame.image.fromstring(game_gif.tobytes(), game_gif.size, game_gif.mode).convert()
    game_background_frames.append(pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT)))
game_current_frame = 0
game_frame_counter = 0
game_background_frame_delay = 5  # Adjust this delay as needed

# Font and Colors
font = pygame.font.Font("fonts/Pixelated Bold Shiny.TTF", 20)
white = (255, 255, 255)
fonts = pygame.font.Font("fonts/Mario-Kart-DS.ttf", 50)
yellow = (211, 169, 108)

# Load sounds
menu_music = pygame.mixer.Sound("sounds/menu_sound.mp3")
jump_sound = pygame.mixer.Sound("sounds/jump.wav")
game_music = pygame.mixer.Sound("sounds/game_music.mp3")
click_sound= pygame.mixer.Sound("sounds/click.wav")
hit_sound= pygame.mixer.Sound("sounds/hit.wav")

# Set initial volume for both music tracks
menu_music.set_volume(0.5)
game_music.set_volume(0.5)
jump_sound.set_volume(0.2)
click_sound.set_volume(0.2)
hit_sound.set_volume(0.2)

# Function to fade out the current music and fade in the new one
def smooth_transition(from_music, to_music, duration=1000):
    from_music.fadeout(duration)
    pygame.time.delay(duration)
    to_music.play(loops=-1)
    to_music.set_volume(0)

    for i in range(0, 11):
        to_music.set_volume(i / 10)
        pygame.time.delay(duration // 10)

# Game state variables
game_active = False
game_paused = False
running = True
score = 0

# Player settings
player_x = 25
player_y = GROUND_Y - player_img.get_height()
player_velocity_y = 0
is_jumping = False

# Obstacle lists
ground_obstacles = []
air_obstacles = []

# History file path
history_file = "history.txt"

# Function to save score to history file
def save_score(score):
    with open(history_file, "a") as file:
        file.write(f"{score}\n")

# Function to read history scores
def read_history():
    try:
        with open(history_file, "r") as file:
            scores = file.readlines()
            return [int(score.strip()) for score in scores]
    except FileNotFoundError:
        return []

# Reset function
def reset_game():
    global player_y, player_velocity_y, is_jumping, score, ground_obstacles, air_obstacles
    player_y = GROUND_Y - player_img.get_height()
    player_velocity_y = 0
    is_jumping = False
    score = 0
    ground_obstacles.clear()
    air_obstacles.clear()
    next_obstacle_x = SCREEN_WIDTH + 200
    for _ in range(3):
        ground_obstacles.append({"x": next_obstacle_x, "y": GROUND_Y - ground_obstacle_img.get_height()})
        air_obstacles.append({"x": next_obstacle_x + random.randint(100, 200), "y": GROUND_Y - 120})
        next_obstacle_x += min_distance_between_obstacles + random.randint(0, obstacle_spacing_variation)

# Menu Screen Function with GIF background
def menu_screen():
    global game_active, running
    menu_music.play(loops=-1)
    while not game_active and running:
        update_background_gif()
        draw_text("Camel Dash Enhanced", fonts, yellow, screen, 125, 50)
        draw_text("Press P to Play", font, white, screen, 350, 200)
        draw_text("Press H to View History", font, white, screen, 330, 250)
        draw_text("Press Q to Quit", font, white, screen, 350, 300)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    click_sound.play()  # Play click sound
                    reset_game()
                    game_active = True
                    smooth_transition(menu_music, game_music)
                elif event.key == pygame.K_h:
                    click_sound.play()  # Play click sound
                    history_screen()
                elif event.key == pygame.K_q:
                    click_sound.play()  # Play click sound
                    running = False

# History Screen Function with GIF background
def history_screen():
    scores = read_history()
    while True:
        update_background_gif()
        draw_text("Score History", font, white, screen, 280, 50)
        y_offset = 100
        # Display every other score starting from the 2nd (index 1)
        for i in range(0, len(scores), 2):  # Step by 2, so it skips every other score
            draw_text(f"{(i // 2) + 1}. Score: {scores[i]}", font, white, screen, 300, y_offset)
            y_offset += 30

        draw_text("Press B", font, white, screen, 30, 250)
        draw_text("to go back to", font, white, screen, 10, 280)
        draw_text("Menu", font, white, screen, 30, 310)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    click_sound.play()  # Play click sound
                    return

# Function to update the game background GIF frames at a slower speed for the pause screen
def update_pause_background_gif():
    global game_current_frame, pause_frame_counter
    pause_frame_counter += 1
    if pause_frame_counter >= pause_background_frame_delay:
        pause_frame_counter = 0
        game_current_frame = (game_current_frame + 1) % len(game_background_frames)
    screen.blit(game_background_frames[game_current_frame], (0, 0))

# Pause Screen Function with GIF background
def pause_screen():
    global game_paused, game_active, running
    game_music.set_volume(0.2)  # Lower the game music volume in the pause screen
    while game_paused:
        update_pause_background_gif()  # Update pause screen with slower GIF

        draw_text("Game Paused", font, white, screen, 300, 150)
        draw_text("Press C to Continue", font, white, screen, 250, 200)
        draw_text("Press M to go to Menu", font, white, screen, 250, 250)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    click_sound.play()  # Play click sound
                    game_paused = False
                    game_music.set_volume(0.5)
                elif event.key == pygame.K_m:
                    click_sound.play()  # Play click sound
                    game_paused = False
                    game_music.stop()
                    menu_music.play(loops=-1)
                    game_active = False
                    return

# Function to update game background GIF frames
def update_game_background_gif():
    global game_current_frame, game_frame_counter
    game_frame_counter += 1
    if game_frame_counter >= game_background_frame_delay:
        game_frame_counter = 0
        game_current_frame = (game_current_frame + 1) % len(game_background_frames)
    screen.blit(game_background_frames[game_current_frame], (0, 0))

# Draw text helper function
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

# Update background GIF frames
def update_background_gif():
    global current_frame, frame_counter
    frame_counter += 1
    if frame_counter >= background_frame_delay:
        frame_counter = 0
        current_frame = (current_frame + 1) % len(background_frames)
    screen.blit(background_frames[current_frame], (0, 0))


# Main game loop
while running:
    if not game_active:
        menu_screen()
    else:
        # Update game background if in active game state
        update_game_background_gif()

        # Handle gameplay events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not is_jumping:
                    jump_sound.play()  # Play jumping sound
                    player_velocity_y = jump_strength
                    is_jumping = True
                elif event.key == pygame.K_ESCAPE:
                    click_sound.play()  # Play click sound
                    game_paused = True
                    pause_screen()

        # Update player physics
        player_y += player_velocity_y
        player_velocity_y += gravity
        if player_y >= GROUND_Y - player_img.get_height():
            player_y = GROUND_Y - player_img.get_height()
            player_velocity_y = 0
            is_jumping = False

        # Draw ground tiles, player, obstacles, and manage collisions
        ground_tile_width = ground_tile.get_width()
        for x in range(0, SCREEN_WIDTH, ground_tile_width):
            screen.blit(ground_tile, (x, GROUND_Y))

        screen.blit(player_img, (player_x, player_y))

        # Move and draw each ground obstacle
        for obstacle in ground_obstacles:
            obstacle["x"] -= obstacle_speed
            if obstacle["x"] < -ground_obstacle_img.get_width():
                obstacle["x"] = SCREEN_WIDTH + min_distance_between_obstacles + random.randint(0,
                                                                                               obstacle_spacing_variation)
                score += 1

            screen.blit(ground_obstacle_img, (obstacle["x"], obstacle["y"]))

            # Collision detection
            player_rect = pygame.Rect(player_x, player_y, player_img.get_width(), player_img.get_height())
            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], ground_obstacle_img.get_width(),
                                        ground_obstacle_img.get_height())
            if player_rect.colliderect(obstacle_rect):
                hit_sound.play()  # Play hit sound
                save_score(score)  # Save the score when the game ends
                game_active = False
                game_music.stop()
                menu_music.play(loops=-1)  # Restart menu music after game over

        # Move and draw each air obstacle
        for obstacle in air_obstacles:
            obstacle["x"] -= obstacle_speed
            if obstacle["x"] < -air_obstacle_img.get_width():
                obstacle["x"] = SCREEN_WIDTH + min_distance_between_obstacles + random.randint(0,
                                                                                               obstacle_spacing_variation)
                obstacle["y"] = random.randint(GROUND_Y - 120, GROUND_Y - 50)
                score += 1

            screen.blit(air_obstacle_img, (obstacle["x"], obstacle["y"]))

            # Collision detection
            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], air_obstacle_img.get_width(),
                                        air_obstacle_img.get_height())
            if player_rect.colliderect(obstacle_rect):
                hit_sound.play()  # Play hit sound
                game_active = False
                save_score(score)  # Save the score when the game ends
                game_music.stop()
                menu_music.play(loops=-1)

        # Display score
        score_text = font.render(f"Score: {score}", True, white)
        screen.blit(score_text, (20, 20))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
