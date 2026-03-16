#pragma once
#include <TFT_eSPI.h>

// ─────────────────────────────────────────────────────────────────────────────
//  Expression IDs
// ─────────────────────────────────────────────────────────────────────────────
enum Expression {
    EXPR_IDLE  = 0,
    EXPR_HAPPY = 1,
    EXPR_SAD   = 2,
    EXPR_BLINK = 3,
    EXPR_TALK  = 4,
    EXPR_COUNT
};

// Map name strings to enum (used by serial parser)
static const struct { const char* name; Expression expr; } EXPR_MAP[] = {
    { "IDLE",  EXPR_IDLE  },
    { "HAPPY", EXPR_HAPPY },
    { "SAD",   EXPR_SAD   },
    { "BLINK", EXPR_BLINK },
    { "TALK",  EXPR_TALK  },
};
static const int EXPR_MAP_LEN = sizeof(EXPR_MAP) / sizeof(EXPR_MAP[0]);

// ─────────────────────────────────────────────────────────────────────────────
//  Palette
// ─────────────────────────────────────────────────────────────────────────────
#define C_BG       TFT_BLACK
#define C_FACE     0x2104   // very dark grey face bg
#define C_EYE      0x07FF   // cyan iris
#define C_PUPIL    TFT_BLACK
#define C_MOUTH    TFT_WHITE
#define C_OUTLINE  0x4208   // dark grey face ring
#define C_GLEAM    TFT_WHITE

// ─────────────────────────────────────────────────────────────────────────────
//  Layout constants (240x320 display, face centered)
// ─────────────────────────────────────────────────────────────────────────────
#define FACE_CX    120      // face centre X
#define FACE_CY    155      // face centre Y
#define FACE_RX    100      // face horizontal radius
#define FACE_RY    120      // face vertical radius

#define EYE_LX      78      // left eye centre X
#define EYE_RX     162      // right eye centre X
#define EYE_Y      115      // eye centre Y
#define EYE_RW      26      // eye half-width
#define EYE_RH      20      // eye half-height
#define PUPIL_R      9      // pupil radius
#define GLEAM_R      4      // specular gleam radius

#define MOUTH_CX   120      // mouth centre X
#define MOUTH_CY   218      // mouth centre Y
#define MOUTH_W     52      // mouth half-width base

// ─────────────────────────────────────────────────────────────────────────────
//  Face renderer (operates on a TFT_eSprite)
// ─────────────────────────────────────────────────────────────────────────────
class FaceRenderer {
public:
    explicit FaceRenderer(TFT_eSPI& tft) : _tft(tft) {
        _lastExpr = EXPR_COUNT;
        _lastBlink = false;
        _lastTick = 0;
        _forceRedraw = true;
    }

    // Call every frame. animTick increments each frame; blinkOverride forces
    // eyes closed regardless of expression.
    void draw(Expression expr, uint32_t animTick, bool blinkOverride = false) {
        // Quantize animation to avoid redrawing every single micro-tick
        uint32_t tick = animTick / 3;

        // Skip redraw if state is exactly the same as last frame
        if (!_forceRedraw && _lastExpr == expr && _lastBlink == blinkOverride && _lastTick == tick) {
            return;
        }

        if (_forceRedraw) {
            _tft.fillScreen(TFT_BLACK);
            _forceRedraw = false;
        }

        String faceStr = "";
        uint32_t color = TFT_WHITE;

        if (blinkOverride || expr == EXPR_BLINK) {
            faceStr = "( - _ - )";
            color = TFT_DARKGREY;
        } else {
            switch (expr) {
                case EXPR_IDLE:
                    // Subtle bobbing or looking around
                    faceStr = (tick % 10 < 2) ? "( O _ O )" : "( o _ o )";
                    color = TFT_WHITE;
                    break;
                case EXPR_HAPPY:
                    // Bouncing happy emoji
                    faceStr = (tick % 4 < 2) ? "( ^ w ^ )" : "( > w < )";
                    color = TFT_GREEN;
                    break;
                case EXPR_SAD:
                    // Flowing tears
                    faceStr = (tick % 4 < 2) ? "( ; _ ; )" : "( T _ T )";
                    color = TFT_CYAN;
                    break;
                case EXPR_TALK: {
                    // Animated speaking mouth
                    int phase = tick % 4;
                    if (phase == 0) faceStr = "( o _ o )";
                    else if (phase == 1) faceStr = "( o O o )";
                    else if (phase == 2) faceStr = "( o 0 o )";
                    else faceStr = "( o O o )";
                    color = TFT_YELLOW;
                    break;
                }
                default:
                    faceStr = "( . _ . )";
                    color = TFT_LIGHTGREY;
                    break;
            }
        }

        _tft.setTextColor(color, TFT_BLACK); // Background black wipes the old chars entirely!
        _tft.setTextDatum(MC_DATUM); // Middle center
        _tft.setTextSize(4); // Font 1 (glcd) scaled by 4 (24px wide * 32px tall per char)
        
        // Pad the string with spaces to safely overwrite parts of older, wider expressions
        String paddedStr = "   " + faceStr + "   ";
        _tft.drawString(paddedStr, 120, 160, 1);

        _lastExpr = expr;
        _lastBlink = blinkOverride;
        _lastTick = tick;
    }

    void forceRedraw() {
        _forceRedraw = true;
    }

private:
    TFT_eSPI& _tft;
    Expression _lastExpr;
    bool _lastBlink;
    uint32_t _lastTick;
    bool _forceRedraw;
};
