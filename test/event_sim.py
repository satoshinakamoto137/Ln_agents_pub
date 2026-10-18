# ============================================
# 🐉 Himeryu Event Simulation Engine
# ============================================
import random
import time
from datetime import datetime

# === Delay Models ===
def gaussian_delay(mean=0.08, stddev=0.02, max_time=0.3):
    delay = min(max(0, random.gauss(mean, stddev)), max_time)
    time.sleep(delay)
    return delay

def lognormal_delay(mu=0.05, sigma=0.04, max_time=0.4):
    delay = min(random.lognormvariate(mu, sigma), max_time)
    time.sleep(delay)
    return delay

# === Event Simulator ===
#def simulate_event_stream(mu=1.0, sigma=0.5, duration_seconds=30):
def simulate_event_stream(mu=2.71, sigma=0.33, duration_seconds=30):

    """
    Simula cada segundo un número que representa los minutos
    hasta que ocurra un evento futuro. Usa distribución log-normal.
    """
    start_time = time.time()
    print(f"🚀 Starting Himeryu Event Simulation at {datetime.now()}")
    print(f"📈 Using log-normal distribution (μ={mu}, σ={sigma}) for event delay (minutes)\n")

    counter = 0
    while time.time() - start_time < duration_seconds:
        counter += 1

        # Generar número log-normal -> minutos hasta evento
        event_minutes = round(random.lognormvariate(mu, sigma), 2)
        timestamp = datetime.now().strftime("%H:%M:%S")

        print(f"[{timestamp}] Event {counter:03d} → next in {event_minutes} minutes")

        # Esperar ~1 segundo entre mediciones (con microvariación)
        lognormal_delay(mu=0.05, sigma=0.04, max_time=0.4)

    print("\n✅ Simulation complete!")
    print(f"Total events generated: {counter}")

# === Run Example ===
if __name__ == "__main__":
    simulate_event_stream()
