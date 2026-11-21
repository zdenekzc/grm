// std::string:  =  +  +=  porovnani,  c_str (), length (), empty ()
#include <stdio.h>
#include <string>
using namespace std;

string number (int n)                  // cislo na text
{
    if (n < 0) return "-" + number (-n);
    string digit = "";
    digit += '0' + n % 10;
    if (n < 10) return digit;
    return number (n / 10) + digit;
}

string repeat (string s, int n)
{
    string r;
    for (int i = 0; i < n; i++) r += s;
    return r;
}

void append_line (string & out, const string & key, int value)
{
    out += key;
    out += " = ";
    out += number (value);
    out += '\n';
}

class Item
{
public:
    string name;
    int    price;
    Item () { price = 0; }
    virtual string describe () { return name + " (" + number (price) + ")"; }
};

class Special : public Item
{
public:
    string note;
    string describe () { return Item::describe () + " [" + note + "]"; }
};

string words [8];
int count = 0;

void add (string w) { words [count] = w; count ++; }

int main ()
{
    printf ("%s %s %s\n", number (0).c_str (), number (12345).c_str (), number (-678).c_str ());
    printf ("[%s] [%s]\n", repeat ("ab", 3).c_str (), repeat ("x", 0).c_str ());

    string report;
    append_line (report, "alpha", 1);
    append_line (report, "beta", -20);
    append_line (report, "gamma", 300);
    printf ("%s", report.c_str ());
    printf ("report length %d\n", report.length ());

    add ("pear"); add ("apple"); add ("fig"); add ("banana");
    add ("apple pie"); add (""); add ("Zebra"); add ("app");

    // bublinkove razeni
    for (int i = 0; i < count; i++)
        for (int j = 0; j < count - 1 - i; j++)
            if (words [j] > words [j + 1])
            {
                string t = words [j];
                words [j] = words [j + 1];
                words [j + 1] = t;
            }
    for (int i = 0; i < count; i++)
        printf ("%d: '%s'%s\n", i, words [i].c_str (), words [i].empty () ? " (empty)" : "");

    Item * a = new Item;
    a->name = "lamp";
    a->price = 250;
    Special * b = new Special;
    b->name = "chair";
    b->price = 1200;
    b->note = "sale";
    Item * list [2];
    list [0] = a;
    list [1] = b;
    for (int i = 0; i < 2; i++)
        printf ("%s\n", list [i]->describe ().c_str ());

    string big;
    for (int i = 0; i < 1000; i++)
        big += number (i % 10);
    printf ("big %d %s\n", big.length (), big == repeat ("0123456789", 100) ? "ok" : "bad");

    string s1 = "abc", s2 = "abc";
    printf ("%d %d %d %d\n", s1 == s2, s1 != s2, s1 < "abd", s1 >= "abcd");
    printf ("O.K.\n");
    return 0;
}
