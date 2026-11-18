/* toaru_compat.h
 *
 * Zjednoduseny drop-in kompatibilni shim pro ukazkove Yutani programy.
 * ToaruOS header <toaru/drawstring.h> sice deklaruje `draw_string`,
 * ale zadna knihovna ho neimplementuje — misto toho se v realu pouziva
 * `tt_draw_string` z <toaru/text.h> s TrueType fontem.
 *
 * Tento header ma v kazdem prelozenem souboru jeden lokalni TT_Font
 * (`static`) a obali tt_draw_string do klasicke signatury
 *   draw_string(ctx, x, y, color, str)
 * jakou programy puvodne volaji.
 *
 * Staci: include misto <toaru/drawstring.h>.
 */

#pragma once
#include <toaru/graphics.h>
#include <toaru/text.h>

static struct TT_Font *_tt_font = 0;

static void _ensure_font(void) {
    if (_tt_font) return;
    _tt_font = tt_font_from_shm("sans-serif");
    tt_set_size(_tt_font, 13);
}

static inline void draw_string(gfx_context_t *ctx, int x, int y,
                               uint32_t color, const char *str) {
    _ensure_font();
    /* tt_draw_string pocita baseline, ne top-left. Pricteme 10 px,
     * aby se vysledek priblizil puvodnimu bitmap-fontovemu offsetu. */
    tt_draw_string(ctx, _tt_font, x, y + 10, str, color);
}

/* ToaruOS graphics.h nema draw_triangle. Jednoduchy nahradni obrys
 * spojenim vrcholu usecekami — postaci pro sipky/indikatory. */
static inline void draw_triangle(gfx_context_t *ctx,
                                 int x0, int y0, int x1, int y1,
                                 int x2, int y2, uint32_t color) {
    draw_line(ctx, x0, x1, y0, y1, color);
    draw_line(ctx, x1, x2, y1, y2, color);
    draw_line(ctx, x2, x0, y2, y0, color);
}
