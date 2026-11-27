
# bellbind/less.py http://gist.github.com/bellbind/3058567
# example of curses: less command

import locale
import os, sys, time
import curses

# https://stackoverflow.com/questions/18551558/how-to-use-terminal-color-palette-with-curses

# --------------------------------------------------------------------------

# http://github.com/spellr/culour

# import os
# import curses

COLOR_PAIRS_CACHE = {}


class TerminalColors(object):
    MAGENTA = '[95'
    BLUE = '[94'
    GREEN = '[92'
    YELLOW = '[93'
    RED = '[91'
    END = '[0'


# Translates between the terminal notation of a color, to it's curses color number
TERMINAL_COLOR_TO_CURSES = {
    TerminalColors.RED: curses.COLOR_RED,
    TerminalColors.GREEN: curses.COLOR_GREEN,
    TerminalColors.YELLOW: curses.COLOR_YELLOW,
    TerminalColors.BLUE: curses.COLOR_BLUE,
    TerminalColors.MAGENTA: curses.COLOR_MAGENTA
}


def _get_color(fg, bg):
    key = (fg, bg)
    if key not in COLOR_PAIRS_CACHE:
        # Use the pairs from 101 and after, so there's less chance they'll be overwritten by the user
        pair_num = len(COLOR_PAIRS_CACHE) + 1
        curses.init_pair(pair_num, fg, bg)
        COLOR_PAIRS_CACHE[key] = pair_num

    return COLOR_PAIRS_CACHE[key]


def _color_str_to_color_pair(color):
    if color == TerminalColors.END:
        fg = curses.COLOR_WHITE
    else:
        if color in TERMINAL_COLOR_TO_CURSES :
           fg = TERMINAL_COLOR_TO_CURSES[color]
        else :
           fg = curses.COLOR_RED # !?
    color_pair = _get_color(fg, curses.COLOR_BLACK)
    return color_pair


def _add_line(y, x, window, line):
    # split but \033 which stands for a color change
    color_split = line.split('\033')

    # Print the first part of the line without color change
    default_color_pair = _get_color(curses.COLOR_WHITE, curses.COLOR_BLACK)
    window.addstr(y, x, color_split[0], curses.color_pair(default_color_pair))
    x += len(color_split[0])

    # Iterate over the rest of the line-parts and print them with their colors
    for substring in color_split[1:]:
        color_str = substring.split('m')[0]
        substring = substring[len(color_str)+1:]
        color_pair = _color_str_to_color_pair(color_str)
        window.addstr(y, x, substring, curses.color_pair(color_pair))
        x += len(substring)


def _inner_addstr(window, string, y=-1, x=-1):
    assert curses.has_colors(), "Curses wasn't configured to support colors. Call curses.start_color()"

    cur_y, cur_x = window.getyx()
    if y == -1:
        y = cur_y
    if x == -1:
        x = cur_x
    for line in string.split(os.linesep):
        _add_line(y, x, window, line)
        # next line
        y += 1


def addstr(*args):
    """
    Adds the color-formatted string to the given window, in the given coordinates
    To add in the current location, call like this:
        addstr(window, string)
    and to set the location to print the string, call with:
        addstr(window, y, x, string)
    Only use color pairs up to 100 when using this function,
    otherwise you will overwrite the pairs used by this function
    """
    if len(args) != 2 and len(args) != 4:
        raise TypeError("addstr requires 2 or 4 arguments")

    if len(args) == 4:
        window = args[0]
        y = args[1]
        x = args[2]
        string = args[3]
    else:
        window = args[0]
        string = args[1]
        y = -1
        x = -1

    return _inner_addstr(window, string, y, x)

# --------------------------------------------------------------------------

lines = [ ]

def menu_func (scr):

    global lines

    border = True
    fixed = False

    top = 0
    left = 0

    step = 0

    done = False
    redraw = True
    while not done :
       if redraw :
          step = step + 1
          scr.clear () # remove old windows
          scr.refresh () # important, otherwise window is not visible

          "create window"
          if fixed :
             h = 10
             w = 40
             y = 2
             x = 2
             if border :
                h = h + 2
                w = w + 2
          else :
             size = scr.getmaxyx()
             h = size[0]
             w = size[1]
             y = 0
             x = 0

          if border :
             win = curses.newwin (h, w, y, x)
             start_line = 1
             start_col = 1
             h = h - 2
             w = w - 2
          elif fixed :
             win = curses.newwin (h, w, y, x)
             start_line = 0
             start_col = 0
             h = h - 1
          else :
             win = scr
             start_line = 0
             start_col = 0
             h = h - 1

          "set colors"
          curses.start_color ()
          curses.init_pair (1, curses.COLOR_WHITE, curses.COLOR_BLUE)
          win.bkgd (' ', curses.color_pair(1))

          if border :
             win.box ()

          cnt = len (lines)
          i = 0
          while i < h and top+i < cnt :
               txt = lines [top+i][left:]
               txt = txt [0:w]
               # win.addstr (start_line+i, start_col, txt)
               addstr (win, start_line+i, start_col, txt)
               i = i + 1

          txt = "top = " + str (top) + ", left = " + str (left) + ", step = " + str (step)
          if border :
             win.addstr (h+1, 1, txt)
          else :
             win.addstr (h, 0, txt)

          "redraw window"
          win.refresh ()


       "wait for key"
       win.timeout (-1)
       key = win.getch ()
       while key == -1 :
          key = win.getch ()

       if key == -1 :
          redraw = False
       else :
          redraw = True
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
   try :
      scr = curses.initscr ()
      curses.cbreak ()
      curses.noecho ()
      # scr.timeout (100)
      scr.keypad (True)

      menu_func (scr)
   finally :
      curses.nocbreak ()
      scr.keypad (False)
      curses.echo ()
      curses.endwin ()
"""

# --------------------------------------------------------------------------

if __name__ == '__main__':
   # locale.setlocale(locale.LC_ALL, "")

   lines = [ ]
   # for line in sys.stdin :
   # for line in open (3, "r") :
   for line in open (0, "r") :
       line = line.rstrip ()
       lines.append (line)
       print (line)


   """
   # lines = lines [0:9]
   line = 4*"0123456789"
   lines = ["abc", "def", "klm"] + 5 * [ line ] + ["xyz"] + [line]
   """

   # print (80*'-')
   # for line in lines :
   #     print (line)

   sys.stdin.close ()
   sys.stdin = open ("/dev/tty", "r")

   curses.wrapper (menu_func)

# --------------------------------------------------------------------------

"""
for line in open (3, "r") :

cat test.txt | python filter.py 3<&0- </dev/tty
valac lexer.vala pas_parser.vala  2>&1 | python filter.py 3<&0- </dev/tty
valac lexer.vala pas_parser.vala --color 2>&1 | python filter.py 3<&0- </dev/tty

last character in 3<&0- is minus
http://www.gnu.org/software/bash/manual/html_node/Redirections.html#Moving-File-Descriptors

"""

"""
gcc ... --color-always | less -R
less command, open keybord, file ttyin.c
https://askubuntu.com/questions/678915/whats-the-difference-between-and-in-bash
"""

"""
for line in open (0, "r") :
NOT for line in sys.stdin :

sys.stdin.close ()
sys.stdin = open ("/dev/tty", "r")

clear ; valac lexer.vala --color 2>&1 | python filter.py
"""

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
