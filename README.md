# 3D Scrolling Shooter
![alt text](image.png)

Minimalist representation of that scam youtube ad game. Copilot wrote the whole thing, including the rest of this readme. I changed one line of code.

## How to Play

### Controls
- **Left Arrow**: Move player(s) left
- **Right Arrow**: Move player(s) right  
- **Space**: Fire projectiles
- **Up/Down Arrows**: Navigate menu options (when game over)
- **Enter**: Select menu option (when game over)

### Gameplay
1. You start with a single player instance
2. Move left and right to dodge enemies and collect powerups
3. Shoot enemies to score points:
   - Regular enemies: 10 points
   - Boss enemies: 50 points
4. Collect numbered powerups to change your player count:
   - Positive numbers (+1 to +5) add more player instances
   - Negative numbers (-1 to -5) remove player instances
   - You need at least 1 player instance to stay alive
5. Multiple player instances move in a circular formation
6. Each player instance can shoot independently
7. Watch out for boss enemies:
   - Larger red enemies with health points displayed
   - Require multiple hits to defeat
   - Colliding with a boss removes player instances equal to its remaining health
8. Game ends when you lose all player instances

## Technical Implementation Details

### Display Settings
- Window Size: 800x600 pixels
- Pseudo-3D road perspective with horizon at y=100
- Road width varies from 400 pixels at bottom to 133 pixels at horizon

### Player Mechanics
- Base Size: 40x40 pixels
- Starting Position: Centered horizontally, 80 pixels from bottom
- Movement Speed: 5 pixels per frame
- Multiple instances arranged in concentric circles
- Circle radius: 1/6 of road width at bottom

### Projectile System
- Base Size: 8x15 pixels
- Speed: 7 pixels per frame upward
- Fired from each player instance independently
- Maintains perspective-correct movement

### Enemy System
#### Regular Enemies
- Base Size: 40x40 pixels (increased for better visibility)
- Speed: 1 pixel per frame downward (reduced for better gameplay)
- Spawn Rate: Every 60 frames
- Spawn in clusters of 3-12 enemies
- Track player movement with smooth transitions
- Speed increases as they get closer to bottom
- Minimum scale of 0.4 when far away

#### Boss Enemies
- 4x larger than regular enemies
- Colored red with health display
- 5% chance to spawn instead of regular enemy cluster
- Random health between 10-100 points
- Requires one hit per health point to defeat
- Moves slower than regular enemies
- Deals damage equal to remaining health on collision

### Powerup System
- Base Size: 50x50 pixels
- Speed: 2 pixels per frame downward
- Spawn Rate: Every 300 frames
- Always spawn in pairs
- Values range from -5 to +5
- Flash effect with 10-frame interval
- Take up exactly 1/4 of road width each

### Visual Effects
- Perspective scaling based on y-position
- Road with side barriers
- Player shadows
- Semi-transparent powerups
- Flashing numbers on powerups
- Health counter display on boss enemies

### Game States
- Playing state
- Game Over state with menu options
- Score tracking
- Player instance counter

### Performance
- 60 FPS target
- Frame counter cycles every 3600 frames
- Perspective calculations for smooth motion

### Technical Notes
- Uses Pygame library
- Collision detection with perspective scaling and buffer zone
- Dynamic object scaling based on y-position
- Normalized x-coordinates for perspective accuracy
- Memory management with object cleanup

## Requirements
- Python 3.x
- Pygame library