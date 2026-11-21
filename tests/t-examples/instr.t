
/* instr.t */

/* ---------------------------------------------------------------------- */

#if 1

int x, y;

int p [10];


void fce1 ()
{

   x = y;

   x = p[x];

   p[y] = y;

   /*
   // if (x > 1)
   //   fce1 ();
   */
}

#if 0

void fce2 ()
{
   if (x > y)
      x = 1;
}

void fce3 ()
{
   while (x > y)
   {
      x = x - 1;
      y = y + 1;
   }

   x = x + y;
}

void fce4 ()
{
   int i;
   int sum;
   sum = 0;
   for (i = 1; i <= 10; i = i+1)
       sum = sum + i;
}

void fce5 (int i, int j)
{
}

void fce ()
{
    fce5 (x, y);
}
#endif

#endif

/* ---------------------------------------------------------------------- */

#if 0

// #include <iostream>
// #include <time.h>
// using namespace std;

// const int N = 1000;
#define N 1000

int a[N];

inline void swap (int /* & */ x, int /* & */ y)
{
    /*
    int t, tx, ty;
    tx = x;
    ty = y
    t = tx;
    tx = ty;
    ty = t;
    */
}

void heapify (int i0, int k)
{
    int i;
    i = i0;
    while (2 * i + 1 <= k)
    {
        int v;
        v = 2 * i + 1;

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
    int i;
    for (i = n-1; i >= 0; i--)
        heapify (i, n-1);

    for (i = n-1; i > 0; i--)
    {
        swap (a[0], a[i]);
        heapify (0, i-1);
    }
}

using namespace std;

int main ()
{
    int i;
    for (i = 0; i < N; i++)
        a[i] = 10 * i;

    heapsort (N);

    #if 0
    bool ok;
    ok = true;
    for (i = 0; i < N; i++)
    {
        cout << a[i];
        if (i < N-1 && a[i + 1] < a[i]) { ok = false; cout << " CHYBA"; }
        cout << endl;
    }

    if (ok)
       cout << "O.K." << endl;
    #endif

    // printf ("Hello");
    // cout << "O.K." << endl;
}

#endif

/* ---------------------------------------------------------------------- */

InstructionsModule // after C++ code
{

}

/* ---------------------------------------------------------------------- */

// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
