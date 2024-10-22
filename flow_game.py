import pygame
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pegasus Maze Game")

# Load the character image (replace with your own Pegasus)
pegasus = pygame.image.load('pegasus.jpeg')
pegasus = pygame.transform.scale(pegasus, (40, 40))  # Adjust size to fit the maze
pegasus_x, pegasus_y = 50, 50  # Starting position (inside the maze)

# Define maze walls (simple example)
maze_walls = [
    pygame.Rect(100, 0, 10, 200),
    pygame.Rect(0, 200, 200, 10),
    pygame.Rect(200, 100, 10, 200),
    pygame.Rect(300, 0, 10, 200),
    pygame.Rect(400, 100, 10, 300),
    pygame.Rect(500, 100, 10, 300),
    pygame.Rect(600, 100, 10, 300),
    # More walls can be added to make the maze complex
]

# Button parameters
button_color = (0, 128, 255)
button_hover_color = (0, 255, 128)
button_rect = pygame.Rect(650, 500, 100, 50)  # Position and size of button

# Variables to control movement
move_to_next = False
target_x, target_y = 200, 200  # Initial target inside the maze

# Function to draw maze walls
def draw_maze():
    for wall in maze_walls:
        pygame.draw.rect(screen, (0, 0, 255), wall)

# Function to draw text
def draw_text(text, x, y, font, color=(255, 255, 255)):
    screen_text = font.render(text, True, color)
    screen.blit(screen_text, (x, y))

# Function to move the Pegasus smoothly
def move_pegasus():
    global pegasus_x, pegasus_y, move_to_next

    if move_to_next:
        # Move Pegasus smoothly to the target
        if pegasus_x < target_x:
            pegasus_x += 3
        elif pegasus_x > target_x:
            pegasus_x -= 3

        if pegasus_y < target_y:
            pegasus_y += 3
        elif pegasus_y > target_y:
            pegasus_y -= 3

        # When Pegasus reaches the target, stop moving
        if abs(pegasus_x - target_x) < 5 and abs(pegasus_y - target_y) < 5:
            move_to_next = False

# Main game loop
running = True
font = pygame.font.SysFont(None, 40)

while running:
    screen.fill((173, 216, 230))  # Clear the screen with a light blue color

    # Draw maze and character
    draw_maze()
    screen.blit(pegasus, (pegasus_x, pegasus_y))

    # Draw button
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, button_hover_color, button_rect)
    else:
        pygame.draw.rect(screen, button_color, button_rect)

    draw_text("Move", button_rect.x + 20, button_rect.y + 10, font)

    # Handle movement
    move_pegasus()

    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # Check for button click to move
        if event.type == MOUSEBUTTONDOWN:
            if button_rect.collidepoint(mouse_pos) and not move_to_next:
                move_to_next = True  # Start movement to the next target

    pygame.display.update()

pygame.quit()
