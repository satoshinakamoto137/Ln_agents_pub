#include <Keyboard.h>
#include <Mouse.h>

String input = "";
bool humanMode = true;      // MODO HUMANO por defecto
bool liveTyping = false;    // HUMAN_LIVE: eco por char en cuanto llega
bool suppressEcho = false;  // Sentinel 0x02: suprime eco hasta '\n'

void setup() {
  Serial.begin(9600);
  Keyboard.begin();
  Mouse.begin();
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      // Se terminó una línea (comando o texto)
      input.trim();
      input.replace("\r", "");

      // ---- Cambios de modo ----
      if (input == "MODE:HUMAN") {
        humanMode = true;
        liveTyping = false;
        Serial.println("OK");
        suppressEcho = false;
        input = "";
        continue;
      }
      if (input == "MODE:HUMAN_LIVE") {
        humanMode = true;
        liveTyping = true;
        Serial.println("OK");
        suppressEcho = false;
        input = "";
        continue;
      }
      if (input == "MODE:COMMAND") {
        humanMode = false;
        liveTyping = false;
        Serial.println("OK");
        suppressEcho = false;
        input = "";
        continue;
      }

      // ---- TYPE_ONLY: siempre imprime el payload tal cual ----
      if (input.startsWith("TYPE_ONLY:")) {
        String textToType = input.substring(10);
        Keyboard.print(textToType);
        Serial.println("OK");
        suppressEcho = false;
        input = "";
        continue;
      }

      // ---- COMMAND MODE ----
      if (!humanMode) {
        if (input == "ctrl+alt+t") { Keyboard.press(KEY_LEFT_CTRL); Keyboard.press(KEY_LEFT_ALT); Keyboard.press('t'); delay(100); Keyboard.releaseAll(); }
        else if (input == "ctrl+a") { Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('a'); delay(100); Keyboard.releaseAll(); }
        else if (input == "ctrl+s") { Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('s'); delay(100); Keyboard.releaseAll(); }
        else if (input == "ctrl+n") { Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('n'); delay(100); Keyboard.releaseAll(); }
        else if (input == "ctrl+c") { Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('c'); delay(100); Keyboard.releaseAll(); }
        else if (input == "ctrl+v") { Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('v'); delay(100); Keyboard.releaseAll(); }
        else if (input == "ctrl+w") { Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('w'); delay(100); Keyboard.releaseAll(); }
        else if (input == "ctrl+u") { Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('u'); delay(100); Keyboard.releaseAll(); }
        else if (input.equalsIgnoreCase("TAB")) { Keyboard.press(KEY_TAB); delay(80); Keyboard.release(KEY_TAB); }
        else if (input == "KEY_RETURN") { Keyboard.press(KEY_RETURN); delay(80); Keyboard.release(KEY_RETURN); }
        else if (input == "ESC") { Keyboard.press(KEY_ESC); delay(80); Keyboard.release(KEY_ESC); }
        else if (input == "BACKSPACE") { Keyboard.press(KEY_BACKSPACE); delay(80); Keyboard.release(KEY_BACKSPACE); }
        else if (input == "MOVE X" || input == "X+") { Mouse.move(1, 0); }
        else if (input == "MOVE -X" || input == "X-") { Mouse.move(-1, 0); }
        else if (input == "MOVE Y" || input == "Y+") { Mouse.move(0, 1); }
        else if (input == "MOVE -Y" || input == "Y-") { Mouse.move(0, -1); }
        else if (input == "CLICK") { Mouse.click(); }
        else if (input == "SCROLL UP") { Mouse.move(0, 0, 1); }
        else if (input == "SCROLL DOWN") { Mouse.move(0, 0, -1); }
        else if (input == "RIGHT_CLICK") { Mouse.click(MOUSE_RIGHT); }
        else if (input == "MIDDLE_CLICK") { Mouse.click(MOUSE_MIDDLE); }
        else if (input == "PING") { Serial.println("PONG"); suppressEcho = false; input=""; continue; }
        else {
          // por compat: si no coincide, escribe tal cual
          if (input.length() > 0) Keyboard.print(input);
        }
        Serial.println("OK");
      } else {
        // ---- HUMAN / HUMAN_LIVE al recibir '\n' ----
        // En HUMAN normal: imprime el buffer completo como bloque
        // En HUMAN_LIVE: ¡NO imprimas el buffer! (ya se ecoó char-a-char)
        if (!liveTyping && input.length() > 0) {
          Keyboard.print(input);
        }
        Serial.println("OK");
      }

      // limpiar estado de línea
      suppressEcho = false;   // importante para el sentinel
      input = "";
    } else {
      // ---- lectura byte a byte ----

      // Sentinel de control (STX = 0x02): desactiva eco hasta el próximo '\n'
      if ((unsigned char)c == 0x02) {
        suppressEcho = true;
        continue;
      }

      // acumular en buffer para cuando llegue '\n'
      input += c;

      // En HUMAN_LIVE: eco inmediato de cada char (si no suprimido)
      if (humanMode && liveTyping && !suppressEcho) {
        if (c != '\r' && c != '\n') {
          Keyboard.write(c);  // incluye espacios y puntuación
        }
      }
    }
  }
}
