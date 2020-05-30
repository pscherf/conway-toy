#! /usr/bin/python3

import curses
import glob
import random
import sys

class column_scanner(object):
    '''
    Scan the columns in a row.
    column_scanner.get_count(col) returns the number of neighbors in this row at col.
    get_count is set to the appropriate (get_*) method as the scan progresses.
    Arguments to get_count must be non-decreasing.

    self.nxt_iter is the column iterator.
    self.prv is the cell to the left ow/ None.
    self.cur is the current cell ow/ None.
    self.nxt is the next cell to scan ow/ None.
    assert: self.prv < self.cur < self.nxt, if they are not None
    assert: self.prv is None or self.prv < col
    assert: self.cur is None or col <= self.cur (or col <= self.cur + 1)
    assert: self.nxt is None or col < self.nxt
    self.on_empty is called when the scan passes the last column

    self.get_XY
        X in [012n] is the number of empty cells between self.cur and self.prv, n means > 2
        Y in [01nx] is the number of empty cells between self.cur and self.nxt, n means > 1, x means there are no more self.nxt
    self.get_n? => either self.prv is None or self.prv + 1 < col
    '''

    def __init__(self, col_list, on_empty):
        self.nxt_iter = col_list.__iter__()
        self.on_empty = on_empty
        #
        self.prv = None
        if len(col_list) == 0:
            self.cur = None # None never == col
            self.nxt = None
            self.on_empty()
            self.get_count = self._get_end
            return
        # get a first self.cur
        self.cur = next(self.nxt_iter)
        if len(col_list) == 1:
            self.nxt = None
            self.get_count = self._get_nx
            return
        # get a first self.nxt
        self.nxt = next(self.nxt_iter)
        if self.cur == self.nxt - 1:
            self.get_count = self._get_n0
        elif self.cur == self.nxt - 2:
            self.get_count = self._get_n1
        else:
            self.get_count = self._get_nn

    # assumes get_count was just called with the same col
    def is_live(self, col): return col == self.cur or col == self.prv or col == self.nxt

    def first_interesting_column(self): return None if self.cur is None else self.cur - 1

    # assumes get_count was just called with the same col
    def next_interesting_column(self, col): # ow/ None
        # assert: self.prv < col <= self.cur + 1, unless self.prv or self.cur are None
        if self.cur is not None: # cur - 1, cur, cur + 1
            if col < self.cur - 1:
                return self.cur - 1
            if col < self.cur + 1:
                return col + 1
        if self.nxt is not None: # nxt - 1, nxt, nxt + 1
            if col < self.nxt - 1:
                return self.nxt - 1
            if col < self.nxt + 1:
                return col + 1
        return None # nothing is interesting

    # get_count

    def _advance_not_end(self, col):
        ''' Advance from the current get_*[01n] to the next get_* '''
        while col > self.cur:
            self.prv = self.cur
            self.cur = self.nxt
            try:
                self.nxt = next(self.nxt_iter)
            except StopIteration: # *x
                self.nxt = None
                if self.prv + 1 == self.cur:
                    self.get_count = self._get_0x
                elif self.prv + 2 == self.cur:
                    self.get_count = self._get_1x
                elif self.prv + 3 == self.cur:
                    self.get_count = self._get_2x
                else:
                    self.get_count = self._get_nx
                break
        else:
            if self.cur == self.nxt - 1: # *0
                if self.prv + 1 == self.cur:
                    self.get_count = self._get_00
                elif self.prv + 2 == self.cur:
                    self.get_count = self._get_10
                elif self.prv + 3 == self.cur:
                    self.get_count = self._get_20
                else:
                    self.get_count = self._get_n0
            elif self.cur == self.nxt - 2: # *1
                if self.prv + 1 == self.cur:
                    self.get_count = self._get_01
                elif self.prv + 2 == self.cur:
                    self.get_count = self._get_11
                elif self.prv + 3 == self.cur:
                    self.get_count = self._get_21
                else:
                    self.get_count = self._get_n1
            else: # self.cur < self.nxt - 2 # *n
                if self.prv + 1 == self.cur:
                    self.get_count = self._get_0n
                elif self.prv + 2 == self.cur:
                    self.get_count = self._get_1n
                elif self.prv + 3 == self.cur:
                    self.get_count = self._get_2n
                else:
                    self.get_count = self._get_nn
        return self.get_count(col)

    def _advance_from_end(self, col): # end
        ''' Advance from the current get_*x to _get_end '''
        self.prv = self.cur
        self.cur = None # never == col
        self.on_empty()
        self.get_count = self._get_end
        return self.get_count(col) # parameter ignored

    def _get_00(self, col):
        ''' prv cur nxt
             .   3   . '''
        if col <= self.cur:
            return 3
        return self._advance_not_end(col)

    def _get_10(self, col):
        ''' prv  .  cur nxt
             .   2   2   . '''
        if col <= self.cur:
            return 2
        return self._advance_not_end(col)

    def _get_20(self, col):
        ''' prv  .   .  cur nxt
             .   1   1   2   . '''
        if col < self.cur:
            return 1
        if col == self.cur:
            return 2
        return self._advance_not_end(col)

    def _get_n0(self, col):
        ''' ...  .  cur nxt
             0   1   2   . '''
        if col < self.cur - 1:
            return 0
        if col < self.cur:
            return 1
        if col <= self.cur:
            return 2
        return self._advance_not_end(col)

    def _get_01(self, col):
        ''' prv cur  .  nxt
             .   2   2   . '''
        if col <= self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def _get_11(self, col):
        ''' prv  .  cur  .  nxt
             .   2   1   2   . '''
        if col < self.cur:
            return 2
        if col <= self.cur:
            return 1
        if col <= self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def _get_21(self, col):
        ''' prv  .   .  cur  .  nxt
             .   1   1   1   2   . '''
        if col <= self.cur:
            return 1
        if col <= self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def _get_n1(self, col):
        ''' ...  .  cur  .  nxt
             0   1   1   2   . '''
        if col < self.cur - 1:
            return 0
        if col <= self.cur:
            return 1
        if col <= self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def _get_0n(self, col):
        ''' prv cur  .  ... nxt
             .   2   1   .   . '''
        if col <= self.cur:
            return 2
        if col <= self.cur + 1:
            return 1
        return self._advance_not_end(col)

    def _get_1n(self, col):
        ''' prv  .  cur  .  ... nxt
             .   2   1   1   .   . '''
        if col < self.cur:
            return 2
        if col <= self.cur + 1:
            return 1
        return self._advance_not_end(col)

    def _get_2n(self, col):
        ''' prv  .   .  cur  .  ... nxt
             .   1   1   1   1   .   .'''
        if col <= self.cur + 1:
            return 1
        return self._advance_not_end(col)

    def _get_nn(self, col):
        ''' ...  .  cur  .  ... nxt
             0   1   1   1   .   . '''
        if col < self.cur - 1:
            return 0
        if col <= self.cur + 1:
            return 1
        return self._advance_not_end(col)

    def _get_0x(self, col):
        ''' prv cur  .  ...
             .   2   1   . '''
        if col <= self.cur:
            return 2
        if col <= self.cur + 1:
            return 1
        return self._advance_from_end(col)

    def _get_1x(self, col):
        ''' prv  .  cur  .  ...
             .   2   1   1   . '''
        if col < self.cur:
            return 2
        if col <= self.cur + 1:
            return 1
        return self._advance_from_end(col)

    def _get_2x(self, col):
        ''' prv  .   .  cur  .  ...
             .   1   1   1   1   . '''
        if col <= self.cur + 1:
            return 1
        return self._advance_from_end(col)

    def _get_nx(self, col):
        ''' ...  .  cur  .  ...
             0   1   1   1   . '''
        if col < self.cur - 1:
            return 0
        if col <= self.cur + 1:
            return 1
        return self._advance_from_end(col)

    def _get_end(self, col):
        ''' ...
             0 '''
        return 0

    def __str__(self):
        return ('column_scanner('
                + ' prv=' + str(self.prv)
                + ' cur=' + str(self.cur)
                + ' nxt=' + str(self.nxt)
                + ' get=' + str(self.get_count)
                + ')')

class cw(object):
    ''' sparse coordinate collection: '''

    def __init__(self, initial_rows=None):
        self.rows = [] if initial_rows is None else initial_rows # [(row_number, [col_number ...])]

    def prt(self, scr):
        scr.clear()
        for row_number, cols in self.rows: # [(row_number, [col_number ...]) ...]
            if r_max <= row_number: # the rest is below the bottom of the screen
                break
            if 0 <= row_number: # else above the top of the screen
                for col_number in cols:
                    if c_max <= col_number: # stuff to the right of the screen
                        break
                    if 0 <= col_number: # else stuff to the left of the screen
                        scr.addch(row_number, col_number, '*')

    def _first_col_number(self, cols_prv, cols_cur, cols_nxt):
        return min((interesting_column for interesting_column in [
                cols_prv.first_interesting_column(),
                cols_cur.first_interesting_column(),
                cols_nxt.first_interesting_column()
            ] if interesting_column is not None), default=None)

    def _next_col_number(self, col_number, cols_prv, cols_cur, cols_nxt):
        return max(col_number + 1, min((interesting_column for interesting_column in [
                cols_prv.next_interesting_column(col_number),
                cols_cur.next_interesting_column(col_number),
                cols_nxt.next_interesting_column(col_number)
            ] if interesting_column is not None), default=col_number + 1))

    def generation(self):
        new_rows = []
        row_prv = None # old row_number_new - 1 ow/ None
        row_cur = None # old row_number_new ow/ None
        row_nxt = None # old row_number_new + 1 ow/ None
        r = 0 # next self.rows[*} to pull in
        len_self_rows = len(self.rows)
        while True:
            # calculate row_number_new, advance row_*, r
            if row_cur is not None: # advance to row_cur[0] + 1
                row_number_new = row_cur[0] + 1
                row_prv = row_cur
                row_cur = row_nxt
                if r < len_self_rows and self.rows[r][0] == row_number_new + 1:
                    row_nxt = self.rows[r]
                    r += 1
                else:
                    row_nxt = None
            elif row_nxt is not None: # row_cur is None, advance to row_nxt[0]
                row_number_new = row_nxt[0]
                row_prv = None
                row_cur = row_nxt
                if r < len_self_rows and self.rows[r][0] == row_number_new + 1:
                    row_nxt = self.rows[r]
                    r += 1
                else:
                    row_nxt = None
            elif r < len_self_rows: # row_cur is None and row_nxt is None, advance to self.rows[r][0] - 1
                row_number_new = self.rows[r][0] - 1
                row_prv = None
                row_cur = None
                row_nxt = self.rows[r]
                r += 1
            else: # row_cur is None and row_nxt is None and r == len_self_rows, stop
                break

            # produce new row (a new row_cur)

            past_end_list = [0]
            def on_past_end(past_end_list=past_end_list): past_end_list[0] += 1
            cols_prv = column_scanner(row_prv[1] if row_prv else [], on_past_end)
            cols_cur = column_scanner(row_cur[1] if row_cur else [], on_past_end)
            cols_nxt = column_scanner(row_nxt[1] if row_nxt else [], on_past_end)

            cols_new = [] # the new cols_cur
            col_number = self._first_col_number(cols_prv, cols_cur, cols_nxt)
            while past_end_list[0] < 3:
                ## append new item to cols_new, if needed
                neighbor_count = cols_prv.get_count(col_number) + cols_cur.get_count(col_number) + cols_nxt.get_count(col_number)
                if cols_cur.is_live(col_number):
                    if neighbor_count - 1 in [2, 3]:
                        cols_new.append(col_number)
                else:
                    if neighbor_count == 3:
                        cols_new.append(col_number)
                col_number = self._next_col_number(col_number, cols_prv, cols_cur, cols_nxt)
            if len(cols_new) > 0:
                new_rows.append((row_number_new, cols_new))

        return cw(new_rows)

    def is_set(self, row, col):
        for row_number, cols in self.rows:
            if row_number == row: # found the row
                return col in cols
            elif row_number > row: # no such row
                return False
        return False # below everything

    def clr(self, row, col): self._change(row, col, -1)
    def toggle(self, row, col): self._change(row, col, 0)
    def set(self, row, col): self._change(row, col, 1)

    def _change(self, row, col, change_type): # -1 == clr, 0 == toggle, 1 == set
        for r in range(len(self.rows)):
            row_number, cols = self.rows[r]
            if row_number == row: # found the row
                for c in range(len(cols)):
                    col_number = cols[c]
                    if col_number == col: # existing col not at end
                        if change_type != 1:
                            cols.remove(col)
                            if len(cols) == 0: # last entry in row
                                del self.rows[r]
                        return
                    elif col_number > col: # new col not at end
                        if change_type != -1: cols.insert(c, col)
                        return
                if change_type != -1: cols.append(col) # new col at end
                return
            elif row_number > row: # new row not at end
                if change_type != -1: self.rows.insert(r, (row, [col]))
                return
        if change_type != -1: self.rows.append((row, [col])) # new row at end

    def clear(self): self.rows = []

    def __str__(self):
        return '[' + ' '.join('(' + str(row_number) + ', ' + '[' + ', '.join(str(c) for c in cols) + ']' + ')' for row_number, cols in self.rows) + ']'

# cw tests

def screen_test(stdscr):
    width = 64
    height = 64
    margin = 10
    failed = False
    stdscr.clear()
    random.seed(1) # so we can re-run the test

    if width + margin + width >= c_max:
        stdscr.addstr(0, 0, 'width=' + str(width) + ' + ' + ' margin=' + str(margin) + ' + ' + ' width=' + str(width) + ' >= ' + ' cols=' + str(c_max))
        failed = True
    if height + margin + height >= r_max:
        stdscr.addstr(1, 0, 'height=' + str(height) + ' + ' + ' margin=' + str(margin) + ' + ' + ' height=' + str(height) + ' >= ' + ' cols=' + str(r_max))
        failed = True
    if failed:
        return

    # initialize old_screen
    old_screen = [[random.randrange(2) != 0 for _ in range(width)] for _ in range(height)]

    # initialize old_conway
    old_conway = cw()
    for r in range(height):
        for c in range(width):
            if old_screen[r][c]:
                old_conway.set(r, c)

    # calculate new_screen
    def calculate(row, col):
        is_live = False
        count = 0
        for r in range(3):
            for c in range(3):
                r_sub = row + r - 1
                c_sub = col + c - 1
                if 0 <= r_sub < height and 0 <= c_sub < width and old_screen[r_sub][c_sub]:
                    if r == 0 and c == 0:
                        is_live = True
                    else:
                        count += 1
        if is_live:
            return count in [2, 3]
        else:
            return count == 3
    new_screen = [[calculate(row, col) for col in range(width)] for row in range(height)]

    # calculate new_conway
    new_conway = old_conway.generation()

    # compare solution
    for row in range(1, height - 1):
        for col in range(1, width - 1):
            if new_screen[row][col] != new_conway.is_set(row, col):
                failed = True
                break
        if failed:
            break
    if failed:
        # show old_conway at (0, 0)
        for row in range(height):
            for col in range(width):
                stdscr.addch(row + 0, col + 0, '*' if old_conway.is_set(row, col) else '.')
        # show new_screen at (0, width + margin)
        for row in range(height):
            for col in range(width):
                stdscr.addch(row + 0, col + width + margin, '*' if new_screen[row][col] else '.')
        # show new_conway at (height + margin, 0)
        for row in range(height):
            for col in range(width):
                stdscr.addch(row + height + margin, col, '*' if new_conway.is_set(row, col) else '.')
        # show diff? at (height + margin, width + margin)
        for row in range(height):
            for col in range(width):
                stdscr.addch(row + height + margin, col + width + margin, '+' if new_screen[row][col] != new_conway.is_set(row, col) else '.')
    else:
        stdscr.addstr(0, 0, 'screen_test: succeeded')

def parallel(stdscr, conway):
    def from_conway(conway, row, col):
        count = 0
        for r in range(3):
            for c in range(3):
                is_set = conway.is_set(row + r - 1, col + c - 1)
                if r == 1 and c == 1:
                    is_live = is_set
                else:
                    count += int(is_set)
        if is_live:
            return count in [2, 3]
        else:
            return count == 3


    # compute next generation from conway into a 2D array (new_screen)
    new_screen = [[from_conway(conway, row, col) for col in range(c_max)] for row in range(r_max)]
    # new_conway = conway.generation()
    new_conway = conway.generation()
    # compare new_conway to new_screen
    # display differences (in color?)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_RED)
    for row in range(r_max):
        for col in range(c_max):
            cw = new_conway.is_set(row, col)
            s = new_screen[row][col]
            if cw == s:
                stdscr.addch(row, col, '*' if cw else ' ')
            else:
                stdscr.addch(row, col, '*' if cw else ' ', curses.color_pair(1))
    return new_conway

# utilities

def cw_lim(n, limit): return n

def lim(n, limit):
    while n < 0: n += limit
    while n >= limit: n -= limit
    return n

# command handling

def add_cw_at(conway, y, x, filename):
    with open(filename, 'r') as f:
        row = y
        while True:
            line = f.readline()
            if len(line) == 0:
                break
            col = x
            for ch in line:
                if ch == '*':
                    conway.set(row, col)
                col = cw_lim(col + 1, c_max)
            row = cw_lim(row + 1, r_max)

def add_rle_at(conway, y, x, filename):
    with open(filename, 'r') as f:
        line = f.readline()
        while True:
            if line[0] != '#':
                break
            line = f.readline()
        if line[0] == 'x':
            line = f.readline()
        row = y
        col = x
        number = 0
        while True:
            for c in line:
                if c.isdigit():
                    number = 10 * number + ord(c) - ord('0')
                elif c == 'b':
                    for _ in range(max(number, 1)):
                        conway.clr(row, col)
                        col = cw_lim(col + 1, c_max)
                    number = 0
                elif c == 'o':
                    for _ in range(max(number, 1)):
                        conway.set(row, col)
                        col = cw_lim(col + 1, c_max)
                    number = 0
                elif c == '$':
                    for _ in range(max(number, 1)):
                        row = cw_lim(row + 1, r_max)
                    col = x
                    number = 0
                elif c == '!':
                    return
                # else some unknown character
            line = f.readline()

def get_menu(scr):
    # build menu
    filenames = glob.glob('*.cw') + glob.glob('*.rle')
    height = len(filenames) + 2
    width = max((1 + len(filename) + 1 for filename in filenames), default=40)
    begin_y = r_max // 16
    begin_x = c_max // 16
    menu = curses.newpad(height, width)
    try:
        menu.border('|', '|', '-', '-', '+', '+', '+', '+')
        for i, filename in enumerate(filenames):
            menu.addstr(i + 1, 1, filename)
        # put up menu
        menu.refresh(0,0, begin_y,begin_x, begin_y+height-1,begin_x+width-1)
        number = 0
        scr.move(begin_y + number + 1, begin_x + 1)
        # process menu input
        while True:
            c = scr.getch()
            if c < 0:
                continue
            if c == curses.KEY_UP:
                number = lim(number - 1, height - 2)
            elif c == curses.KEY_DOWN:
                number = lim(number + 1, height - 2)
            elif c == ord('\t'): # tab
                return None
            elif c == ord('\n'):
                return filenames[number]
            scr.move(begin_y + number + 1, begin_x + 1)
    finally:
        del menu

def main(stdscr):
    global r_max, c_max
    stdscr.clear()
    stdscr.nodelay(True)
    # stdscr.timeout(1)
    stdscr.leaveok(False)

    r_max, c_max = curses.LINES, curses.COLS # stdscr.getmaxyx()
    c_max -= 1 # not sure why it breaks without this

    row = r_max // 2
    col = c_max // 2

    conway = cw()
    y = 0
    x = 0
    conway.set(y + 0, x + 1)
    conway.set(y + 1, x + 2)
    conway.set(y + 2, x + 0)
    conway.set(y + 2, x + 1)
    conway.set(y + 2, x + 2)
    conway.prt(stdscr)

    fuse = 0

    while True:
        # then do a generation
        if fuse != 0:
            if fuse > 0: fuse -= 1
            conway = conway.generation()
            conway.prt(stdscr)
            if fuse == 0:
                row = r_max // 2
                col = c_max // 2
        # check for input character
        stdscr.refresh()
        stdscr.move(row, col)
        c = stdscr.getch()
        if c < 0:
            continue
        # process input character
        if c == ord(' '): # toggle pause
            if fuse == 0:
                fuse = -1
            else:
                fuse = 0
                row = r_max // 2
                col = c_max // 2
        elif c == ord('1'): fuse = 1
        elif c == ord('2'): fuse = 2
        elif c == ord('3'): fuse = 3
        elif c == ord('4'): fuse = 4
        elif c == ord('5'): fuse = 5
        elif c == ord('6'): fuse = 6
        elif c == ord('7'): fuse = 7
        elif c == ord('8'): fuse = 8
        elif c == ord('9'): fuse = 9
        elif c == curses.KEY_LEFT: col = cw_lim(col - 1, c_max)
        elif c == curses.KEY_RIGHT: col = cw_lim(col + 1, c_max)
        elif c == curses.KEY_UP: row = cw_lim(row - 1, r_max)
        elif c == curses.KEY_DOWN: row = cw_lim(row + 1, r_max)
        elif c == ord('c'): # clear the whole thing
            conway.clear()
            conway.prt(stdscr)
        elif c == ord('m'): # get menu input
            filename = get_menu(stdscr)
            if filename is not None:
                if filename.endswith('.cw'):
                    add_cw_at(conway, row, col, filename)
                elif filename.endswith('.rle'):
                    add_rle_at(conway, row, col, filename)
                # else we don't understand filename
                conway.prt(stdscr)
        elif c == ord('p'): # do a parallel generation
            fuse = 0 # make sure we are paused
            row = 0
            col = 0
            conway = parallel(stdscr, conway)
        elif c == ord('s'): # run a screen_test
            screen_test(stdscr)
        elif c == ord('q'): # quit
            return
        elif c == ord('.'): # toggle (row, col)
            conway.toggle(row, col)
            conway.prt(stdscr)

curses.wrapper(main)
