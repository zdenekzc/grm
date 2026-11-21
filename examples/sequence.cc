/* sequence.c - vestaveny typ Sequence <T>: add, get, change, size, empty,
   clear, contains, last, insertFirst, push, pop, top, seq [i] (cteni
   i zapis), for (T x : seq), for (T & x : seq), hodnotova semantika
   (prirazeni, parametr hodnotou, navratova hodnota, polozka objektu),
   prvky int, double, std::string, ukazatele, enum, bool */

#include <stdio.h>
#include <string>
#include "../../cmini/ownheaders/containers.h"
using namespace std;

enum Color { red, green, blue };

struct Item
{
   int id;
   string name;
};

class Bag
{
   public:
      string title;
      Sequence <int> nums;
      Sequence <string> words;
};

Sequence <int> global_seq;

int total (Sequence <int> s)            /* hodnotou - kopie */
{
   int t = 0;
   for (int x : s) t += x;
   s.add (1000);                         /* nezmeni puvodni */
   return t;
}

void fill (Sequence <int> & s, int n)    /* referenci */
{
   for (int i = 0; i < n; i++) s.add (i * i);
}

Sequence <string> split (string text)   /* navratova hodnota */
{
   Sequence <string> r;
   string w = "";
   for (int i = 0; i < (int) text.length (); i++)
   {
      if (text [i] == ' ')
      {
         if (w != "") r.add (w);
         w = "";
      }
      else w += text [i];
   }
   if (w != "") r.add (w);
   return r;
}

int main ()
{
   Sequence <int> a;
   printf ("empty %d size %d\n", a.empty (), a.size ());
   for (int i = 1; i <= 20; i++) a.add (i);
   printf ("size %d get %d last %d contains %d %d\n", a.size (), a.get (4), a.last (), a.contains (7), a.contains (77));
   a.change (0, 100);
   a [1] = a [1] * 50;
   a [2] += 7;
   printf ("a: %d %d %d\n", a [0], a [1], a.get (2));
   a.insertFirst (-1);
   printf ("first %d size %d\n", a [0], a.size ());

   Sequence <int> b = a;                 /* kopie */
   b.add (99);
   b [0] = 555;
   printf ("copy: a %d %d  b %d %d\n", a.size (), a [0], b.size (), b [0]);
   b = a;
   printf ("assign: b %d %d\n", b.size (), b [0]);

   printf ("total %d size %d\n", total (a), a.size ());
   fill (global_seq, 5);
   for (int x : global_seq) printf ("%d ", x);
   printf ("\n");

   for (int & x : a) x = x * 2;          /* zmena prvku */
   int s = 0;
   for (int x : a)
   {
      if (x > 30) break;
      if (x % 4 == 0) continue;
      s += x;
   }
   printf ("ref loop %d sum %d\n", a [5], s);

   Sequence <string> w = split ("  jeden dva  tri ctyri ");
   printf ("words %d:", w.size ());
   for (string x : w) printf (" [%s]", x.c_str ());
   printf (" contains %d %d\n", w.contains ("tri"), w.contains ("pet"));
   w [0] += "!";
   printf ("w0 %s last %s\n", w [0].c_str (), w.last ().c_str ());

   Sequence <double> d;
   d.add (1.5);
   d.add (2);
   d.add (0.25f);
   double ds = 0;
   for (double x : d) ds += x;
   printf ("double %f %f %d\n", ds, d [1] / 4, d.contains (2.0));

   Sequence <Item *> items;
   for (int i = 0; i < 3; i++)
   {
      Item * it = new Item;
      it->id = i + 10;
      it->name = "item" + string (1, 'A' + i);
      items.add (it);
   }
   for (Item * it : items) printf ("%d %s; ", it->id, it->name.c_str ());
   printf ("contains ptr %d\n", items.contains (items [1]));

   Sequence <Color> colors;
   colors.add (blue);
   colors.add (red);
   Sequence <bool> flags;
   flags.add (true);
   flags.add (false);
   printf ("enum %d %d bool %d %d\n", colors [0], colors.get (1), flags [0], flags.last ());

   Sequence <int> st;
   st.push (1);
   st.push (2);
   st.push (3);
   st.pop ();
   printf ("stack top %d size %d\n", st.top (), st.size ());
   st.clear ();
   printf ("clear %d %d\n", st.size (), st.empty ());

   Bag bag1;
   bag1.title = "prvni";
   bag1.nums.add (1);
   bag1.words.add ("x");
   Bag bag2;
   bag2 = bag1;                          /* struktura - kopie posloupnosti */
   bag2.nums.add (2);
   bag2.words [0] = "y";
   printf ("bag %d %s  %d %s\n", bag1.nums.size (), bag1.words [0].c_str (), bag2.nums.size (), bag2.words [0].c_str ());

   Sequence <int> * p = &a;
   p->add (7);
   printf ("pointer %d %d\n", p->size (), (*p) [0]);
   return 0;
}
