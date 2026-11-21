import math
import random
import pygame


# --- Control Logic ---
def classify_grip(eng: float) -> str:
    if eng < 0.20:
        return "Rest"
    elif eng < 0.45:
        return "Precision Pinch"
    elif eng < 0.70:
        return "Cylindrical Grasp"
    else:
        return "Power Grip"


def compute_finger_closures(eng: float) -> dict:
    """Returns closure percentage (0.0 to 100.0) per finger based on EMG & grip mode."""
    eng = max(0.0, min(1.0, eng))
    grip = classify_grip(eng)

    if grip == "Rest":
        base = eng * 40
        return {k: base for k in ["Thumb", "Index", "Middle", "Ring", "Little"]}
    elif grip == "Precision Pinch":
        return {
            "Thumb": 72.0,
            "Index": 75.0,
            "Middle": 18.0,
            "Ring": 12.0,
            "Little": 10.0,
        }
    elif grip == "Cylindrical Grasp":
        return {
            "Thumb": 65.0,
            "Index": 68.0,
            "Middle": 70.0,
            "Ring": 66.0,
            "Little": 62.0,
        }
    else:  # Power Grip
        return {k: 88.0 + (eng - 0.70) * 40 for k in ["Thumb", "Index", "Middle", "Ring", "Little"]}


def main():
    pygame.init()
    width, height = 900, 560
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("NeuroGrip - Smart Prosthetic Hand Simulation")
    clock = pygame.time.Clock()
    fps = 60
    font = pygame.font.SysFont("arial", 20)
    big_font = pygame.font.SysFont("arial", 28, bold=True)

    target_eng = 0.25
    current_eng = target_eng
    dragging_slider = False

    slider_rect = pygame.Rect(80, 440, 500, 12)

    running = True
    while running:
        dt = clock.tick(fps) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    target_eng = 0.10
                elif event.key == pygame.K_2:
                    target_eng = 0.35
                elif event.key == pygame.K_3:
                    target_eng = 0.58
                elif event.key == pygame.K_4:
                    target_eng = 0.90
                elif event.key == pygame.K_SPACE:
                    target_eng = round(random.uniform(0.0, 1.0), 2)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                knob_x = slider_rect.x + int(target_eng * slider_rect.width)
                knob_rect = pygame.Rect(knob_x - 12, slider_rect.centery - 12, 24, 24)
                if knob_rect.collidepoint(event.pos) or slider_rect.inflate(0, 16).collidepoint(event.pos):
                    dragging_slider = True
                    rel_x = max(0, min(slider_rect.width, event.pos[0] - slider_rect.x))
                    target_eng = round(rel_x / slider_rect.width, 2)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_slider = False

            elif event.type == pygame.MOUSEMOTION and dragging_slider:
                rel_x = max(0, min(slider_rect.width, event.pos[0] - slider_rect.x))
                target_eng = round(rel_x / slider_rect.width, 2)

        # Smoothly move current_eng toward target_eng
        current_eng += (target_eng - current_eng) * min(1.0, dt * 8.0)
        grip_mode = classify_grip(current_eng)
        closures = compute_finger_closures(current_eng)

        # --- Draw ---
        screen.fill((22, 26, 34))

        title_surf = big_font.render("NeuroGrip - Smart Prosthetic Hand Simulation", True, (235, 240, 248))
        screen.blit(title_surf, (40, 30))

        mode_surf = font.render(f"Grip Mode: {grip_mode}   |   EMG: {current_eng:.2f}", True, (110, 215, 255))
        screen.blit(mode_surf, (40, 75))

        help_surf = font.render("Keys: [1] Rest  [2] Pinch  [3] Cylindrical  [4] Power  [Space] Random", True, (165, 175, 190))
        screen.blit(help_surf, (40, 110))

        # Draw finger closure bars
        y_pos = 165
        for finger, pct in closures.items():
            clamped_pct = max(0.0, min(100.0, pct))
            label = font.render(f"{finger:7s}: {clamped_pct:5.1f}%", True, (220, 225, 235))
            screen.blit(label, (80, y_pos))

            bar_bg = pygame.Rect(240, y_pos + 4, 340, 20)
            pygame.draw.rect(screen, (45, 52, 66), bar_bg, border_radius=6)

            bar_fill = pygame.Rect(240, y_pos + 4, int(340 * clamped_pct / 100.0), 20)
            pygame.draw.rect(screen, (60, 190, 130), bar_fill, border_radius=6)

            y_pos += 42

        # Draw EMG slider
        pygame.draw.rect(screen, (65, 75, 92), slider_rect, border_radius=6)
        knob_x = slider_rect.x + int(target_eng * slider_rect.width)
        pygame.draw.circle(screen, (255, 190, 60), (knob_x, slider_rect.centery), 12)

        slider_label = font.render(f"Target EMG Slider: {target_eng:.2f}", True, (240, 240, 240))
        screen.blit(slider_label, (80, 465))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()