# NeuroGrip – Smart Prosthetic Hand Simulation

A Python simulation exploring EMG-driven control logic for a smart prosthetic hand. It models simulated muscle activation/EMG signal levels and maps them to grip modes and finger closure states.

## Key Features
- Simulated EMG signal generation and amplitude/RMS processing.
- Grip mode classification (`Rest`, `Precision Pinch`, `Cylindrical Grasp`, `Power Grip`).
- Finger closure percentage mapping for prosthetic hand actuation logic.
- Interactive `Pygame` simulation interface (`pygame_ui.py`) with smooth EMG interpolation, keyboard shortcuts, and an interactive slider.

## Grip Modes & EMG Thresholds
The simulation maps normalized EMG values (`0.0` to `1.0`) to four grip modes:

- **Rest (`EMG < 0.20`)**: Low/baseline muscle activation; all fingers follow a gentle proportional closure (`EMG * 40`).
- **Precision Pinch (`0.20 <= EMG < 0.45`)**: Fine grip between Thumb (`72%`) and Index (`75%`) fingers, while Middle (`18%`), Ring (`12%`), and Little (`10%`) remain mostly open.
- **Cylindrical Grasp (`0.45 <= EMG < 0.70`)**: Balanced mid-range closure across all five fingers (`62%–70%`) for grasping cylindrical objects.
- **Power Grip (`EMG >= 0.70`)**: High-force closure across all fingers (`88%` base, scaling up to `100%` as `EMG` increases).

## Running the Simulation UI
Make sure `pygame` is installed on Python 3.13:

```bash
py -3.13 -m pip install pygame
py -3.13 pygame_ui.py
```

## Controls
- `1`: Set target EMG to `0.10` (`Rest`)
- `2`: Set target EMG to `0.35` (`Precision Pinch`)
- `3`: Set target EMG to `0.58` (`Cylindrical Grasp`)
- `4`: Set target EMG to `0.90` (`Power Grip`)
- `Space`: Assign a random target EMG value between `0.0` and `1.0`
- **Mouse Slider**: Drag the target EMG slider to adjust target signal levels smoothly

## Future Hardware Extension
- Integrate real surface EMG sensors (sEMG), signal filtering, and servo/motor control loops on a microcontroller.
