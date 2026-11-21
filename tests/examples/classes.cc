// tridy, jednoducha dedicnost, konstruktory bez parametru, virtualni metody
#include <stdio.h>

int created = 0;                       // pocet vytvorenych objektu

class Counter
{
public:
    int id;
    Counter () { created ++; id = created; }
};

class Shape                            // abstraktni trida
{
protected:
    int kind;
    Counter tag;                       // vnoreny objekt s konstruktorem
public:
    Shape * next;                      // spojovy seznam utvaru

    Shape () { kind = 0; next = nullptr; }
    virtual ~Shape () { }

    virtual int area () = 0;
    virtual int perimeter () { return 0; }
    virtual const char * name () { return "shape"; }

    int number () { return tag.id; }
    void print ();
};

void Shape::print ()
{
    printf ("%-10s #%d  area %4d  perimeter %3d\n", name (), number (), area (), perimeter ());
}

class Rect : public Shape
{
protected:
    int w;
    int h;
public:
    Rect () { kind = 1; w = 2; h = 3; }
    void set (int a, int b) { w = a; h = b; }
    int area () override { return w * h; }
    int perimeter () override { return 2 * (w + h); }
    const char * name () override { return "rect"; }
};

class Square : public Rect             // dedi area a perimeter z Rect
{
public:
    Square () { kind = 2; }
    void side (int a) { set (a, a); }
    const char * name () override { return "square"; }
};

class Circle : public Shape
{
    int r;
public:
    Circle () { kind = 3; r = 1; }
    void radius (int x) { r = x; }
    int area () { return 3 * r * r; }       // virtualni i bez virtual (prekryva)
    int perimeter () { return 6 * r; }
    const char * name () { return "circle"; }
};

class Labeled : public Square          // volani metody baze:  Square::name
{
public:
    int extra;
    Labeled () { extra = 100; }
    int area () { return Rect::area () + extra; }
    const char * name () { return "labeled"; }
};

class Stats                            // staticka metoda, pole objektu
{
public:
    Counter slots [3];
    static int square (int x) { return x * x; }
    int sum () { int s = 0; for (int i = 0; i < 3; i++) s += square (slots [i].id); return s; }
};

Stats global_stats;                    // globalni objekt - konstruktor pred main

int total (Shape * list)
{
    int s = 0;
    while (list != nullptr)
    {
        s += list->area ();
        list = list->next;
    }
    return s;
}

int main ()
{
    printf ("created before main: %d\n", created);

    Shape * list = nullptr;
    for (int i = 1; i <= 6; i++)
    {
        Shape * s;
        if (i % 3 == 0)
        {
            Circle * c = new Circle;
            c->radius (i);
            s = c;
        }
        else if (i % 3 == 1)
        {
            Square * q = new Square;
            q->side (i + 1);
            s = q;
        }
        else
        {
            Rect * r = new Rect;
            r->set (i, i + 2);
            s = r;
        }
        s->next = list;
        list = s;
    }

    Labeled lab;
    lab.side (5);
    lab.next = list;
    list = &lab;

    for (Shape * p = list; p != nullptr; p = p->next)
        p->print ();

    printf ("total area %d\n", total (list));
    printf ("stats sum %d\n", global_stats.sum ());
    printf ("created %d\n", created);
    printf ("O.K.\n");
    return 0;
}
