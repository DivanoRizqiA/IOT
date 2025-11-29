import math

def detect_step(ax, ay, az, threshold=1.1):
    magnitude = math.sqrt(ax**2 + ay**2 + az**2)
    if magnitude > threshold:
        return True
    return False

def calories_from_steps(step_count, weight_kg=70):
    return step_count * 0.04 * weight_kg
