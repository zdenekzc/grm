/* containers.h - Sequence <T> a Dictionary <K, V> pro g++

   cparser ma oba typy vestavene (CHANGELOG.txt, kapitola 22) - tento soubor
   pouziva jen g++ (testy, vypis -p); chovani je stejne:
     - hodnotova semantika (prirazeni a predani hodnotou = kopie),
     - index mimo rozsah:  "Assertion failed in function Sequence (index out
       of range)" na stderr a abort,
     - Dictionary::get vraci pro chybejici klic V () (0, nullptr, ""),
       dict [k] chybejici klic vlozi */

#ifndef __CPARSER__
#ifndef CPARSER_CONTAINERS_H
#define CPARSER_CONTAINERS_H

#include <deque>
#include <map>
#include <cstdio>
#include <cstdlib>

inline void cparser_range_error (const char * what)
{
   fflush (stdout);
   fprintf (stderr, "Assertion failed in function %s\n", what);
   abort ();
}

template <typename T>
class Sequence
{
   private:
      std::deque <T> v;   /* ne vector - vector <bool> nema T & */

      void check (long i) const
      {
         if (i < 0 || i >= (long) v.size ())
            cparser_range_error ("Sequence (index out of range)");
      }

   public:
      void add (T x)            { v.push_back (x); }
      void push (T x)           { v.push_back (x); }
      void insertFirst (T x)    { v.push_front (x); }
      T    get (int i) const    { check (i); return v [i]; }
      void change (int i, T x)  { check (i); v [i] = x; }
      int  size () const        { return (int) v.size (); }
      bool empty () const       { return v.empty (); }
      void clear ()             { v.clear (); }
      T    last () const        { check ((long) v.size () - 1); return v.back (); }
      T    top () const         { return last (); }
      void pop ()               { check ((long) v.size () - 1); v.pop_back (); }
      T &  operator [] (int i)  { check (i); return v [i]; }

      bool contains (T x) const
      {
         for (size_t i = 0; i < v.size (); i++)
            if (v [i] == x) return true;
         return false;
      }

      typename std::deque <T>::iterator begin () { return v.begin (); }
      typename std::deque <T>::iterator end ()   { return v.end (); }
      typename std::deque <T>::const_iterator begin () const { return v.begin (); }
      typename std::deque <T>::const_iterator end () const   { return v.end (); }
};

template <typename K, typename V>
class Dictionary
{
   private:
      std::map <K, V> m;

   public:
      void store (K k, V x)        { m [k] = x; }
      bool contains (K k) const    { return m.find (k) != m.end (); }
      void clear ()                { m.clear (); }
      int  size () const           { return (int) m.size (); }
      bool empty () const          { return m.empty (); }
      V &  operator [] (K k)       { return m [k]; }

      V get (K k) const
      {
         typename std::map <K, V>::const_iterator it = m.find (k);
         return it == m.end () ? V () : it->second;
      }
};

#endif /* CPARSER_CONTAINERS_H */
#endif /* __CPARSER__ */
