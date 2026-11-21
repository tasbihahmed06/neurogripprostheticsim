import random
import time

def generate_emg_signal():
    """Simulate muscle activation signal."""
    return random.uniform(0, 1)

def classify_grip(emg):
    """Classify grip mode based on EMG activation."""

    if emg < 0.2:
        return "Rest"

    elif emg < 0.4:
        return "Precision Pinch"

    elif emg < 0.7:
        return "Cylindrical Grasp"

    else:
        return "Power Grip"


def control_fingers(emg):
    """Map EMG signal to finger closure percentage."""

    closure = min(emg * 100, 100)

    return {
        "Thumb": closure,
        "Index": closure,
        "Middle": closure,
        "Ring": closure,
        "Little": closure
    }


def main():
    print("NeuroGrip - Smart Prosthetic Hand Simulation")
    print("-" * 45)

    for i in range(10):
        emg = generate_emg_signal()
        grip = classify_grip(emg)
        fingers = control_fingers(emg)

        print(f"\nEMG Signal: {emg:.2f}")
        print(f"Grip Mode: {grip}")

        for finger, value in fingers.items():
            print(f"{finger}: {value:.1f}% closed")

        time.sleep(1)


if __name__ == "__main__":
    main()
