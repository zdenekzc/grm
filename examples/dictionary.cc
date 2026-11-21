/* dictionary.c - vestaveny typ Dictionary <K, V>: store, get, contains, size,
   empty, clear, dict [k] (chybejici klic se vlozi), klice std::string,
   cela cisla, ukazatele, vycty; hodnotova semantika; zvetsovani tabulky */

#include <stdio.h>
#include <string>
#include "../../cmini/ownheaders/containers.h"
using namespace std;

enum Kind { alpha, beta, gamma };

struct Rule
{
   string name;
   int line;
};

class Grammar
{
   public:
      Dictionary <string, Rule *> rules;
      Dictionary <int, string> names;
};

Dictionary <string, int> count_words (Sequence <string> & words)
{
   Dictionary <string, int> d;
   for (string w : words)
      d [w] ++;
   return d;
}

int lookup (Dictionary <string, int> d, string k)     /* hodnotou - kopie */
{
   d.store ("zmena", 1);
   return d.get (k);
}

int main ()
{
   Dictionary <string, int> d;
   printf ("empty %d size %d get %d contains %d\n", d.empty (), d.size (), d.get ("x"), d.contains ("x"));
   d.store ("jedna", 1);
   d.store ("dva", 2);
   d.store ("tri", 3);
   d.store ("dva", 22);                       /* prepsani */
   printf ("size %d: %d %d %d %d\n", d.size (), d.get ("jedna"), d.get ("dva"), d.get ("tri"), d.get ("ctyri"));
   printf ("contains %d %d\n", d.contains ("tri"), d.contains ("pet"));
   d ["pet"] = 5;
   d ["jedna"] += 100;
   int missing = d ["sest"];                  /* vlozi 0 */
   printf ("index %d %d %d size %d\n", d ["pet"], d.get ("jedna"), missing, d.size ());

   string key = "dva";
   key += "";
   printf ("string key %d\n", d.get (key));

   Dictionary <string, int> copy = d;
   copy.store ("novy", 9);
   copy ["jedna"] = -1;
   printf ("copy %d %d  orig %d %d\n", copy.size (), copy.get ("jedna"), d.size (), d.get ("jedna"));
   printf ("lookup %d size %d contains %d\n", lookup (d, "tri"), d.size (), d.contains ("zmena"));

   /* mnoho klicu - zvetsovani tabulky */
   Dictionary <int, int> squares;
   for (int i = -3000; i < 3000; i += 3)
      squares.store (i, i * i);
   long sum = 0;
   for (int i = -3000; i < 3000; i++)
      if (squares.contains (i)) sum += squares.get (i);
   printf ("squares size %d sum %ld get %d %d\n", squares.size (), sum, squares.get (-2997), squares.get (1));

   Dictionary <string, string> names;
   for (int i = 0; i < 2000; i++)
   {
      string k = "k";
      int n = i;
      do { k += (char) ('0' + n % 10); n /= 10; } while (n > 0);
      names.store (k, "v" + k);
   }
   printf ("names %d %s %s [%s]\n", names.size (), names.get ("k0").c_str (), names.get ("k9991").c_str (),
           names.get ("nic").c_str ());
   names.clear ();
   names.store ("a", "b");
   printf ("clear %d %d %s\n", names.size (), names.contains ("k0"), names ["a"].c_str ());

   Grammar g;
   Rule * r1 = new Rule;
   r1->name = "expr";
   r1->line = 10;
   Rule * r2 = new Rule;
   r2->name = "stat";
   r2->line = 20;
   g.rules.store (r1->name, r1);
   g.rules.store (r2->name, r2);
   g.names [10] = "deset";
   printf ("rules %d %s %d null %d\n", g.rules.get ("stat")->line, g.rules ["expr"]->name.c_str (),
           g.rules.size (), g.rules.get ("nic") == nullptr);
   Grammar h;
   h = g;                                     /* kopie slovniku v objektu */
   h.names [10] = "ten";
   h.rules.store ("nove", r1);
   printf ("objects %s %s %d %d\n", g.names [10].c_str (), h.names.get (10).c_str (), g.rules.size (), h.rules.size ());

   Dictionary <Rule *, int> visits;
   visits [r1] ++;
   visits [r1] ++;
   visits [r2] = 7;
   printf ("pointer keys %d %d %d\n", visits [r1], visits.get (r2), visits.contains (nullptr));

   Dictionary <Kind, double> weights;
   weights.store (beta, 2.5);
   weights [gamma] = 0.25;
   printf ("enum keys %f %f %f\n", weights.get (alpha), weights [beta], weights.get (gamma));

   Dictionary <int, bool> seen;
   seen.store (5, true);
   printf ("bool %d %d\n", seen.get (5), seen.get (6));

   Sequence <string> words;
   words.add ("a");
   words.add ("b");
   words.add ("a");
   words.add ("c");
   words.add ("a");
   Dictionary <string, int> wc = count_words (words);
   printf ("words a=%d b=%d c=%d d=%d size %d\n", wc ["a"], wc.get ("b"), wc.get ("c"), wc.get ("d"), wc.size ());
   return 0;
}
