import serial
import time
import random

CONTROL = b"\x02"  # STX sentinel
ARDUINO_PORT = "/dev/ttyACM2"  # Update this to your Arduino port
BAUD_RATE = 9600

def gaussian_delay(mean=0.08, stddev=0.02, max_time=0.3):
    delay = min(max(0, random.gauss(mean, stddev)), max_time)
    time.sleep(delay)
    return delay

def lognormal_delay(mu=0.05, sigma=0.04, max_time=0.4):
    delay = min(random.lognormvariate(mu, sigma), max_time)
    time.sleep(delay)
    return delay

def delay_for(type="lognormal", max_time=0.4):
    if type == "gaussian":
        return gaussian_delay(max_time=max_time)
    else:
        return lognormal_delay(max_time=max_time)

def message_write(message):
    """
    Write a message to the serial port.
    """
    port = ARDUINO_PORT
    baud = BAUD_RATE
    ser = serial.Serial(port, baud, timeout=1)

    def send(cmd, pause=True):
        ser.write((cmd + "\n").encode())
    
    send(message)                             # Search


def mimick_human_write(message, type='lognormal', max_time=0.5): #works with ino1_2
    port = ARDUINO_PORT
    baud = BAUD_RATE
    ser = serial.Serial(port, baud, timeout=1)

    def delay_function():
        if type == 'gaussian':
            return gaussian_delay(max_time=max_time)
        else:
            return lognormal_delay(max_time=max_time)

    for char in message:
        ser.write(char.encode())
        ser.write(b'\n') 
        delay_function()

    ser.close()

class Actions:
    def __init__(self, port=ARDUINO_PORT, baud=BAUD_RATE, delay_type='lognormal', max_delay=0.4):
        self.port = port
        self.baud = baud
        self.ser = serial.Serial(port, baud, timeout=1)
        self.delay_type = delay_type
        self.max_delay = max_delay
        time.sleep(2)  # Wait for Arduino

    def send(self, command):
        self.ser.write((command + '\n').encode())

    def type(self, text, delay=None, max_time=None):
        delay = delay or self.delay_type
        max_time = max_time or self.max_delay
        for char in f"TYPE_ONLY:{text}":
            self.ser.write(char.encode())
            delay_for(delay, max_time)
        self.ser.write(b'\n')

    def combo(self, combo_str):
        self.send(combo_str)

    def press_tab(self, repeat=1, delay_type=None, max_time=None):
        delay_type = delay_type or self.delay_type
        max_time = max_time or self.max_delay
        for _ in range(repeat):
            self.send("TAB")
            time.sleep(0.05)  # 💡 pequeño respiro para Arduino (50 ms o ajustable)
            delay_for(delay_type, max_time)

    def press_enter(self, delay=None, max_time=None):
        self.send("KEY_RETURN")
        delay_for(delay or self.delay_type, max_time or self.max_delay)

    def press_esc(self):
        self.send("ESC")

    def press_backspace(self):
        self.send("BACKSPACE")

    def press_space(self):
        self.send("SPACE")

    def mouse_move(self, direction):
        valid = ["X+", "X-", "Y+", "Y-", "MOVE X", "MOVE -X", "MOVE Y", "MOVE -Y"]
        if direction in valid:
            self.send(direction)

    def click(self):
        self.send("CLICK")

    def right_click(self):
        self.send("RIGHT_CLICK")

    def middle_click(self):
        self.send("MIDDLE_CLICK")

    def scroll_up(self):
        self.send("SCROLL UP")

    def scroll_down(self):
        self.send("SCROLL DOWN")

    def up_arrow(self):
        self.send("UP_ARROW")

    def down_arrow(self):
        self.send("DOWN_ARROW")

    def left_arrow(self):
        self.send("LEFT_ARROW")

    def right_arrow(self):
        self.send("RIGHT_ARROW")

    def set_mode_b(self, mode="COMMAND"):
        if mode.upper() in ["COMMAND", "HUMAN"]:
            self.send(f"MODE:{mode.upper()}")

    def repeat_command(self, command, repeat=1, delay_type=None, max_time=None):
        delay_type = delay_type or self.delay_type
        max_time = max_time or self.max_delay
        for _ in range(repeat):
            self.send(command)
            delay_for(delay_type, max_time)

    def ping(self):
        self.send("PING")

    def _set_mode(self, mode):
        # Prepend sentinel so Arduino won't echo the letters
        self.ser.write(CONTROL + f"MODE:{mode}\n".encode())
        time.sleep(0.05)

    def type_human(self, text, delay_type=None, max_time=None, restore_mode="COMMAND"):
        delay_type = delay_type or self.delay_type
        max_time = max_time or self.max_delay

        # Activar live typing
        self.ser.write(CONTROL + b"MODE:HUMAN_LIVE\n")
        time.sleep(0.05)

        # Mandar los caracteres uno por uno con delay
        for ch in text:
            self.ser.write(ch.encode())      # 👈 sin newline aquí
            delay_for(delay_type, max_time)

        # Restaurar modo COMMAND
        if restore_mode:
            time.sleep(0.05)
            self.ser.write(CONTROL + f"MODE:{restore_mode}\n".encode())
            time.sleep(0.05)


        # Finish the line for your shell/editor if you want (optional):
        # self.ser.write(b"\n")

        # Restore to COMMAND safely (again with sentinel)
        if restore_mode:
            time.sleep(0.05)
            self.ser.write(CONTROL + f"MODE:{restore_mode}\n".encode())
            time.sleep(0.05)

def human_somo_chingones_test():

    # 7 TABs with lognormal delays
    #actions.press_tab(repeat=3, delay_type="lognormal", max_time=0.5)

    # Type "Hello World" with Gaussian delays
    
    #mimick_human_write("Hello World", type="gaussian", max_time=0.5)

    actions = Actions(delay_type="lognormal", max_delay=0.5)
    time.sleep(2)

    # Paso 1: abrir terminal con Ctrl+Alt+T
    actions.combo("ctrl+alt+t")
    time.sleep(1)   # dale chance a la terminal de abrir

    # Paso 2: cambiar a modo humano live typing
    actions._set_mode("HUMAN_LIVE")

    # Paso 3: escribir como humano con delays
    actions.type_human("somo chingones!", delay_type="lognormal", max_time=0.5)

    # Paso 4: presionar Enter
    actions.press_enter()

    # Paso 5: volver a COMMAND (opcional, para siguientes comandos)
    actions._set_mode("COMMAND")


#if __name__ == "__main__": #open terminal and write "somos chingones at "

    # 7 TABs with lognormal delays
    #actions.press_tab(repeat=3, delay_type="lognormal", max_time=0.5)
    #print('XD')