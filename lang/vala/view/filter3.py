
import os, sys
import curses

# --------------------------------------------------------------------------

def send_line (line_num, col_num, width, line) :
    "line_num, col_num from 0"
    """
    print ("\033[" + str (line_num+1) + ";1H", sep = "", end = "") # go to line
    line = line [ col_num : ]
    while len (line) < width :
       line = line + " "
    line = line [ : width]
    print (line, end = "")
    return
    """

    inx = 0
    cnt = len (line)

    attr_start = -1
    attr_end = -1

    text_start = -1
    text_end = -1

    col = 0

    while inx < cnt :
       while inx < cnt and  line [inx] == '\033' :
          attr_start = inx
          while inx < cnt and line [inx] != 'm' :
             inx = inx + 1
          inx = inx + 1
          attr_end = inx

       if inx < cnt :
          if col == col_num :
             text_start = inx
          inx = inx + 1
          col = col + 1
          if col == col_num + width :
             text_end = inx

    rest = col_num + width - col

    if text_end == -1 :
       text_end = cnt

    print ("\033[" + str (line_num+1) + ";1H", sep = "", end = "") # go to line
    if attr_start != -1 :
       print (line [attr_start : attr_end], end = "")
    if text_start != -1 :
       print (line [text_start : text_end], end = "")
    if rest > 0 :
       print (rest * ' ', end = "")

# --------------------------------------------------------------------------

def clean_line (line) :
    result = ""
    cnt = len (line)
    inx = 0
    while inx < cnt :
       while inx < cnt and line [inx] == '\033' :
          while inx < cnt and line[inx] != 'm' :
             inx = inx + 1
          inx = inx + 1
       if inx < cnt :
          result.append (line [inx])
    return result

# --------------------------------------------------------------------------

lines = [ ]
# for line in sys.stdin :
# for line in open (3, "r") :
for line in open (0, "r") :
    line = line.rstrip ()
    lines.append (line)
    # print (line, end = "")

sys.stdin.close ()
sys.stdin = open ("/dev/tty", "r")

"""
line = 4*"0123456789"
lines = ["abc", "def", "klm"] + 5 * [ line ] + ["xyz"] + [line]

print (80*'-')
for line in lines :
    print (line)
"""

try :
    scr = curses.initscr ()
    curses.cbreak ()
    curses.noecho ()
    scr.keypad (True)

    top = 0
    left = 0
    cnt = len (lines)

    done = False
    while not done :
        size = scr.getmaxyx ()
        h = size [0]-2
        w = size [1]

        print ("\033[2J", end="") # clear screen
        print ("\033[1;1H", sep = "", end = "") # go to line
        # print ("\033[0J", end="") # clear screen

        inx = 0
        while inx < h-1 :
            if top + inx < cnt :
               text = lines [top + inx]
            else :
               text = ""
            # text = "\033[0m" + text
            send_line (inx, left, w, text)
            # print ("\033[" + str (inx+1) + ";1H", text, sep = "", end = "") # go to line
            inx = inx + 1

        text = "screen " + str (w) + " x " + str (h) + " top = " + str (top) + " left = " + str (left)
        text = "\033[37;44m" + text # white on blue
        send_line (h-1, 0, w, text)
        # text = "\033[" + str(h) + ";1H" + text
        # text = "\033[37;44m" + text # white on blue
        # print (text, end = "")

        # print ("\033[" + str(h+1) + ";1H", end = "")
        # print ("\033[0m", end = "")
        # done = True

        curses.nocbreak ()
        scr.keypad (False)
        curses.echo ()
        curses.endwin ()

        scr = curses.initscr ()
        curses.cbreak ()
        curses.noecho ()
        scr.keypad (True)

        scr.timeout (-1)
        key = scr.getch ()
        while key == -1 :
           key = scr.getch ()

        if key == ord ('q') :
              done = True
        if key == ord ('u') or key == curses.KEY_UP :
           if top > 0 :
              top = top - 1
        if key == ord ('d') or key == curses.KEY_DOWN :
           if top < cnt - 1 :
              top = top + 1
        if key == ord ('l') or key == curses.KEY_LEFT :
           if left > 0 :
              left = left - 1
        if key == ord ('r') or key == curses.KEY_RIGHT :
           left = left + 1
        if key == ord ('h') or key == curses.KEY_HOME :
           top = 0
           left = 0
        if key == ord ('e') or key == curses.KEY_END :
           top = cnt - (h-1)
           if top < 0 :
              top = 0
        if key == ord ('p') or key == curses.KEY_PPAGE : # Page Up
           top = top - (h-1)
           if top < 0 :
              top = 0
        if key == ord ('n') or key == curses.KEY_NPAGE : # Page Down
           top = top + (h-1)
           if top > cnt-1 :
              top = cnt-1

finally :
   curses.nocbreak ()
   scr.keypad (False)
   curses.echo ()
   curses.endwin ()

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
