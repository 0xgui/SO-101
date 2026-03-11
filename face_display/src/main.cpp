/*
 * SO-101 Face Display
 * ESP32-S3 SuperMini + 2.0" ST7789V 240x320 SPI TFT
 *
 * Wiring:
 *   Display   →  ESP32-S3 SuperMini
 *   ────────────────────────────────
 *   VCC       →  3.3V  (NOT 5V)
 *   GND       →  GND
 *   CS        →  GPIO 10
 *   DC        →  GPIO 2
 *   RST       →  GPIO 3
 *   SDA/MOSI  →  GPIO 11
 *   SCL/SCK   →  GPIO 12
 *   BLK       →  3.3V  (always on) or a GPIO for dimming
 *
 * Serial commands (115200 baud, newline-terminated):
 *   FACE:IDLE   FACE:HAPPY   FACE:SAD   FACE:BLINK   FACE:TALK
 *
 * Python integration example (LeRobot controller side):
 *   import serial
 *   face = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)
 *   face.write(b"FACE:HAPPY\n")
 */

#include <Arduino.h>
#include <TFT_eSPI.h>
#include "faces.h"

// ── Display + sprite ──────────────────────────────────────────────────────────
TFT_eSPI    tft;
TFT_eSprite sprite(&tft);
FaceRenderer renderer(sprite);

// ── State ─────────────────────────────────────────────────────────────────────
Expression  currentExpr    = EXPR_IDLE;
Expression  pendingExpr    = EXPR_IDLE;  // applied at next frame boundary
bool        exprChanged    = false;

uint32_t    animTick       = 0;
uint32_t    lastFrameMs    = 0;
const int   FRAME_MS       = 33;          // ~30 fps

// Auto-blink in IDLE: fires every ~4 s, lasts 3 frames
uint32_t    lastBlinkMs    = 0;
const int   BLINK_INTERVAL = 4000;        // ms between auto-blinks
const int   BLINK_FRAMES   = 3;
int         blinkFramesLeft = 0;

// BLINK expression: auto-return to IDLE after animation
const int   BLINK_EXPR_FRAMES = 6;
int         blinkExprLeft     = 0;

// TALK: auto-return to IDLE if no new command arrives within 3 s
uint32_t    talkLastCmdMs  = 0;
const int   TALK_TIMEOUT   = 3000;

// ── Serial input buffer ───────────────────────────────────────────────────────
static String inputBuf;

// ─────────────────────────────────────────────────────────────────────────────
//  Command parser
// ─────────────────────────────────────────────────────────────────────────────
void applyCommand(const String& raw) {
    String s = raw;
    s.trim();
    s.toUpperCase();

    if (!s.startsWith("FACE:")) return;
    String name = s.substring(5);

    for (int i = 0; i < EXPR_MAP_LEN; i++) {
        if (name == EXPR_MAP[i].name) {
            pendingExpr = EXPR_MAP[i].expr;
            exprChanged = true;

            if (pendingExpr == EXPR_TALK) talkLastCmdMs = millis();
            Serial.print("OK:");
            Serial.println(EXPR_MAP[i].name);
            return;
        }
    }
    Serial.println("ERR:unknown expression");
}

void readSerial() {
    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\n' || c == '\r') {
            if (inputBuf.length() > 0) {
                applyCommand(inputBuf);
                inputBuf = "";
            }
        } else if (inputBuf.length() < 64) {
            inputBuf += c;
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
//  Expression transition logic
// ─────────────────────────────────────────────────────────────────────────────
void updateExprState() {
    uint32_t now = millis();

    // Apply pending command
    if (exprChanged) {
        exprChanged   = false;
        currentExpr   = pendingExpr;
        blinkExprLeft = (currentExpr == EXPR_BLINK) ? BLINK_EXPR_FRAMES : 0;
        blinkFramesLeft = 0;  // cancel auto-blink if any
        animTick      = 0;
    }

    // BLINK expression: return to IDLE after N frames
    if (currentExpr == EXPR_BLINK) {
        if (blinkExprLeft > 0) {
            blinkExprLeft--;
        } else {
            currentExpr = EXPR_IDLE;
            animTick    = 0;
        }
    }

    // TALK timeout: return to IDLE if no recent FACE:TALK command
    if (currentExpr == EXPR_TALK && (now - talkLastCmdMs > TALK_TIMEOUT)) {
        currentExpr = EXPR_IDLE;
        animTick    = 0;
    }

    // Auto-blink in IDLE
    if (currentExpr == EXPR_IDLE) {
        if (blinkFramesLeft > 0) {
            blinkFramesLeft--;
        } else if (now - lastBlinkMs >= BLINK_INTERVAL) {
            lastBlinkMs     = now;
            blinkFramesLeft = BLINK_FRAMES;
        }
    } else {
        blinkFramesLeft = 0;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
//  Setup
// ─────────────────────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    // Short delay so USB CDC is ready on ESP32-S3
    delay(500);

    tft.init();
    tft.setRotation(0);          // portrait, USB at bottom
    tft.fillScreen(C_BG);
    tft.setSwapBytes(true);

    // 16-bit colour sprite (full screen buffer)
    sprite.setColorDepth(16);
    sprite.createSprite(240, 320);

    Serial.println("SO-101 face display ready.");
    Serial.println("Commands: FACE:IDLE  FACE:HAPPY  FACE:SAD  FACE:BLINK  FACE:TALK");
}

// ─────────────────────────────────────────────────────────────────────────────
//  Main loop
// ─────────────────────────────────────────────────────────────────────────────
void loop() {
    readSerial();

    uint32_t now = millis();
    if (now - lastFrameMs >= (uint32_t)FRAME_MS) {
        lastFrameMs = now;
        updateExprState();

        bool autoBlinking = (currentExpr == EXPR_IDLE && blinkFramesLeft > 0);
        renderer.draw(currentExpr, animTick, autoBlinking);
        sprite.pushSprite(0, 0);

        animTick++;
    }
}
