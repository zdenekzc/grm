
#  bellbind/less.py http://gist.github.com/bellbind/3058567

# http://github.com/vaab/colour

# example of curses: less command
import locale
import sys
import curses

# --------------------------------------------------------------------------

def menu_func (scr):

    """
    lines = [ ]
    for line in sys.stdin :
        lines.append (line)
        print (line)
    """

    lines = ["abc", "def", "klm"]

    top = 0
    left = 0

    done = False
    while not done :
       scr.clear () # remove old windows
       scr.refresh () # important, otherwise window is not visible

       "create window"
       h = 20
       w = 72
       y = 2
       x = 2
       win = curses.newwin (h+2, w+2, y, x)

       # size = screen.getmaxyx()
       size = win.getmaxyx ()

       "set colors"
       curses.start_color ()
       curses.init_pair (1, curses.COLOR_WHITE, curses.COLOR_BLUE)
       win.bkgd (' ', curses.color_pair(1))

       win.box ()

       cnt = len (lines)
       i = 0
       while i < h and top+i < cnt :
            txt = lines [top+i][left:]
            win.addstr (i+1, 1, txt)
            i = i + 1

       txt = "top = " + str (top) + ", left = " + str (left)
       win.addstr (h+1, 1, txt)

       "redraw window"
       win.refresh ()

       "wait for key"
       key = scr.getch ()
       # key = scr.getch ()
       # key = self.pad.getch()
       if key == ord ('q') :
          done = True
       if key == curses.KEY_UP :
          top = max (top - 1, 0)
       if key == curses.KEY_DOWN :
          top = min (top + 1, h-1)
       if key == curses.KEY_LEFT :
          left = max (left - 1, 0)
       if key == curses.KEY_RIGHT :
          left = min (left + 1, w-1)

# --------------------------------------------------------------------------

"""
def curses_wrapper (menu_func) :
   scr = curses.initscr ()
   curses.cbreak ()
   curses.noecho ()
   scr.keypad (True)

   menu_func (scr)

   curses.nocbreak ()
   scr.keypad (False)
   curses.echo ()
   curses.endwin ()
"""

# --------------------------------------------------------------------------

if __name__ == '__main__':
   locale.setlocale(locale.LC_ALL, "")
   curses.wrapper (menu_func)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
