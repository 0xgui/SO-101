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
    explicit FaceRenderer(TFT_eSprite& spr) : _spr(spr) {}

    // Call every frame. animTick increments each frame; blinkOverride forces
    // eyes closed regardless of expression.
    void draw(Expression expr, uint32_t animTick, bool blinkOverride = false) {
        _spr.fillSprite(C_BG);
        drawFaceOval();
        drawEyes(expr, animTick, blinkOverride);
        drawMouth(expr, animTick);
    }

private:
    TFT_eSprite& _spr;

    // ── Face oval ────────────────────────────────────────────────────────────
    void drawFaceOval() {
        // Filled face
        _spr.fillEllipse(FACE_CX, FACE_CY, FACE_RX, FACE_RY, C_FACE);
        // Outline (2px)
        _spr.drawEllipse(FACE_CX, FACE_CY, FACE_RX,     FACE_RY,     C_OUTLINE);
        _spr.drawEllipse(FACE_CX, FACE_CY, FACE_RX - 1, FACE_RY - 1, C_OUTLINE);
    }

    // ── Single eye ───────────────────────────────────────────────────────────
    void drawEye(int cx, int cy, bool closed, bool squint = false) {
        if (closed) {
            // Closed: flat line
            _spr.drawFastHLine(cx - EYE_RW, cy, EYE_RW * 2, C_EYE);
            _spr.drawFastHLine(cx - EYE_RW, cy + 1, EYE_RW * 2, C_EYE);
            return;
        }
        if (squint) {
            // Squint (sad): half-height ellipse, flat top
            _spr.fillEllipse(cx, cy + EYE_RH / 2, EYE_RW, EYE_RH / 2, C_EYE);
            _spr.fillRect(cx - EYE_RW, cy - EYE_RH / 2, EYE_RW * 2, EYE_RH / 2, C_FACE);
            return;
        }
        // Normal eye
        _spr.fillEllipse(cx, cy, EYE_RW, EYE_RH, C_EYE);
        // Pupil
        _spr.fillCircle(cx, cy, PUPIL_R, C_PUPIL);
        // Gleam (top-left of pupil)
        _spr.fillCircle(cx - GLEAM_R, cy - GLEAM_R, GLEAM_R, C_GLEAM);
    }

    // ── Eyes (both) ──────────────────────────────────────────────────────────
    void drawEyes(Expression expr, uint32_t tick, bool blinkOverride) {
        bool closed = blinkOverride || (expr == EXPR_BLINK);
        bool squint = (expr == EXPR_SAD);
        bool happy  = (expr == EXPR_HAPPY);

        if (happy) {
            // Happy: upward arc "^" eyes
            drawHappyEye(EYE_LX, EYE_Y);
            drawHappyEye(EYE_RX, EYE_Y);
        } else {
            drawEye(EYE_LX, EYE_Y, closed, squint);
            drawEye(EYE_RX, EYE_Y, closed, squint);
        }
    }

    void drawHappyEye(int cx, int cy) {
        // "^" arc: filled semicircle with bottom cut
        _spr.fillEllipse(cx, cy, EYE_RW, EYE_RH, C_EYE);
        _spr.fillRect(cx - EYE_RW, cy, EYE_RW * 2, EYE_RH + 2, C_FACE);
    }

    // ── Mouth ────────────────────────────────────────────────────────────────
    void drawMouth(Expression expr, uint32_t tick) {
        switch (expr) {
            case EXPR_HAPPY:
                // Big smile: arc below centre
                drawArcMouth(MOUTH_CX, MOUTH_CY - 20, 55, 48, 15, 165);
                break;
            case EXPR_SAD:
                // Frown: arc above a lower centre point
                drawArcMouth(MOUTH_CX, MOUTH_CY + 30, 55, 48, 195, 345);
                break;
            case EXPR_TALK: {
                // Animated oval that grows/shrinks (4-frame cycle)
                int phase = tick % 8;
                int mh = (phase < 4) ? (4 + phase * 5) : (24 - (phase - 4) * 5);
                _spr.fillEllipse(MOUTH_CX, MOUTH_CY, MOUTH_W / 2, mh, C_MOUTH);
                // Teeth line
                _spr.drawFastHLine(MOUTH_CX - MOUTH_W / 2 + 6, MOUTH_CY, MOUTH_W - 12, C_FACE);
                break;
            }
            case EXPR_BLINK:
            case EXPR_IDLE:
            default:
                // Neutral: thin horizontal line
                _spr.fillRoundRect(MOUTH_CX - MOUTH_W / 2, MOUTH_CY - 3,
                                   MOUTH_W, 6, 3, C_MOUTH);
                break;
        }
    }

    // Approximate arc with a series of filled circles (TFT_eSPI drawArc needs
    // TFT_eSPI v2.4+ and can be slow; this is portable and fast enough)
    void drawArcMouth(int cx, int cy, int rx, int ry,
                      int startDeg, int endDeg) {
        for (int deg = startDeg; deg <= endDeg; deg += 3) {
            float rad = deg * 0.01745f;
            int x = cx + (int)(rx * cosf(rad));
            int y = cy + (int)(ry * sinf(rad));
            _spr.fillCircle(x, y, 4, C_MOUTH);
        }
    }
};
