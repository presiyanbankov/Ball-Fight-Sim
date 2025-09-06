import pygame
import math
import numpy as np
import sys
import colorsys


class Ball:
    def __init__(self, type, position, velocity, radius, gravity, damage, hue, hue_speed, area, image):
        self.type = type
        self.pos = np.array(position, dtype=np.float64)
        self.vel = np.array(velocity, dtype=np.float64)
        self.radius = radius
        self.gravity = gravity
        self.dmg = damage
        self.last_dmg = 0
        self.hue = hue
        self.hue_speed = hue_speed
        self.area = area
        self.borders = [area.center[0] - RECT_WIDTH / 2 + 2, area.center[1] - RECT_HEIGHT / 2 + 2,
                        area.center[0] + RECT_WIDTH / 2 - 2, area.center[1] + RECT_HEIGHT / 2 - 2]
        self.current_box = 0
        self.boxes = [Box((area.center[0], area.center[1] - 150), (RECT_WIDTH, 150), 100),
                      Box((area.center[0], area.center[1]), (RECT_WIDTH, 150), 10000),
                      Box((area.center[0], area.center[1] + 150), (RECT_WIDTH, 150), 1000000),
                      Box((area.center[0], area.center[1] + 300), (RECT_WIDTH, 150), math.inf)]
        self.img = image


class Box:
    def __init__(self, center, size, health):
        self.center = center
        self.size = size
        self.health = health


SCALE = 3
pygame.init()
WIDTH = 450
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), depth=32)
high_res = pygame.Surface((WIDTH * SCALE, HEIGHT * SCALE), depth=32)
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = screen.get_size()
HEIGHT *= SCALE
WIDTH *= SCALE
clock = pygame.time.Clock()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CHARCOAL = (54, 69, 79)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
font = pygame.font.SysFont('calibri', 25, bold=False)
title_font = pygame.font.SysFont('calibri', 50, bold=True)
CENTER = (WIDTH // 2, HEIGHT // 2)

RECT_WIDTH = 300 * SCALE
RECT_HEIGHT = 250 * SCALE
rect1 = pygame.Rect(0, 0, RECT_WIDTH, RECT_HEIGHT)
rect2 = pygame.Rect(0, 0, RECT_WIDTH, RECT_HEIGHT)
rect1.center = (CENTER[0], CENTER[1] - 200 * SCALE)
rect2.center = (CENTER[0], CENTER[1] + 200 * SCALE)

BALL_RADIUS = 15 * SCALE
fibo_pos = np.array([rect1.center[0], rect1.center[1] - 100 * SCALE], dtype=np.float64)
fibo_vel = np.array([0.5 * SCALE, 0.03 * SCALE], dtype=np.float64)
striker_pos = np.array([rect2.center[0], rect2.center[1] - 100 * SCALE], dtype=np.float64)
striker_vel = np.array([1 * SCALE, 1 * SCALE], dtype=np.float64)

fibo_img = pygame.image.load("phi.png").convert_alpha()
fibo_img = pygame.transform.smoothscale(fibo_img, (32 * SCALE, 32 * SCALE))

striker_img = pygame.image.load("sword.png").convert_alpha()
striker_img = pygame.transform.smoothscale(striker_img, (20 * SCALE, 20 * SCALE))

fibo = Ball("fibo", fibo_pos, fibo_vel, BALL_RADIUS, 0.01 * SCALE, 1, 0, 0.001, rect1, fibo_img)
striker = Ball("striker", striker_pos, striker_vel, BALL_RADIUS, 0.072 * SCALE, 1000, 0, 0, rect2, striker_img)

finish_cols = 30
finish_rows = 5
border_thickness = 3

balls = [fibo, striker]

fibo_bounce_sfx = pygame.mixer.Sound("fibonacci_bounce.mp3")
striker_bounce_sfx = pygame.mixer.Sound("striker_bounce.mp3")

running = True
finished = False


def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def render_text_surface(text, font_obj, color):
    return font_obj.render(text, True, color)


pygame.time.delay(1000)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    high_res.fill(CHARCOAL)

    if not finished:
        for ball in balls:
            ball.vel[1] += ball.gravity
            ball.pos += ball.vel
            ball.hue += ball.hue_speed
            if ball.hue > 1:
                ball.hue -= 1
            if ball.boxes:
                ball.borders[3] = ball.boxes[0].center[1] - ball.boxes[0].size[1] / 2
            else:
                ball.borders[3] = ball.area.center[1] + RECT_HEIGHT / 2 - 2

            if ball.pos[0] - ball.radius < ball.borders[0]:
                ball.pos[0] = ball.borders[0] + ball.radius
                ball.vel[0] = -0.99 * ball.vel[0]
            if ball.pos[0] + ball.radius > ball.borders[2]:
                ball.pos[0] = ball.borders[2] - ball.radius
                ball.vel[0] = -0.99 * ball.vel[0]
            if ball.pos[1] - ball.radius < ball.borders[1]:
                ball.pos[1] = ball.borders[1] + ball.radius
                ball.vel[1] = -0.99 * ball.vel[1]
            if ball.pos[1] + ball.radius > ball.borders[3]:
                ball.pos[1] = ball.borders[3] - ball.radius
                ball.vel[1] = -0.99 * ball.vel[1]
                if ball.type == "fibo":
                    fibo_bounce_sfx.play()
                elif ball.type == "striker":
                    striker_bounce_sfx.play()

                if ball.boxes:
                    if math.isinf(ball.boxes[0].health):
                        finished = True
                    ball.boxes[0].health -= ball.dmg
                if ball.type == "fibo":
                    temp = ball.dmg
                    ball.dmg += ball.last_dmg
                    ball.last_dmg = temp
                elif ball.type == "striker":
                    ball.dmg += 1000

            if ball.boxes and ball.boxes[0].health <= 0:
                if ball.type == "fibo":
                    ball.gravity *= 2
                ball.boxes.pop(0)

    for ball in balls:
        pygame.draw.rect(high_res, WHITE, ball.area, 2 * SCALE)
        ball_color = hsv_to_rgb(ball.hue, 1, 1)
        pygame.draw.circle(high_res, ball_color, (int(ball.pos[0]), int(ball.pos[1])), ball.radius)
        pygame.draw.circle(high_res, BLACK, (int(ball.pos[0]), int(ball.pos[1])), ball.radius, 2 * SCALE)
        ball_img_center = ball.pos - ball.img.get_width() // 2
        high_res.blit(ball.img, ball_img_center)

        for box in ball.boxes:
            box_rect = pygame.Rect(0, 0, box.size[0], box.size[1])
            box_rect.center = box.center

            if math.isinf(box.health):

                for i in range(finish_rows):
                    for j in range(finish_cols):
                        if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1):
                            small_rect_color = BLACK
                        else:
                            small_rect_color = WHITE
                        pygame.draw.rect(high_res, small_rect_color,
                                         (box.center[0] - box.size[0] / 2 + j * box.size[0] / finish_cols,
                                          box.center[1] - box.size[1] / 2 + i * box.size[1] / finish_rows,
                                          box.size[0] / finish_cols, box.size[1] / finish_rows))
            else:
                box_text = pygame.font.SysFont('calibri', int(30 * SCALE * 0.8)).render(f"{int(box.health)}", True,
                                                                                        WHITE)
                box_text_rect = box_text.get_rect(center=box.center)
                high_res.blit(box_text, box_text_rect)
            pygame.draw.rect(high_res, WHITE, box_rect, 1 * SCALE)

    scaled = pygame.transform.smoothscale(high_res, (ORIGINAL_WIDTH, ORIGINAL_HEIGHT))
    screen.blit(scaled, (0, 0))

    fibo_damage_text = font.render(f"Damage: {fibo.dmg}", True, WHITE)
    striker_damage_text = font.render(f"Damage: {striker.dmg}", True, WHITE)

    title_text1 = title_font.render(f"Fibonacci", True, hsv_to_rgb(fibo.hue, 1, 1))
    title_text1_rect = title_text1.get_rect(center=(ORIGINAL_WIDTH // 2, ORIGINAL_HEIGHT // 2 - 45))

    title_text2 = title_font.render("VS", True, WHITE)
    title_text2_rect = title_text2.get_rect(center=(ORIGINAL_WIDTH // 2, ORIGINAL_HEIGHT // 2))

    title_text3 = title_font.render(f"Striker", True, hsv_to_rgb(striker.hue, 1, 1))
    title_text3_rect = title_text3.get_rect(center=(ORIGINAL_WIDTH // 2, ORIGINAL_HEIGHT // 2 + 45))

    for dx in range(-border_thickness, border_thickness + 1):
        for dy in range(-border_thickness, border_thickness + 1):
            if dx ** 2 + dy ** 2 <= border_thickness ** 2:
                text1_border_surface = title_font.render(f"Fibonacci", True, BLACK)
                text2_border_surface = title_font.render("VS", True, BLACK)
                text3_border_surface = title_font.render(f"Striker", True, BLACK)
                text1_border_rect = text1_border_surface.get_rect(center= (ORIGINAL_WIDTH // 2 + dx, ORIGINAL_HEIGHT // 2 - 45 + dy))
                text2_border_rect = text2_border_surface.get_rect(center=(ORIGINAL_WIDTH // 2 + dx, ORIGINAL_HEIGHT // 2 + dy))
                text3_border_rect = text3_border_surface.get_rect(center=(ORIGINAL_WIDTH // 2 + dx, ORIGINAL_HEIGHT // 2 + 45 + dy))

                screen.blit(text1_border_surface, text1_border_rect)
                screen.blit(text2_border_surface, text2_border_rect)
                screen.blit(text3_border_surface, text3_border_rect)

    screen.blit(fibo_damage_text, (70,50))
    screen.blit(striker_damage_text, (220, 730))
    screen.blit(title_text1, title_text1_rect)
    screen.blit(title_text2, title_text2_rect)
    screen.blit(title_text3, title_text3_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
