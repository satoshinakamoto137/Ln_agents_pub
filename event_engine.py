# ============================================
# 🐉 Himeryu Event Generator Engine (Hermetic Sequential Mode v2)
# ============================================
import random
import time
import subprocess
from datetime import datetime
import os, sys

# === Logging dual (pantalla + archivo) ===
os.makedirs("./logs", exist_ok=True)
log_path = f"./logs/himeryu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, data):
        for f in self.files:
            f.write(data)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

# Creamos el archivo de log y activamos la salida doble
log_file = open(log_path, "a", buffering=1)  # buffering=1 = line-buffered (inmediato)
sys.stdout = Tee(sys.__stdout__, log_file)
sys.stderr = sys.stdout

print(f"🌸 Himeryu Log initialized at {datetime.now()} → {log_path}")
print("--------------------------------------------------------------")

# === Delay Models ===
def lognormal_delay(mu=0.05, sigma=0.04, max_time=0.4):
    delay = min(random.lognormvariate(mu, sigma), max_time)
    time.sleep(delay)
    return delay


# === Acción individual del evento ===
def execute_event(event_id, script_path="event_launcher.py", timeout_seconds=600):
    """
    Ejecuta un evento como subproceso completamente independiente.
    """
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] 💖 Event {event_id:03d} started!")

    try:
        result = subprocess.run(
        ["python3", script_path],
        text=True,
        timeout=timeout_seconds,
        #stdout=sys.stdout,
        #stderr=sys.stderr,
        )


        now = datetime.now().strftime("%H:%M:%S")
        if result.returncode == 0:
            print(f"[{now}] ✅ Event {event_id:03d} completed successfully!")
        else:
            print(f"[{now}] ⚠️ Event {event_id:03d} returned non-zero code ({result.returncode})")
            print(f"stderr: {result.stderr.strip()}")

    except subprocess.TimeoutExpired:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] 💀 Event {event_id:03d} exceeded timeout and was killed.")
    except Exception as e:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] ❌ Event {event_id:03d} failed: {e}")
    finally:
        print("-" * 70)


# === Generador principal ===
def himeryu_event_generator(
    script_path="event_launcher.py",
    mu=2.71,
    sigma=0.33,
    total_events=10,
    timeout_flag=True,
    timeout_minutes=9,
):
    """
    Genera eventos independientes y secuenciales ejecutando scripts
    en procesos aislados (nuevo intérprete Python cada vez).
    """
    print(f"🚀 Starting Himeryu Event Generator (v2) at {datetime.now()}")
    print(f"📈 Using log-normal distribution (μ={mu}, σ={sigma}) for delay (minutes)")
    print(f"🔒 Hermetic Mode: full Python isolation per event.")
    print(f"⏱️ Timeout: {'Enabled (' + str(timeout_minutes) + ' min)' if timeout_flag else 'Disabled'}\n")

    timeout_seconds = timeout_minutes * 60 if timeout_flag else None

    for i in range(1, total_events + 1):
        event_minutes = round(random.lognormvariate(mu, sigma), 2)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ⏳ Event {i:03d} → executing in {event_minutes} minutes")

        # Esperar hasta el evento
        time.sleep(event_minutes * 60)

        # Limpieza previa (por si algo quedó atascado)
        #os.system("sudo fuser -k /dev/ttyACM0 >/dev/null 2>&1")

        execute_event(i, script_path, timeout_seconds=timeout_seconds)

        # Delay aleatorio entre eventos
        lognormal_delay(mu=0.05, sigma=0.04, max_time=0.4)

    print("🌸 All events executed sequentially with isolation and timeout control.\n")


# === Ejemplo de ejecución ===
if __name__ == "__main__":
    himeryu_event_generator(
        script_path="event_launcher.py",
        mu=2.71,
        sigma=0.33,
        total_events=4,
        timeout_flag=True,
        timeout_minutes=9,
    )
