import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
ROAD_WIDTH_BOTTOM = WINDOW_WIDTH // 2
ROAD_WIDTH_TOP = ROAD_WIDTH_BOTTOM // 3
HORIZON_Y = 100
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("3D Scrolling Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
YELLOW = (255, 255, 0)

# Player settings
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40
player_x = WINDOW_WIDTH // 2  # Center horizontally
player_y = WINDOW_HEIGHT - 80  # Move slightly higher up from the bottom
player_speed = 5
player_instances = 1
player_circle_radius = ROAD_WIDTH_BOTTOM // 6

# Projectile settings
PROJECTILE_BASE_WIDTH = 8
PROJECTILE_BASE_HEIGHT = 15
projectile_speed = 7
projectiles = []  # Each projectile is [x, y, normalized_x]  # Modified to store normalized x position

# Enemy settings
ENEMY_BASE_WIDTH = 40  # Increased from 30
ENEMY_BASE_HEIGHT = 40  # Increased from 30
enemy_speed = 1
enemies = []  # Regular enemies: [normalized_x, y]
boss_enemies = []  # Boss enemies: [normalized_x, y, health]
spawn_rate = 60
boss_spawn_chance = 0.05  # 5% chance when spawning enemies

# Powerup settings
POWERUP_BASE_WIDTH = 50   # Increased from 25 to take up more space
POWERUP_BASE_HEIGHT = 50  # Made square for better visibility
powerup_speed = 2
powerups = []  # Each powerup is [normalized_x, y, value, flash_timer]
powerup_spawn_rate = 300  # Spawn much less frequently than enemies
flash_speed = 10  # Speed of number flashing

# Game settings
score = 0
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Game states
GAME_STATE_PLAYING = 0
GAME_STATE_GAME_OVER = 1
game_state = GAME_STATE_PLAYING
selected_option = 0  # 0 for restart, 1 for quit

def reset_game():
    global player_instances, score, enemies, projectiles, powerups, game_state
    player_instances = 1
    score = 0
    enemies.clear()
    projectiles.clear()
    powerups.clear()
    game_state = GAME_STATE_PLAYING

def get_scale_factor(y_pos):
    # Objects appear larger when closer (lower y value = further away)
    distance = (y_pos - HORIZON_Y) / (WINDOW_HEIGHT - HORIZON_Y)
    return max(0.4, min(1.0, distance))  # Increased minimum scale from 0.2 to 0.4

def get_x_position_on_road(normalized_x, y_pos):
    # Convert a normalized x position (0-1) to actual x position based on perspective
    road_width = ROAD_WIDTH_BOTTOM - (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP) * ((WINDOW_HEIGHT - y_pos) / (WINDOW_HEIGHT - HORIZON_Y))
    road_left = (WINDOW_WIDTH - road_width) / 2
    return road_left + (road_width * normalized_x)

def draw_road():
    # Draw the main road surface
    road_points = [
        (WINDOW_WIDTH//2 - ROAD_WIDTH_BOTTOM//2, WINDOW_HEIGHT),
        (WINDOW_WIDTH//2 - ROAD_WIDTH_TOP//2, HORIZON_Y),
        (WINDOW_WIDTH//2 + ROAD_WIDTH_TOP//2, HORIZON_Y),
        (WINDOW_WIDTH//2 + ROAD_WIDTH_BOTTOM//2, WINDOW_HEIGHT)
    ]
    pygame.draw.polygon(screen, GRAY, road_points)
    
    # Draw road barriers
    barrier_width = 10
    left_barrier_points = [
        (WINDOW_WIDTH//2 - ROAD_WIDTH_BOTTOM//2 - barrier_width, WINDOW_HEIGHT),
        (WINDOW_WIDTH//2 - ROAD_WIDTH_TOP//2 - barrier_width//2, HORIZON_Y),
        (WINDOW_WIDTH//2 - ROAD_WIDTH_TOP//2, HORIZON_Y),
        (WINDOW_WIDTH//2 - ROAD_WIDTH_BOTTOM//2, WINDOW_HEIGHT)
    ]
    right_barrier_points = [
        (WINDOW_WIDTH//2 + ROAD_WIDTH_BOTTOM//2, WINDOW_HEIGHT),
        (WINDOW_WIDTH//2 + ROAD_WIDTH_TOP//2, HORIZON_Y),
        (WINDOW_WIDTH//2 + ROAD_WIDTH_TOP//2 + barrier_width//2, HORIZON_Y),
        (WINDOW_WIDTH//2 + ROAD_WIDTH_BOTTOM//2 + barrier_width, WINDOW_HEIGHT)
    ]
    pygame.draw.polygon(screen, DARK_GRAY, left_barrier_points)
    pygame.draw.polygon(screen, DARK_GRAY, right_barrier_points)

def spawn_enemy():
    # Chance to spawn a boss enemy instead of regular enemies
    if random.random() < boss_spawn_chance:
        normalized_x = random.random()
        health = random.randint(10, 100)
        boss_enemies.append([normalized_x, HORIZON_Y, health])
        return

    # Regular enemy cluster spawning
    cluster_size = random.randint(3, 12)  # Increased from 2-10 to 3-12 enemies per cluster
    cluster_spread = 0.2  # How spread out the cluster is horizontally
    
    # Choose a center point for the cluster
    center_x = random.random()
    # Ensure the center point allows for spread in both directions
    center_x = max(cluster_spread, min(1 - cluster_spread, center_x))
    
    # Create enemies in the cluster
    for _ in range(cluster_size):
        # Add some random spread to x position
        spread = random.uniform(-cluster_spread, cluster_spread)
        normalized_x = max(0, min(1, center_x + spread))
        
        # Add some variation to starting y position for more natural grouping
        y_variation = random.uniform(-20, 20)
        enemies.append([normalized_x, HORIZON_Y + y_variation])

def spawn_powerup_pair():
    # Spawn two powerups side by side, each taking up 1/4 of the road width
    base_x = random.random() * 0.5  # Base position for the left powerup, allowing only left half of road
    
    # Position powerups so they each take up 1/4 of the road
    # Left powerup centered at 1/4 position from base_x
    left_x = base_x + 0.125  # 0.125 is 1/8 of road width, centering it in its quarter
    # Right powerup centered at 1/4 position from left powerup
    right_x = left_x + 0.25  # Move 1/4 of road width to center of next quarter
    
    # Create random values for the powerups
    val1 = random.randint(-5, 5)
    val2 = random.randint(-5, 5)
    while val2 == val1:  # Ensure different values
        val2 = random.randint(-5, 5)
    
    # Make powerups larger to match their designated space
    powerups.append([left_x, HORIZON_Y, val1, 0])  # flash_timer starts at 0
    powerups.append([right_x, HORIZON_Y, val2, 0])

def draw_player(base_x, y):
    # Calculate positions for all player instances in a circle
    scale = get_scale_factor(y)
    width = PLAYER_WIDTH * scale
    height = PLAYER_HEIGHT * scale
    
    # For single instance, draw at center
    if player_instances == 1:
        # Draw player instance
        pygame.draw.rect(screen, RED, (base_x - width//2, y - height//2, width, height))
        
        # Draw shadow
        shadow_points = [
            (base_x - width//2, y + height//2),
            (base_x + width//2, y + height//2),
            (base_x + width//3, y + height),
            (base_x - width//3, y + height)
        ]
        pygame.draw.polygon(screen, DARK_GRAY, shadow_points)
        return

    # For multiple instances, distribute in concentric rings
    max_ring = math.ceil(math.sqrt(player_instances))
    instances_placed = 0
    
    for ring in range(max_ring):
        ring_radius = player_circle_radius * (ring + 1) / max_ring
        # Calculate how many instances should go in this ring
        if ring == max_ring - 1:  # Last ring
            instances_in_ring = player_instances - instances_placed
        else:
            instances_in_ring = min(math.floor(2 * math.pi * ring_radius / (width * 1.5)), 
                                  player_instances - instances_placed)
        
        if instances_placed + instances_in_ring > player_instances:
            instances_in_ring = player_instances - instances_placed
            
        # Skip this ring if no instances would be placed
        if instances_in_ring <= 0:
            continue
        
        ring_angle_step = 2 * math.pi / instances_in_ring
        
        for i in range(instances_in_ring):
            angle = ring_angle_step * i
            # Calculate offset from base position
            offset_x = ring_radius * math.cos(angle)
            offset_y = ring_radius * math.sin(angle) * 0.3
            
            x = base_x + offset_x
            instance_y = y + offset_y
            
            # Draw player instance
            pygame.draw.rect(screen, RED, (x - width//2, instance_y - height//2, width, height))
            
            # Draw shadow
            shadow_points = [
                (x - width//2, instance_y + height//2),
                (x + width//2, instance_y + height//2),
                (x + width//3, instance_y + height),
                (x - width//3, instance_y + height)
            ]
            pygame.draw.polygon(screen, DARK_GRAY, shadow_points)
        
        instances_placed += instances_in_ring

def draw_projectiles():
    for proj in projectiles:
        x, y, normalized_x = proj
        # Get perspective-correct x position
        perspective_x = get_x_position_on_road(normalized_x, y)
        scale = get_scale_factor(y)
        width = PROJECTILE_BASE_WIDTH * scale
        height = PROJECTILE_BASE_HEIGHT * scale
        pygame.draw.rect(screen, WHITE, (perspective_x - width//2, y - height//2, width, height))

def draw_enemies():
    # Draw regular enemies
    for enemy in enemies:
        normalized_x, y = enemy
        x = get_x_position_on_road(normalized_x, y)
        scale = get_scale_factor(y)
        width = ENEMY_BASE_WIDTH * scale
        height = ENEMY_BASE_HEIGHT * scale
        pygame.draw.rect(screen, WHITE, (x - width//2, y - height//2, width, height))

    # Draw boss enemies
    for boss in boss_enemies:
        normalized_x, y, health = boss
        x = get_x_position_on_road(normalized_x, y)
        scale = get_scale_factor(y)
        width = ENEMY_BASE_WIDTH * scale * 4  # Increased from 2 to 4 times larger
        height = ENEMY_BASE_HEIGHT * scale * 4
        
        # Draw boss enemy
        pygame.draw.rect(screen, RED, (x - width//2, y - height//2, width, height))
        
        # Draw health number
        font_size = max(20, int(width * 0.4))
        health_font = pygame.font.Font(None, font_size)
        health_text = health_font.render(str(health), True, WHITE)
        text_rect = health_text.get_rect(center=(x, y))
        screen.blit(health_text, text_rect)

def draw_powerups():
    for powerup in powerups:
        normalized_x, y, value, flash_timer = powerup
        x = get_x_position_on_road(normalized_x, y)
        
        # Calculate road width at current y position
        road_width = ROAD_WIDTH_BOTTOM - (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP) * ((WINDOW_HEIGHT - y) / (WINDOW_HEIGHT - HORIZON_Y))
        
        # Make powerup width exactly 1/4 of the road width at current y position
        width = road_width / 4
        height = width  # Keep powerup square
        
        # Create a surface for the powerup with transparency
        powerup_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(powerup_surface, (YELLOW[0], YELLOW[1], YELLOW[2], 160), (0, 0, width, height))  # 160 is the alpha value (0-255)
        
        # Draw powerup box
        screen.blit(powerup_surface, (x - width//2, y - height//2))
        
        # Draw flashing number - scale font based on powerup size
        if (flash_timer // flash_speed) % 2 == 0:  # Flash effect
            font_size = max(20, int(width * 0.5))  # Scale font with powerup size but not smaller than 20
            number_font = pygame.font.Font(None, font_size)
            value_text = number_font.render(str(value), True, BLACK)
            text_rect = value_text.get_rect(center=(x, y))
            screen.blit(value_text, text_rect)
        
        powerup[3] = (flash_timer + 1) % (flash_speed * 2)  # Update flash timer

def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    # Add a small buffer to make collisions more forgiving
    buffer = 5
    return (x1 < x2 + w2 + buffer and x1 + w1 + buffer > x2 and
            y1 < y2 + h2 + buffer and y1 + h1 + buffer > y2)

def update_enemy_position(enemy, target_x):
    normalized_x, y = enemy
    # Get current screen position
    current_x = get_x_position_on_road(normalized_x, y)
    
    # Calculate direction to player
    dx = target_x - current_x
    
    # Update normalized_x based on direction
    road_width = ROAD_WIDTH_BOTTOM - (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP) * ((WINDOW_HEIGHT - y) / (WINDOW_HEIGHT - HORIZON_Y))
    movement_scale = 0.01  # Adjust this to control how quickly enemies track the player
    normalized_movement = (dx / road_width) * movement_scale
    
    # Update normalized_x while keeping it within bounds
    new_normalized_x = max(0, min(1, normalized_x + normalized_movement))
    enemy[0] = new_normalized_x

def draw_game_over_screen():
    # Draw semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Draw "GAME OVER" text
    game_over_text = font.render("GAME OVER", True, WHITE)
    text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
    screen.blit(game_over_text, text_rect)
    
    # Draw final score
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
    screen.blit(score_text, score_rect)
    
    # Draw options
    restart_color = WHITE if selected_option == 0 else GRAY
    quit_color = WHITE if selected_option == 1 else GRAY
    
    restart_text = font.render("Restart", True, restart_color)
    quit_text = font.render("Quit", True, quit_color)
    
    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
    quit_rect = quit_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 90))
    
    screen.blit(restart_text, restart_rect)
    screen.blit(quit_text, quit_rect)

running = True
frame_count = 0

while running:
    if game_state == GAME_STATE_PLAYING:
        # Increment frame counter at the start of the loop
        frame_count = (frame_count + 1) % 3600  # Reset counter every minute to prevent overflow
        
        # Spawn enemies and powerups
        if frame_count % spawn_rate == 0:
            spawn_enemy()
        if frame_count % powerup_spawn_rate == 0:
            spawn_powerup_pair()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Fire a projectile from each player instance using the same distribution logic
                    if player_instances == 1:
                        # Calculate normalized x position for the projectile
                        normalized_x = (player_x - (WINDOW_WIDTH//2 - ROAD_WIDTH_BOTTOM//2)) / ROAD_WIDTH_BOTTOM
                        projectiles.append([player_x, player_y, normalized_x])
                    else:
                        max_ring = math.ceil(math.sqrt(player_instances))
                        instances_placed = 0
                        
                        for ring in range(max_ring):
                            ring_radius = player_circle_radius * (ring + 1) / max_ring
                            if ring == max_ring - 1:
                                instances_in_ring = player_instances - instances_placed
                            else:
                                instances_in_ring = min(math.floor(2 * math.pi * ring_radius / (PLAYER_WIDTH * 1.5)),
                                                      player_instances - instances_placed)
                            
                            if instances_placed + instances_in_ring > player_instances:
                                instances_in_ring = player_instances - instances_placed
                                
                            # Skip this ring if no instances would be placed
                            if instances_in_ring <= 0:
                                continue
                            
                            ring_angle_step = 2 * math.pi / instances_in_ring
                            
                            for i in range(instances_in_ring):
                                angle = ring_angle_step * i
                                # Calculate offset from base position
                                offset_x = ring_radius * math.cos(angle)
                                offset_y = ring_radius * math.sin(angle) * 0.3
                                
                                x = player_x + offset_x
                                y = player_y + offset_y
                                
                                # Calculate normalized x position for each projectile
                                normalized_x = (x - (WINDOW_WIDTH//2 - ROAD_WIDTH_BOTTOM//2)) / ROAD_WIDTH_BOTTOM
                                projectiles.append([x, y, normalized_x])
                            
                            instances_placed += instances_in_ring

        # Player movement
        keys = pygame.key.get_pressed()
        normalized_player_x = (player_x - (WINDOW_WIDTH//2 - ROAD_WIDTH_BOTTOM//2)) / ROAD_WIDTH_BOTTOM
        if keys[pygame.K_LEFT] and normalized_player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and normalized_player_x < 1:
            player_x += player_speed

        # Update projectiles
        for proj in projectiles[:]:
            x, y, normalized_x = proj
            # Update y position
            y -= projectile_speed
            # Update x position based on perspective
            x = get_x_position_on_road(normalized_x, y)
            proj[0] = x
            proj[1] = y
            if y < HORIZON_Y:
                projectiles.remove(proj)

        # Update enemies and check collisions
        for enemy in enemies[:]:
            normalized_x, y = enemy
            # Update y position with perspective-based speed
            speed_scale = 1 + (y - HORIZON_Y) / (WINDOW_HEIGHT - HORIZON_Y)  # Moves faster when closer
            enemy[1] += enemy_speed * speed_scale
            
            # Update x position to move towards player
            update_enemy_position(enemy, player_x)
            
            enemy_x = get_x_position_on_road(normalized_x, y)
            
            if y > WINDOW_HEIGHT:
                enemies.remove(enemy)
                continue

            enemy_scale = get_scale_factor(y)
            enemy_width = ENEMY_BASE_WIDTH * enemy_scale
            enemy_height = ENEMY_BASE_HEIGHT * enemy_scale

            # Check collision with projectiles first
            for proj in projectiles[:]:
                proj_x, proj_y, proj_normalized_x = proj
                proj_scale = get_scale_factor(proj_y)
                proj_width = PROJECTILE_BASE_WIDTH * proj_scale
                proj_height = PROJECTILE_BASE_HEIGHT * proj_scale
                
                if check_collision(
                    proj_x - proj_width//2, proj_y - proj_height//2,
                    proj_width, proj_height,
                    enemy_x - enemy_width//2, y - enemy_height//2,
                    enemy_width, enemy_height):
                    if proj in projectiles:
                        projectiles.remove(proj)
                    if enemy in enemies:
                        enemies.remove(enemy)
                        score += 10
                    break

            # Then check collision with player instances
            if enemy in enemies:  # Only if enemy wasn't destroyed by projectile
                player_scale = get_scale_factor(player_y)
                collision_detected = False
                
                # Use the same concentric rings distribution as drawing
                if player_instances == 1:
                    # Check collision with single centered instance
                    if check_collision(
                        player_x - (PLAYER_WIDTH * player_scale)//2, player_y - (PLAYER_HEIGHT * player_scale)//2,
                        PLAYER_WIDTH * player_scale, PLAYER_HEIGHT * player_scale,
                        enemy_x - enemy_width//2, y - enemy_height//2,
                        enemy_width, enemy_height):
                        player_instances -= 1
                        enemies.remove(enemy)
                        if player_instances <= 0:
                            game_state = GAME_STATE_GAME_OVER
                else:
                    # Check collision with instances in concentric rings
                    max_ring = math.ceil(math.sqrt(player_instances))
                    instances_placed = 0
                    
                    for ring in range(max_ring):
                        if collision_detected:
                            break
                            
                        ring_radius = player_circle_radius * (ring + 1) / max_ring
                        if ring == max_ring - 1:
                            instances_in_ring = player_instances - instances_placed
                        else:
                            instances_in_ring = min(math.floor(2 * math.pi * ring_radius / (PLAYER_WIDTH * player_scale * 1.5)),
                                                  player_instances - instances_placed)
                        
                        if instances_placed + instances_in_ring > player_instances:
                            instances_in_ring = player_instances - instances_placed
                        
                        if instances_in_ring <= 0:  # Skip rings with no instances
                            continue
                            
                        ring_angle_step = 2 * math.pi / instances_in_ring
                        
                        for i in range(instances_in_ring):
                            angle = ring_angle_step * i
                            # Calculate offset from base position
                            offset_x = ring_radius * math.cos(angle)
                            offset_y = ring_radius * math.sin(angle) * 0.3
                            
                            x = player_x + offset_x
                            instance_y = player_y + offset_y
                            
                            if check_collision(
                                x - (PLAYER_WIDTH * player_scale)//2, instance_y - (PLAYER_HEIGHT * player_scale)//2,
                                PLAYER_WIDTH * player_scale, PLAYER_HEIGHT * player_scale,
                                enemy_x - enemy_width//2, y - enemy_height//2,
                                enemy_width, enemy_height):
                                player_instances -= 1
                                enemies.remove(enemy)
                                if player_instances <= 0:
                                    game_state = GAME_STATE_GAME_OVER
                                collision_detected = True
                                break

        # Update boss enemies and check collisions
        for boss in boss_enemies[:]:
            normalized_x, y, health = boss
            # Update y position with perspective-based speed
            speed_scale = 1 + (y - HORIZON_Y) / (WINDOW_HEIGHT - HORIZON_Y)  # Moves faster when closer
            boss[1] += enemy_speed * speed_scale * 0.7  # Boss moves slightly slower
            
            # Update x position to move towards player
            current_x = get_x_position_on_road(normalized_x, y)
            dx = player_x - current_x
            road_width = ROAD_WIDTH_BOTTOM - (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP) * ((WINDOW_HEIGHT - y) / (WINDOW_HEIGHT - HORIZON_Y))
            movement_scale = 0.005  # Boss moves more slowly horizontally
            normalized_movement = (dx / road_width) * movement_scale
            boss[0] = max(0, min(1, normalized_x + normalized_movement))
            
            if y > WINDOW_HEIGHT:
                boss_enemies.remove(boss)
                continue

            boss_scale = get_scale_factor(y)
            boss_width = ENEMY_BASE_WIDTH * boss_scale * 4  # Increased from 2 to 4 times larger
            boss_height = ENEMY_BASE_HEIGHT * boss_scale * 4
            boss_x = get_x_position_on_road(normalized_x, y)

            # Check collision with projectiles
            for proj in projectiles[:]:
                proj_x, proj_y, proj_normalized_x = proj
                proj_scale = get_scale_factor(proj_y)
                proj_width = PROJECTILE_BASE_WIDTH * proj_scale
                proj_height = PROJECTILE_BASE_HEIGHT * proj_scale
                
                if check_collision(
                    proj_x - proj_width//2, proj_y - proj_height//2,
                    proj_width, proj_height,
                    boss_x - boss_width//2, y - boss_height//2,
                    boss_width, boss_height):
                    if proj in projectiles:
                        projectiles.remove(proj)
                        boss[2] -= 1  # Decrease health by 1
                        if boss[2] <= 0:  # Boss is defeated
                            boss_enemies.remove(boss)
                            score += 50  # More points for defeating a boss
                    break

            # Check collision with player (if boss still alive)
            if boss in boss_enemies:
                player_scale = get_scale_factor(player_y)
                # Similar player collision code as with regular enemies
                if player_instances == 1:
                    if check_collision(
                        player_x - (PLAYER_WIDTH * player_scale)//2, player_y - (PLAYER_HEIGHT * player_scale)//2,
                        PLAYER_WIDTH * player_scale, PLAYER_HEIGHT * player_scale,
                        boss_x - boss_width//2, y - boss_height//2,
                        boss_width, boss_height):
                        player_instances -= health  # Remove instances equal to boss health
                        boss_enemies.remove(boss)
                        if player_instances <= 0:
                            game_state = GAME_STATE_GAME_OVER
                else:
                    # Check collision with instances in concentric rings
                    max_ring = math.ceil(math.sqrt(player_instances))
                    instances_placed = 0
                    collision_detected = False
                    
                    for ring in range(max_ring):
                        if collision_detected:
                            break
                            
                        ring_radius = player_circle_radius * (ring + 1) / max_ring
                        if ring == max_ring - 1:
                            instances_in_ring = player_instances - instances_placed
                        else:
                            instances_in_ring = min(math.floor(2 * math.pi * ring_radius / (PLAYER_WIDTH * player_scale * 1.5)),
                                                  player_instances - instances_placed)
                        
                        if instances_placed + instances_in_ring > player_instances:
                            instances_in_ring = player_instances - instances_placed
                        
                        if instances_in_ring <= 0:  # Skip rings with no instances
                            continue
                            
                        ring_angle_step = 2 * math.pi / instances_in_ring
                        
                        for i in range(instances_in_ring):
                            if collision_detected:
                                break
                                
                            # Calculate instance position and size
                            angle = ring_angle_step * i
                            offset_x = ring_radius * math.cos(angle)
                            offset_y = ring_radius * math.sin(angle) * 0.3
                            instance_x = player_x + offset_x
                            instance_y = player_y + offset_y
                            
                            instance_width = PLAYER_WIDTH * player_scale
                            instance_height = PLAYER_HEIGHT * player_scale
                            
                            if check_collision(
                                instance_x - (PLAYER_WIDTH * player_scale)//2, instance_y - (PLAYER_HEIGHT * player_scale)//2,
                                PLAYER_WIDTH * player_scale, PLAYER_HEIGHT * player_scale,
                                boss_x - boss_width//2, y - boss_height//2,
                                boss_width, boss_height):
                                player_instances -= health
                                boss_enemies.remove(boss)
                                if player_instances <= 0:
                                    game_state = GAME_STATE_GAME_OVER
                                collision_detected = True
                                break
                            
                        instances_placed += instances_in_ring

        # Update powerups and check collisions
        for powerup in powerups[:]:
            normalized_x, y, value, flash_timer = powerup
            # Update y position with perspective-based speed
            speed_scale = 1 + (y - HORIZON_Y) / (WINDOW_HEIGHT - HORIZON_Y)
            y += powerup_speed * speed_scale
            powerup[1] = y
            
            if y > WINDOW_HEIGHT:
                powerups.remove(powerup)
                continue

            powerup_scale = get_scale_factor(y)
            powerup_width = POWERUP_BASE_WIDTH * powerup_scale
            powerup_height = POWERUP_BASE_HEIGHT * powerup_scale

            # Get screen position for powerup - keeping original normalized_x position
            powerup_x = get_x_position_on_road(normalized_x, y)
            
            # Check collision with player instances
            collision_detected = False  # Add flag to track if powerup was collected
            player_scale = get_scale_factor(player_y)  # Get player's correct scale
            
            if player_instances == 1:
                # Check collision with single centered instance
                if check_collision(
                    player_x - (PLAYER_WIDTH * player_scale)//2, player_y - (PLAYER_HEIGHT * player_scale)//2,
                    PLAYER_WIDTH * player_scale, PLAYER_HEIGHT * player_scale,
                    powerup_x - powerup_width//2, y - powerup_height//2,
                    powerup_width, powerup_height):
                    new_instances = max(1, player_instances + value)
                    if new_instances != player_instances:
                        player_instances = new_instances
                    powerups.remove(powerup)
                    collision_detected = True
            else:
                # Check collision with instances in concentric rings
                max_ring = math.ceil(math.sqrt(player_instances))
                instances_placed = 0
                
                for ring in range(max_ring):
                    if collision_detected:  # Break outer loop if collision already detected
                        break
                        
                    ring_radius = player_circle_radius * (ring + 1) / max_ring
                    if ring == max_ring - 1:
                        instances_in_ring = player_instances - instances_placed
                    else:
                        instances_in_ring = min(math.floor(2 * math.pi * ring_radius / (PLAYER_WIDTH * player_scale * 1.5)),
                                              player_instances - instances_placed)
                    
                    if instances_placed + instances_in_ring > player_instances:
                        instances_in_ring = player_instances - instances_placed
                        
                    if instances_in_ring <= 0:  # Skip rings with no instances
                        continue
                        
                    ring_angle_step = 2 * math.pi / instances_in_ring
                    
                    for i in range(instances_in_ring):
                        if collision_detected:  # Break inner loop if collision already detected
                            break
                            
                        # Calculate instance position and size
                        angle = ring_angle_step * i
                        offset_x = ring_radius * math.cos(angle)
                        offset_y = ring_radius * math.sin(angle) * 0.3
                        instance_x = player_x + offset_x
                        instance_y = player_y + offset_y
                        
                        instance_width = PLAYER_WIDTH * player_scale
                        instance_height = PLAYER_HEIGHT * player_scale
                        
                        if check_collision(
                            instance_x - (PLAYER_WIDTH * player_scale)//2, instance_y - (PLAYER_HEIGHT * player_scale)//2,
                            PLAYER_WIDTH * player_scale, PLAYER_HEIGHT * player_scale,
                            powerup_x - powerup_width//2, y - powerup_height//2,
                            powerup_width, powerup_height):
                            new_instances = max(1, player_instances + value)
                            if new_instances != player_instances:
                                player_instances = new_instances
                            powerups.remove(powerup)
                            collision_detected = True
                            break
                            
                    if collision_detected:  # Skip remaining rings if collision detected
                        break

        # Check if player died
        if player_instances <= 0:
            game_state = GAME_STATE_GAME_OVER
            continue

        # Draw everything
        screen.fill(BLACK)
        draw_road()
        draw_enemies()
        draw_projectiles()
        draw_powerups()
        draw_player(player_x, player_y)
        
        # Draw UI elements
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        count_text = font.render(f"Players: {player_instances}", True, WHITE)
        screen.blit(count_text, (10, 50))

    elif game_state == GAME_STATE_GAME_OVER:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected_option = 1 - selected_option  # Toggle between 0 and 1
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:  # Restart
                        reset_game()
                    else:  # Quit
                        running = False

        # Draw game over screen on top of frozen game state
        draw_game_over_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()