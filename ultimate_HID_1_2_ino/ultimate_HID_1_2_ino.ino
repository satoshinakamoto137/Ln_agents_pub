#include <Keyboard.h>
#include <Mouse.h>

String input = "";
bool humanMode = true;  // start in HUMAN if you like, but Python must flip to COMMAND

void setup() {
  Serial.begin(9600);
  Keyboard.begin();
  Mouse.begin();
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      input.trim();
      input.replace("\r", "");

      // Mode switches
      if (input == "MODE:HUMAN") { humanMode = true;  Serial.println("OK"); input=""; continue; }
      if (input == "MODE:COMMAND") { humanMode = false; Serial.println("OK"); input=""; continue; }

      // TYPE_ONLY always types text, regardless of mode
      if (input.startsWith("TYPE_ONLY:")) {
        String textToType = input.substring(10);
        Keyboard.print(textToType);
        Serial.println("OK");
        input = "";
        continue;
      }

      // COMMAND mode: interpret tokens
      if (!humanMode) {
        if (input == "ctrl+alt+t") {
          Keyboard.press(KEY_LEFT_CTRL); Keyboard.press(KEY_LEFT_ALT); Keyboard.press('t');
          delay(100); Keyboard.releaseAll();
        } else if (input == "ctrl+a") {
          Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('a');
          delay(100); Keyboard.releaseAll();
        } else if (input == "ctrl+s") {
          Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('s');
          delay(100); Keyboard.releaseAll();
        } else if (input == "ctrl+n") {
          Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('n');
          delay(100); Keyboard.releaseAll();
        } else if (input == "ctrl+c") {
          Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('c');
          delay(100); Keyboard.releaseAll();
        } else if (input == "ctrl+v") {
          Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('v');
          delay(100); Keyboard.releaseAll();
        } else if (input == "ctrl+w") {
          Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('w');
          delay(100); Keyboard.releaseAll();
        } else if (input == "ctrl+u") {
          Keyboard.press(KEY_LEFT_CTRL); Keyboard.press('u');
          delay(100); Keyboard.releaseAll();
        } else if (input.equalsIgnoreCase("TAB")) {
          Keyboard.press(KEY_TAB); delay(80); Keyboard.release(KEY_TAB);
        } else if (input == "KEY_RETURN") {
          Keyboard.press(KEY_RETURN); delay(80); Keyboard.release(KEY_RETURN);
        } else if (input == "ESC") {
          Keyboard.press(KEY_ESC); delay(80); Keyboard.release(KEY_ESC);
        } else if (input == "BACKSPACE") {
          Keyboard.press(KEY_BACKSPACE); delay(80); Keyboard.release(KEY_BACKSPACE);
        } else if (input == "MOVE X" || input == "X+") {
          Mouse.move(1, 0);
        } else if (input == "MOVE -X" || input == "X-") {
          Mouse.move(-1, 0);
        } else if (input == "MOVE Y" || input == "Y+") {
          Mouse.move(0, 1);
        } else if (input == "MOVE -Y" || input == "Y-") {
          Mouse.move(0, -1);
        } else if (input == "CLICK") {
          Mouse.click();
        } else if (input == "SCROLL UP") {
          Mouse.move(0, 0, 1);
        } else if (input == "SCROLL DOWN") {
          Mouse.move(0, 0, -1);
        } else if (input == "RIGHT_CLICK") {
          Mouse.click(MOUSE_RIGHT);
        } else if (input == "MIDDLE_CLICK") {
          Mouse.click(MOUSE_MIDDLE);
        } else if (input == "PING") {
          Serial.println("PONG");
          input = "";
          continue;
        } else {
          // default in COMMAND mode: type it
          if (input.length() > 0) Keyboard.print(input);
        }
        Serial.println("OK");
      } else {
        // HUMAN mode: default is to type whatever line arrives
        if (input.length() > 0) Keyboard.print(input);
        Serial.println("OK");
      }

      input = ""; // clear buffer
    } else {
      // accumulate until newline; DO NOT print characters here
      input += c;
    }
  }
}
