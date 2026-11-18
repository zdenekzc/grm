
/* generate.t */

/* ---------------------------------------------------------------------- */

#if 1
void example (int i, int k)
{
    int n;
    n = 0;
    while ( i > 0 )
    {
       if ( i > j )
          i = 2 * i + k;
       else
          i = n;
    }
}
#endif

/* ---------------------------------------------------------------------- */

#if 1

void printf ();   // extern, resolved via libc

// N malé pro výuku — 20 prvků se vejde na obrazovku, demonstrace
// algoritmu je zachována.
const int N = 20;

int a[N];

// Pointerová verze swap — naivní generátor nepodporuje C++ reference,
// ale *p / &x z Phase B fungují skvěle.
void swap (int * x, int * y)
{
    int t = *x;
    *x = *y;
    *y = t;
}

void heapify (int i, int k)
{
    while (2 * i + 1 <= k)
    {
        int v = 2 * i + 1;

        if (v + 1 <= k)
            if (a[v+1] > a[v])
                v = v + 1;

        if (a[i] < a[v])
        {
            swap (& a[i], & a[v]);
            i = v;
        }
        else
        {
            i = k+1;
        }
    }
}

void heapsort (int n)
{
    int i;
    for (i = n-1; i >= 0; i = i - 1)
        heapify (i, n-1);

    for (i = n-1; i > 0; i = i - 1)
    {
        swap (& a[0], & a[i]);
        heapify (0, i-1);
    }
}

int main ()
{
    int i;

    // Naplň pole hodnotami v sestupném pořadí (worst case pro sort).
    for (i = 0; i < N; i = i + 1)
        a[i] = N - i;

    heapsort (N);

    // Vytiskni setříděné pole.
    for (i = 0; i < N; i = i + 1)
        printf ("%d ", a[i]);
    printf ("\n");

    // Ověř, že je opravdu setříděné.
    int ok;
    ok = 1;
    for (i = 0; i < N - 1; i = i + 1)
        if (a[i + 1] < a[i])
            ok = 0;

    if (ok)
       printf ("OK\n");
    else
       printf ("CHYBA\n");

    return 0;
}

#endif

/* ---------------------------------------------------------------------- */

GenerateModule // after C++ code
{

}

/* ---------------------------------------------------------------------- */

// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
