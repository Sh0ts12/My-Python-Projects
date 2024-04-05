import pygame
import sys

# Initialize pygame
pygame.init()


# font sizes:

font = pygame.font.SysFont('arial', 24)

# Additional variables for edit mode

is_edit_mode = False
selected_object = None

# Functions


def distance_point_to_line_segment(p, a, b):
    """Calculate the distance from point p to the line segment ab."""
    # Vector from a to b
    ab = (b[0] - a[0], b[1] - a[1])
    # Vector from a to p
    ap = (p[0] - a[0], p[1] - a[1])
    # Normalize the direction from a to b
    ab_length = (ab[0]**2 + ab[1]**2)**0.5
    ab_normalized = (ab[0] / ab_length, ab[1] / ab_length)
    # Project vector from a to p onto ab
    t = ap[0]*ab_normalized[0] + ap[1]*ab_normalized[1]
    # Ensure t is within the range of [0, ab_length]
    t = max(0, min(ab_length, t))
    # Find the closest point on ab to p
    closest = (a[0] + ab_normalized[0] * t, a[1] + ab_normalized[1] * t)
    # Vector from p to closest point on ab
    pc = (closest[0] - p[0], closest[1] - p[1])
    # Distance from p to closest point on ab
    distance = (pc[0]**2 + pc[1]**2)**0.5
    return distance


dragging_wall = False
wall_drag_start = None


def point_in_triangle(pt, v1, v2, v3):
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    b1 = sign(pt, v1, v2) < 0.0
    b2 = sign(pt, v2, v3) < 0.0
    b3 = sign(pt, v3, v1) < 0.0

    return ((b1 == b2) and (b2 == b3))


def substract(v1, v2):
    return v1[0] - v2[0], v1[1] - v2[1]


def add(v1, v2):
    return v1[0] + v2[0], v1[1] + v2[1]


dragging_triangle = False
triangle_offset = [None, None, None]


def is_hovering(mouse_pos, circle_pos, circle_radius):
    distance_squared = (circle_pos[0] - mouse_pos[0]
                        )**2 + (circle_pos[1] - mouse_pos[1])**2
    return distance_squared <= circle_radius**2


# Set up screen
screen_width = 1600
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Define player properties
player_color = WHITE
player_radius = 25
player_position = (100, screen_height - 100)  # Adjust as needed

# Define target properties
target_color = RED
target_radius = 25
target_position = (screen_width - 50, 50)  # Adjust as needed

# Define wall properties
wall_color = WHITE
wall_start_pos = (150, 75)
wall_end_pos = (screen_width - 400, 500)
wall_thickness = 15
wall_points = wall_start_pos and wall_end_pos

# Define reflecting triangle properties
triangle_color = WHITE

left_triangle_point = (screen_width - 150, screen_height - 50)
right_triangel_point = (screen_width - 50, screen_height - 50)
top_trianlge_point = (screen_width - 50, screen_height - 150)

triangle_points = [left_triangle_point,
                   right_triangel_point, top_trianlge_point]


# Initialize variables for dragging the player

dragging_player = False
player_offset_x = 0
player_offset_y = 0


# Variables for dragging target

dragging_target = False
target_offset_x = 0
target_offset_y = 0

# Main game loop
running = True

while running:

    mouse_pos = pygame.mouse.get_pos()
    hovering_wall = distance_point_to_line_segment(
        mouse_pos, wall_start_pos, wall_end_pos) <= 10

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_o:
                is_edit_mode = not is_edit_mode
                print("Edit mode Toggled:", is_edit_mode)

        # Edit mode:

       # Handling mouse click in edit mode
        elif event.type == pygame.MOUSEBUTTONDOWN and is_edit_mode:
            mouse_pos = event.pos
            keys = pygame.key.get_pressed()
            shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

            if is_hovering(mouse_pos, player_position, player_radius):
                dragging_player = True
                selected_object = 'player'
                player_offset_x = player_position[0] - mouse_pos[0]
                player_offset_y = player_position[1] - mouse_pos[1]

            #
            # add checks for other game elements here:

            # check for target
            elif is_hovering(mouse_pos, target_position, target_radius):
                dragging_target = True
                selected_object = 'target'
                target_offset_x = target_position[0] - mouse_pos[0]
                target_offset_y = target_position[1] - mouse_pos[1]

            # Check for bounce platform (triangle)

            elif point_in_triangle(pygame.mouse.get_pos(), triangle_points[0], triangle_points[1], triangle_points[2]):
                dragging_triangle = True
                selected_object = 'triangle'
                triangle_offset = [substract(p, mouse_pos)
                                   for p in triangle_points]

            elif distance_point_to_line_segment(mouse_pos, wall_start_pos, wall_end_pos) < 10:
                dragging_wall = True
                selected_object = 'wall'

                original_wall_start_pos = wall_start_pos
                original_wall_end_pos = wall_end_pos

                if shift_pressed:
                    wall_drag_mode = "whole"

                else:
                    if (mouse_pos[0] - wall_start_pos[0])**2 + (mouse_pos[1] - wall_start_pos[1])**2 < (mouse_pos[0] - wall_end_pos[0])**2 + (mouse_pos[1] - wall_end_pos[1])**2:
                        wall_drag_mode = "start"  # Move the start of the wall
                    else:
                        wall_drag_mode = "end"  # Move the end of the wall

                if (mouse_pos[0] - wall_start_pos[0])**2 + (mouse_pos[1] - wall_start_pos[1])**2 < (mouse_pos[0] - wall_end_pos[0])**2 + (mouse_pos[1] - wall_end_pos[1])**2:
                    wall_drag_start = True

                else:
                    wall_drag_start = False

        # Handle mouse release
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_target = False
            dragging_player = False
            dragging_triangle = False
            selected_object = None

            if event.type == pygame.MOUSEBUTTONUP and dragging_wall:
                dragging_wall = False
                wall_drag_start = None

        elif event.type == pygame.MOUSEMOTION and dragging_player and selected_object == 'player':
            mouse_x, mouse_y = event.pos
            player_position = (mouse_x + player_offset_x,
                               mouse_y + player_offset_y)

        elif event.type == pygame.MOUSEMOTION and dragging_player and selected_object == 'player':
            mouse_x, mouse_y = event.pos
            player_position[0] = mouse_x + player_offset_x
            player_position[1] = mouse_y + player_offset_y

        elif dragging_target and selected_object == 'target':
            mouse_x, mouse_y = event.pos
            target_position = (mouse_x + target_offset_x,
                               mouse_y + target_offset_y)

        elif dragging_triangle and selected_object == 'triangle':
            mouse_x, mouse_y = event.pos
            triangle_points = [add(p, (mouse_x, mouse_y))
                               for p in triangle_offset]

        elif event.type == pygame.MOUSEMOTION and dragging_wall:
            mouse_x, mouse_y = event.pos
            selected_object = 'whole wall'
            if wall_drag_mode == "whole":
                dx = mouse_x - original_wall_start_pos[0]
                dy = mouse_y - original_wall_start_pos[1]
                # Apply movement to both points
                wall_start_pos = (
                    original_wall_start_pos[0] + dx, original_wall_start_pos[1] + dy)
                wall_end_pos = (
                    original_wall_end_pos[0] + dx, original_wall_end_pos[1] + dy)
            elif wall_drag_mode == "start":
                wall_start_pos = (mouse_x, mouse_y)
            elif wall_drag_mode == "end":
                wall_end_pos = (mouse_x, mouse_y)

            elif wall_drag_start is True:
                wall_start_pos = (mouse_x, mouse_y)
            elif wall_drag_start is False:
                wall_end_pos = (mouse_x, mouse_y)


# Fill Screen with black
    screen.fill(BLACK)

# Render the edit moode status text on screen:

    edit_mode_text = font.render(
        f'Edit Mode: {"ON" if is_edit_mode else "OFF"}', True, WHITE)
    screen.blit(edit_mode_text, (10, 10))


# If in edit mode and hovering over player highlight it:
    # highlight player
    if is_edit_mode and is_hovering(pygame.mouse.get_pos(), player_position, player_radius):
        pygame.draw.circle(screen, WHITE, player_position,
                           player_radius + 2, 2)
    # highlight target
    elif is_edit_mode and is_hovering(pygame.mouse.get_pos(), target_position, target_radius):
        pygame.draw.circle(screen, RED, target_position, target_radius + 2, 2)

    # Highlight triangle
    elif is_edit_mode:
        if point_in_triangle(pygame.mouse.get_pos(), *triangle_points) or selected_object == 'triangle':

            pygame.draw.polygon(screen, triangle_color, triangle_points, 2)
    # Highlight wall
    if hovering_wall and is_edit_mode:
        # Highlight the wall if in edit mode and mouse is hovering over it
        pygame.draw.line(screen, wall_color, wall_start_pos,
                         wall_end_pos, wall_thickness + 4)
    else:
        # Draw the wall normally
        pygame.draw.line(screen, wall_color, wall_start_pos,
                         wall_end_pos, wall_thickness)

# Draw the player
    pygame.draw.circle(screen, player_color, player_position, player_radius)

# Draw the target
    pygame.draw.circle(screen, target_color, target_position, target_radius)

# Draw the wall
    pygame.draw.line(screen, wall_color, wall_start_pos,
                     wall_end_pos, wall_thickness)

# Draw the reflecting triangle
    pygame.draw.polygon(screen, triangle_color, triangle_points)

    # add outlines for other elements here


# Update the display
    pygame.display.flip()


# After updating display, check if we need to reset the dragging state

if not is_edit_mode or selected_object is None:
    dragging_player = False

# Quit Pygame
pygame.quit()
sys.exit()
