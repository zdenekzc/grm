#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include <toaru/graphics.h>
#include <toaru/yutani.h>
#include <toaru/decorations.h>
#include "toaru_compat.h"

#define WIN_W 300
#define WIN_H 400
#define LINE_H 18

typedef struct Node {
    const char *name;
    int level;
    int expanded;
    struct Node *children;
    int child_count;
} Node;

/* --- Ukázkový strom funkcí --- */

Node func_main_children[] = {
    { "init()", 1, 0, NULL, 0 },
    { "load_config()", 1, 0, NULL, 0 },
    { "run()", 1, 0, NULL, 0 },
};

Node root_nodes[] = {
    { "main()", 0, 1, func_main_children, 3 },
    { "helper()", 0, 0, NULL, 0 },
    { "compute()", 0, 0, NULL, 0 },
};

int root_count = 3;

/* --- Rekurzivní vykreslení stromu --- */

int draw_node(gfx_context_t *ctx, Node *n, int y) {
    int x = 10 + n->level * 20;

    /* Trojúhelník pro rozbalení */
    if (n->child_count > 0) {
        uint32_t col = rgb(200,200,200);
        if (n->expanded) {
            draw_triangle(ctx, x, y+6, x+8, y+6, x+4, y+12, col);
        } else {
            draw_triangle(ctx, x, y+4, x+8, y+8, x, y+8, col);
        }
    }

    /* Text */
    draw_string(ctx, x + 14, y, rgb(230,230,230), n->name);

    y += LINE_H;

    /* Děti */
    if (n->expanded && n->children) {
        for (int i = 0; i < n->child_count; i++) {
            y = draw_node(ctx, &n->children[i], y);
        }
    }

    return y;
}

/* --- Najde uzel podle Y souřadnice kliknutí --- */

Node *find_node_by_y(Node *nodes, int count, int *y, int click_y) {
    for (int i = 0; i < count; i++) {
        Node *n = &nodes[i];

        if (click_y >= *y && click_y < *y + LINE_H) {
            return n;
        }

        *y += LINE_H;

        if (n->expanded && n->children) {
            Node *child = find_node_by_y(n->children, n->child_count, y, click_y);
            if (child) return child;
        }
    }
    return NULL;
}

/* --- Hlavní program --- */

int main(void) {
    yutani_t *yctx = yutani_init();
    init_decorations();
    yutani_window_t *win = yutani_window_create(yctx, WIN_W, WIN_H);
    yutani_window_move(yctx, win, 200, 200);

    gfx_context_t *ctx = init_graphics_yutani(win);

    struct decor_bounds bounds;
    decor_get_bounds(win, &bounds);

    uint8_t pressed = 0;   /* tlacitka stisknuta pri DOWN — CLICK uz stav nema */

    while (1) {
        /* Vykreslení pozadí */
        draw_fill(ctx, rgb(40,40,40));
        render_decorations(win, ctx, (char*)"Function Tree");

        int y = bounds.top_height + 10;
        for (int i = 0; i < root_count; i++) {
            y = draw_node(ctx, &root_nodes[i], y);
        }

        yutani_flip(yctx, win);

        /* Události */
        yutani_msg_t *m = yutani_poll(yctx);
        if (!m) continue;

        switch (m->type) {
            case YUTANI_MSG_WINDOW_MOUSE_EVENT: {
                struct yutani_msg_window_mouse_event *me = (void*)m->data;

                /* Prepina jen skutecny klik (stisk i pusteni na miste). Kompozitor
                 * posila YUTANI_MOUSE_EVENT_CLICK az pri uvolneni, takže v me->buttons
                 * uz levy tlacitko neni — ktery tlacitko kliklo si musime pamatovat
                 * ze zpravy DOWN. Bez toho by tah mysi pres strom prepinal postupne
                 * vsechny uzly na ceste. */
                if (me->command == YUTANI_MOUSE_EVENT_DOWN) {
                    pressed = me->buttons;
                } else if (me->command == YUTANI_MOUSE_EVENT_CLICK
                        && (pressed & YUTANI_MOUSE_BUTTON_LEFT)) {
                    int click_y = me->new_y - bounds.top_height - 10;
                    int y = 0;
                    Node *clicked = find_node_by_y(root_nodes, root_count, &y, click_y);
                    if (clicked && clicked->child_count > 0) {
                        clicked->expanded = !clicked->expanded;
                    }
                }
                break;
            }

            case YUTANI_MSG_WINDOW_CLOSE:
            case YUTANI_MSG_SESSION_END:
                return 0;
        }

        free(m);
    }

    return 0;
}
