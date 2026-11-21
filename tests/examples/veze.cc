#include <stdio.h>
#include <assert.h>

const int N = 5; // pocet disku

struct Vez
{
    int v;      // vyska veze
    int p [N];  // velikosti disku, p[0] je dole, p[v-1] je vrchol
};

Vez A, B, C;

void nuluj (Vez & X)
{
   X.v = 0; // nulova vyska

   for (int i = 0; i<N; i++)
        X.p [i] = 0; // pro ladeni - vse vynulujeme
}

void init (Vez & X)
{
    X.v = N; // N disku
    for (int i = 0; i<N; i++)
        X.p [i] = N-i; // dole p[0] = N, ..., nahore p[N-1] = 1
}

void zobraz (Vez & X)
{
    for (int i = 0; i < X.v; i++)
        printf ("%d", X.p[i]);
    for (int i = X.v; i <= N; i++)
        printf (" "); // dopln mezerami
}

void tiskni (Vez & X, Vez & Y, Vez & Z)
{
    zobraz (X);
    printf (" : ");
    zobraz (Y);
    printf (" : ");
    zobraz (Z);
    printf ("\n");
}

void krok (Vez & X, Vez & Y) // presun disku z veze X na nez Y
{
    int h;
    assert (X.v > 0); // zkontroluj zda je vez neprazdna

    h = X.p [X.v-1]; // cislo disku z vrcholu veze X
    X.p [X.v-1] = 0; // pro ladeni - vynulujeme
    X.v = X.v - 1;  // zmensime vysku veze X

    assert (Y.v < N); // zkontroluj zda vez neni prilis vysoka
    if (Y.v > 0)
    {
        assert (h < Y.p [Y.v-1]); // zda h je mensi nez soucasny vrchol
    }

    Y.v = Y.v + 1; // zvysime vez Y
    Y.p [Y.v-1] = h; // na vrchol pridame disk h
}

void hraj (Vez & X, Vez & Y, Vez & Z, int k)
// presun z veze X na vez Z, vez Y bude pomocna vez
// preneseme k disku z vrcholu veze X
{
    if (k > 1) hraj (X, Z, Y, k-1); // k-1 disku, X --> Y, Z je pomocna vez
    krok (X, Z); // 1 disk, X --> Z
    tiskni (A, B, C); // vytiskneme jeden krok
    if (k > 1) hraj (Y, X, Z, k-1); // k-1 disku, Y --> Z, X je pomocna vez
}

int main (int argc, char * argv [])
{
    init (A); // vez A - N disku
    nuluj (B); // veze B a C jsou prazdne
    nuluj (C);

    tiskni (A, B, C); // pocatecni stav
    hraj (A, B, C, N); // A --> C, B je pomocna vez, preneseme N disku

    printf ("O.K.\n");
    return 0;
}
