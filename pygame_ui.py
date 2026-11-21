from collections import deque
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
    return {
        k: 88.0 + (eng - 0.70) * 40
        for k in ["Thumb", "Index", "Middle", "Ring", "Little"]
    }


def draw_hand_schematic(
    surface: pygame.Surface,
    closures: dict,
    font: pygame.font.Font,
    rect: pygame.Rect,
):
  """Draws 5 fingers closing/opening dynamically based on closure percentages."""
  pygame.draw.rect(surface, (28, 33, 43), rect, border_radius=10)
  pygame.draw.rect(surface, (60, 70, 88), rect, 2, border_radius=10)

  header = font.render("Finger Closure Visual", True, (215, 222, 235))
  surface.blit(header, (rect.x + 14, rect.y + 10))

  order = ["Thumb", "Index", "Middle", "Ring", "Little"]
  palm_rect = pygame.Rect(rect.x + 28, rect.bottom - 52, rect.width - 56, 22)
  pygame.draw.rect(surface, (75, 86, 106), palm_rect, border_radius=6)

  max_len = 115
  min_len = 24
  col_w = (rect.width - 40) / len(order)

  for idx, finger in enumerate(order):
    pct = max(0.0, min(100.0, closures.get(finger, 0.0)))
    cur_len = max_len - (pct / 100.0) * (max_len - min_len)

    center_x = int(rect.x + 20 + (idx + 0.5) * col_w)
    finger_w = 24
    base_y = palm_rect.top
    top_y = int(base_y - cur_len)

    finger_rect = pygame.Rect(
        center_x - finger_w // 2, top_y, finger_w, int(cur_len)
    )
    pygame.draw.rect(surface, (85, 175, 255), finger_rect, border_radius=6)
    pygame.draw.circle(surface, (220, 240, 255), (center_x, top_y), 5)

    short_label = font.render(finger[:3], True, (190, 200, 215))
    surface.blit(
        short_label,
        (center_x - short_label.get_width() // 2, palm_rect.bottom + 4),
    )


def draw_emg_plot(
    surface: pygame.Surface,
    history: deque,
    target_val: float,
    font: pygame.font.Font,
    rect: pygame.Rect,
):
  """Draws a real-time EMG signal trace inside rect."""
  pygame.draw.rect(surface, (28, 33, 43), rect, border_radius=10)
  pygame.draw.rect(surface, (60, 70, 88), rect, 2, border_radius=10)

  title = font.render("Live EMG Signal", True, (215, 222, 235))
  surface.blit(title, (rect.x + 14, rect.y + 10))

  plot_area = pygame.Rect(
      rect.x + 14, rect.y + 38, rect.width - 28, rect.height - 52
  )
  pygame.draw.rect(surface, (20, 24, 32), plot_area, border_radius=6)

  # Threshold guide lines (0.20, 0.45, 0.70)
  for th in (0.20, 0.45, 0.70):
    ty = int(plot_area.bottom - th * plot_area.height)
    pygame.draw.line(
        surface, (55, 62, 76), (plot_area.left, ty), (plot_area.right, ty), 1
    )

  # Target EMG dashed/horizontal reference line
  target_y = int(
      plot_area.bottom - max(0.0, min(1.0, target_val)) * plot_area.height
  )
  pygame.draw.line(
      surface,
      (255, 190, 60),
      (plot_area.left, target_y),
      (plot_area.right, target_y),
      1,
  )

  if len(history) > 1:
    points = []
    n = len(history)
    for i, val in enumerate(history):
      px = plot_area.left + (i / (n - 1)) * plot_area.width
      clamped = max(0.0, min(1.0, val))
      py = plot_area.bottom - clamped * plot_area.height
      points.append((px, py))
    pygame.draw.lines(surface, (70, 215, 145), False, points, 3)


def main():
  pygame.init()
  width, height = 900, 560
  screen = pygame.display.set_mode((width, height))
  pygame.display.set_caption("NeuroGrip - Smart Prosthetic Hand Simulation")
  clock = pygame.time.Clock()
  fps = 60
  font = pygame.font.SysFont("arial", 20)
  small_font = pygame.font.SysFont("arial", 16)
  big_font = pygame.font.SysFont("arial", 28, bold=True)

  target_eng = 0.25
  current_eng = target_eng
  dragging_slider = False
  emg_history = deque([current_eng] * 140, maxlen=140)

  slider_rect = pygame.Rect(80, 445, 500, 12)
  hand_box = pygame.Rect(615, 155, 250, 215)
  plot_box = pygame.Rect(615, 385, 250, 145)

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
        knob_rect = pygame.Rect(
            knob_x - 12, slider_rect.centery - 12, 24, 24
        )
        if knob_rect.collidepoint(event.pos) or slider_rect.inflate(
            0, 16
        ).collidepoint(event.pos):
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
    emg_history.append(current_eng)

    grip_mode = classify_grip(current_eng)
    closures = compute_finger_closures(current_eng)

    # --- Draw ---
    screen.fill((22, 26, 34))

    title_surf = big_font.render(
        "NeuroGrip - Smart Prosthetic Hand Simulation", True, (235, 240, 248)
    )
    screen.blit(title_surf, (40, 30))

    mode_surf = font.render(
        f"Grip Mode: {grip_mode}   |   EMG: {current_eng:.2f}",
        True,
        (110, 215, 255),
    )
    screen.blit(mode_surf, (40, 75))

    help_surf = font.render(
        "Keys: [1] Rest  [2] Pinch  [3] Cylindrical  [4] Power  [Space] Random",
        True,
        (165, 175, 190),
    )
    screen.blit(help_surf, (40, 110))

    # Draw finger closure bars
    y_pos = 160
    for finger, pct in closures.items():
      clamped_pct = max(0.0, min(100.0, pct))
      label = font.render(
          f"{finger:7s}: {clamped_pct:5.1f}%", True, (220, 225, 235)
      )
      screen.blit(label, (80, y_pos))

      bar_bg = pygame.Rect(240, y_pos + 4, 340, 20)
      pygame.draw.rect(screen, (45, 52, 66), bar_bg, border_radius=6)

      bar_fill = pygame.Rect(
          240, y_pos + 4, int(340 * clamped_pct / 100.0), 20
      )
      pygame.draw.rect(screen, (60, 190, 130), bar_fill, border_radius=6)

      y_pos += 42

    # Draw EMG slider
    pygame.draw.rect(screen, (65, 75, 92), slider_rect, border_radius=6)
    knob_x = slider_rect.x + int(target_eng * slider_rect.width)
    pygame.draw.circle(
        screen, (255, 190, 60), (knob_x, slider_rect.centery), 12
    )

    slider_label = font.render(
        f"Target EMG Slider: {target_eng:.2f}", True, (240, 240, 240)
    )
    screen.blit(slider_label, (80, 470))

    # Draw visual hand & live EMG plot
    draw_hand_schematic(screen, closures, small_font, hand_box)
    draw_emg_plot(screen, emg_history, target_eng, small_font, plot_box)

    pygame.display.flip()

  pygame.quit()


if __name__ == "__main__":
  main()
