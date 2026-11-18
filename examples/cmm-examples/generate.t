
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

#if 0
// #include <iostream>
// #include <time.h>
// using namespace std;

const int N = 1000000;

int a[N];

inline void swap (int /* &  */ x, int /* & */ y)
{
    int t = x;
    x = y;
    y = t;
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
            swap (a[i], a[v]);
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
    for (int i = n-1; i >= 0; i--)
        heapify (i, n-1);

    for (int i = n-1; i > 0; i--)
    {
        swap (a[0], a[i]);
        heapify (0, i-1);
    }
}

int main ()
{
    for (int i = 0; i < N; i++)
        a[i] = 10 * i;

    heapsort (N);

    bool ok = true;
    for (int i = 0; i < N; i++)
    {
        cout << a[i];
        if (i < N-1 && a[i + 1] < a[i]) { ok = false; cout << " CHYBA"; }
        cout << endl;
    }

    if (ok)
       cout << "O.K." << endl;
}

#endif

/* ---------------------------------------------------------------------- */

GenerateModule // after C++ code
{

}

/* ---------------------------------------------------------------------- */

// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
