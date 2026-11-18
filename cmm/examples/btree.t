
/* btree.t — B-strom adaptovaný pro view-mini/cmm generátor.
 *
 * Originál: view-mini/plain/btree.cc.  Téměř identický až na
 * pár drobností, na které student nemusí narazit:
 *
 *   - cout << x       ->  printf ("%d\n", x)   (libc přes extern)
 *   - ofstream f      ->  FILE * f = fopen     (C-style I/O)
 *
 * Pro studenty:
 * https://kmlinux.fjfi.cvut.cz/~culikzde/wiki/doku.php?id=zalg:btree
 */

/* externí libc — adresy si generátor zjistí přes ctypes.CDLL(None) */
void   printf ();
void * fopen ();
void   fprintf ();
void   fclose ();

const int Max = 4;

struct Item
{
    int    cnt;             /* počet klíčů v uzlu */
    int    key [Max+1];     /* key[0]..key[cnt-1], jeden navíc */
    Item * ref [Max+2];     /* ref[0]..ref[cnt],   jeden navíc */
};

/* 'new Item' alokuje zero-initialized blok přes calloc, takže
 * cnt=0 a všechny ref[i]=nullptr jsou rovnou pravdivé.  Pole key
 * zůstane vynulované — stačí, protože algoritmus key[i] pro
 * i >= cnt nikdy nečte. */

void enter0 (Item * p, int val)
{
    int i;
    i = 0;
    while (i < p->cnt && p->key [i] < val) i = i + 1;

    if (i < p->cnt && p->key [i] == val)
    {
        /* už tam je, nic neděláme */
    }
    else
    {
        Item * t;
        t = p->ref [i];
        if (t == nullptr)
        {
            int k;
            for (k = p->cnt - 1; k >= i; k = k - 1) p->key [k+1] = p->key [k];
            for (k = p->cnt;     k >= i; k = k - 1) p->ref [k+1] = p->ref [k];
            p->key [i] = val;
            p->ref [i] = nullptr;
            p->cnt = p->cnt + 1;
        }
        else
        {
            enter0 (t, val);
            if (t->cnt == Max + 1)
            {
                int  a, b, d, k;
                Item * n;
                a = Max / 2;             /* a klíčů zůstane v t */
                b = t->cnt - a - 1;      /* b klíčů do nového bloku */
                d = t->key [a];          /* dělící bod */

                n = new Item;
                n->cnt = b;
                for (k = a + 1; k < t->cnt;     k = k + 1) n->key [k - a - 1] = t->key [k];
                for (k = a + 1; k < t->cnt + 1; k = k + 1) n->ref [k - a - 1] = t->ref [k];

                for (k = a + 1; k < t->cnt;     k = k + 1) t->key [k] = 0;
                for (k = a + 1; k < t->cnt + 1; k = k + 1) t->ref [k] = nullptr;
                t->cnt = a;

                for (k = p->cnt - 1; k >= i; k = k - 1) p->key [k+1] = p->key [k];
                for (k = p->cnt;     k >  i; k = k - 1) p->ref [k+1] = p->ref [k];
                p->key [i]   = d;
                p->ref [i+1] = n;
                p->cnt = p->cnt + 1;
            }
        }
    }
}

void enter (Item * & p, int val)
{
    if (p == nullptr)
    {
        p = new Item;
        p->cnt = 1;
        p->key [0] = val;
    }
    else
    {
        Item * t;
        enter0 (p, val);
        t = p;
        if (t->cnt == Max + 1)
        {
            int  a, b, d, k;
            Item * n;
            Item * r;
            a = Max / 2;
            b = t->cnt - a - 1;
            d = t->key [a];

            n = new Item;
            n->cnt = b;
            for (k = a + 1; k < t->cnt;     k = k + 1) n->key [k - a - 1] = t->key [k];
            for (k = a + 1; k < t->cnt + 1; k = k + 1) n->ref [k - a - 1] = t->ref [k];

            for (k = a + 1; k < t->cnt;     k = k + 1) t->key [k] = 0;
            for (k = a + 1; k < t->cnt + 1; k = k + 1) t->ref [k] = nullptr;
            t->cnt = a;

            r = new Item;
            r->cnt = 1;
            r->ref [0] = t;
            r->key [0] = d;
            r->ref [1] = n;
            p = r;
        }
    }
}

/* Vytiskne klíče v rostoucím pořadí (in-order procházka). */
void print_tree (Item * p)
{
    if (p != nullptr)
    {
        int i;
        for (i = 0; i < p->cnt; i = i + 1)
        {
            print_tree (p->ref [i]);
            printf ("%d\n", p->key [i]);
        }
        print_tree (p->ref [p->cnt]);
    }
}

/* HTML/JS výstup pro mxGraph.  comma a level mají defaulty,
 * volání z displayData stačí 'display (f, p)'. */
void display (void * f, Item * p, int comma = 0, int level = 0)
{
    if (p != nullptr)
    {
        int  is_leaf;
        int  i;
        is_leaf = (p->ref [0] == nullptr);

        for (i = 1; i <= level; i = i + 1) fprintf (f, "   ");
        fprintf (f, "[");

        /* klíče v jednoduchých uvozovkách jako jeden string */
        fprintf (f, "'");
        for (i = 0; i < p->cnt; i = i + 1)
        {
            fprintf (f, "%d", p->key [i]);
            if (i < p->cnt - 1) fprintf (f, ", ");
        }
        fprintf (f, "'");

        if (! is_leaf)
        {
           fprintf (f, ",\n");
           for (i = 0; i < p->cnt + 1; i = i + 1)
               display (f, p->ref [i], i < p->cnt, level + 1);
           for (i = 1; i <= level; i = i + 1) fprintf (f, "   ");
        }

        fprintf (f, "]");
        if (comma) fprintf (f, ",");
        fprintf (f, "\n");
    }
}

void displayData (Item * p)
{
    void * f;
    f = fopen ("output.html", "w");

    fprintf (f, "<html>\n");
    fprintf (f, "<head>\n");
    fprintf (f, "<title>B-Tree with mxGraph</title>\n");
    fprintf (f, "<script type=\"text/javascript\">\n");
    fprintf (f, "    mxBasePath = 'http://jgraph.github.io/mxgraph/javascript/src';\n");
    fprintf (f, "</script>\n");
    fprintf (f, "<script type=\"text/javascript\" src=\"http://jgraph.github.io/mxgraph/javascript/src/js/mxClient.js\"></script>\n");
    fprintf (f, "<script type=\"text/javascript\">\n");

    fprintf (f, "    var data =\n");
    display (f, p);
    fprintf (f, "    ;\n");

    fprintf (f, "function display (graph, parent, above, items) {\n");
    fprintf (f, "    var name;\n");
    fprintf (f, "    if (Array.isArray (items)) name = items [0];\n");
    fprintf (f, "    else name = items;\n");
    fprintf (f, "    var v1 = graph.insertVertex (parent, null, name, 0, 0, 80, 30);\n");
    fprintf (f, "    if (above != null)\n");
    fprintf (f, "       var e1 = graph.insertEdge (parent, null, '', above, v1);\n");
    fprintf (f, "    if (Array.isArray (items)) {\n");
    fprintf (f, "      var i;\n");
    fprintf (f, "      for (i = 1; i < items.length; i++) {\n");
    fprintf (f, "         var item = items [i];\n");
    fprintf (f, "         display (graph, parent, v1, items [i]);\n");
    fprintf (f, "      }\n");
    fprintf (f, "    }\n");
    fprintf (f, "    return v1;\n");
    fprintf (f, "}\n");
    fprintf (f, "function main (container) {\n");
    fprintf (f, "    var graph = new mxGraph (container);\n");
    fprintf (f, "    var parent = graph.getDefaultParent ();\n");
    fprintf (f, "    graph.getModel ().beginUpdate ();\n");
    fprintf (f, "    var v1 = display (graph, parent, null, data);\n");
    fprintf (f, "    var layout = new mxHierarchicalLayout (graph, mxConstants.DIRECTION_NORTH);\n");
    fprintf (f, "    layout.execute (graph.getDefaultParent (), v1);\n");
    fprintf (f, "    graph.getModel ().endUpdate ();\n");
    fprintf (f, "};\n");
    fprintf (f, "</script>\n");
    fprintf (f, "</head>\n");
    fprintf (f, "<body onload=\"main (document.getElementById ('graphContainer'))\">\n");
    fprintf (f, "<div id=\"graphContainer\">\n");
    fprintf (f, "</div>\n");
    fprintf (f, "</body>\n");
    fprintf (f, "</html>\n");

    fclose (f);
}

int main ()
{
    Item * root;
    int k;

    root = nullptr;
    enter (root, 30);
    enter (root, 20);
    enter (root, 10);
    enter (root, 40);
    enter (root, 50);

    for (k = 21; k <= 29; k = k + 1) enter (root, k);
    for (k = 51; k <= 80; k = k + 1) enter (root, k);

    print_tree (root);
    displayData (root);

    return 0;
}

GenerateModule { }

/* kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all */
