#! /usr/bin/python3

import curses
import glob

class cols_scanner(object):
    '''
    Scan the columns in a row.
    cols_scanner.get_count(col) returns the number of neighbors in this row at col.
    get_count is set to the appropriate (get_*) method as the scan progresses.
    Arguments to get_count must be non-decreasing.

    self.nxt_iter is the column iterator.
    self.prv is the column to the left of self.cur ow/ None.
    self.cur is the current column ow/ None.
    self.nxt is the next column after self.cur ow/ None.
    initially we are before the first column, self.prv and self.cur are None

    assert: self.prv is None or self.cur is None or self.prv < self.cur
    assert: self.cur is None or self.cur <= col
    assert: self.nxt is None or col < self.nxt

    get_count strategy: self.prv < self.cur <= col < self.nxt

    rule: it is not allowed to call get_count with a smaller col than before.
    rule: it is not allowed to call get_count with the same col twice.
    get_count advances to the next state when called.
    These rules allow not having a dummy scan at the end of every row.

    _get... name key: after _get is a sequence of what needs to happen
    curnxt = while col < self.nxt - 1: return 0
    1 = return 1
    2 = return 2
    3 = return 3
    0 = while True: return 0
    _first = _advance_first
    _plain = _advance_plain
    _last = _advance_last
    _only = _advance_only
    This means get_count contains the current state

    self.get_XY
        X in [012n] is the number of empty cells between self.cur and self.prv, n means > 2
        Y in [01nx] is the number of empty cells between self.cur and self.nxt, n means > 1, x means there are no more self.nxt
    self.get_n? => either self.prv is None or self.prv + 1 < col
    '''

    def __init__(self, col_list):
        self.nxt_iter = col_list.__iter__()
        self.prv = None
        self.cur = None # None never == col
        if len(col_list) == 0: # an empty row
            self.nxt = None
            self.get_count = self._get_0
        else:
            self.nxt = next(self.nxt_iter)
            self.get_count = self._get_curnxt_only_1 if len(col_list) == 1 else self._get_curnxt_1_first

    # assert: get_count has never been called
    def first_interesting_column(self): return None if self.nxt is None else self.nxt - 1

    # assert: get_count was just called with the same col
    def is_live(self, col): return col == self.cur or col == self.nxt or col == self.prv

    def _next_interesting_column_relative_to_row(self, row, col):
        if col < row - 1:
            return row - 1
        if col == row - 1:
            return row
        return row + 1
    # assert: get_count was just called with the same col
    def next_interesting_column(self, col):
        if self.prv is not None and col <= self.prv: # self.prv could have been self.cur just before get_count(col)
            return self._next_interesting_column_relative_to_row(self.prv, col)
        if self.cur is not None and col <= self.cur:
            return self._next_interesting_column_relative_to_row(self.cur, col)
        if self.nxt is not None and col <= self.nxt:
            return self._next_interesting_column_relative_to_row(self.nxt, col)
        return None

    # _first

    def _get_curnxt_1_first(self, col): # cur_nxt=0=col . nxtm1=1 . nxt
        if col < self.nxt - 1:
            return 0
        self.get_count = self._get_1_first
        return self.get_count(col)

    def _get_1_first(self, col): # nxtm1=1 . nxt
        self._advance_first(col)
        return 1

    def _advance_end(self, col):
        self.nxt = None
        self.get_count = [self._get_2_last_1, self._get_1_last_1][min(self.cur - self.prv - 1, 1)]

    def _advance_first(self, col):
        ''' The first advance of the row '''
        self.prv = self.cur # None
        self.cur = self.nxt # not None
        try:
            self.nxt = next(self.nxt_iter)
            self.get_count = [self._get_plain_2, self._get_1_plain_2, self._get_1_1_plain_1, self._get_1_1_curnxt_plain_1][min(self.nxt - self.cur - 1, 3)]
        except StopIteration: # *x
            self._advance_end(col)

    # _plain

    def _get_plain_3(self, col): # prv . cur=3=col . nxt
        self._advance_plain(col)
        return 3

    def _get_2_plain_2(self, col): # prv . cur=2=col . nxtm1=2 . nxt
        self.get_count = self._get_plain_2
        return 2

    def _get_2_1_plain_1(self, col): # prv . cur=2=col . curp1=1 . nxtm1=1 . nxt
        self.get_count = self._get_1_plain_1
        return 2

    def _get_2_1_curnxt_plain_1(self, col): # prv . cur=2=col . curp1=1 . cur_nxt=0 . nxtm1=1 . nxt
        self.get_count = self._get_1_curnxt_plain_1
        return 2

    def _get_1_plain_2(self, col): # prv . curm1 . cur=1=col . nxtm1=2 . nxt
        self.get_count = self._get_plain_2
        return 1

    def _get_plain_2(self, col): # nxtm1=2=col . nxt
        self._advance_plain(col)
        return 2

    def _get_1_1_plain_1(self, col): # prv . curm1 . cur=1=col . curp1=1 . nxtm1=1 . nxt
        self.get_count = self._get_1_plain_1
        return 1

    def _get_1_plain_1(self, col): # curp1=1=col . nxtm1=1 . nxt
        self.get_count = self._get_plain_1
        return 1

    def _get_1_1_curnxt_plain_1(self, col): # prv . curm1 . cur=1=col . curp1=1 . cur_nxt=0 . nxtm1=1 . nxt
        self.get_count = self._get_1_curnxt_plain_1
        return 1

    def _get_1_curnxt_plain_1(self, col): # curp1=1=col . cur_nxt=0 . nxtm1=1 . nxt
        self.get_count = self._get_curnxt_plain_1
        return 1
    def _get_curnxt_plain_1(self, col): # cur_nxt=0=col . nxtm1=1 . nxt
        if col < self.nxt - 1:
            return 0
        self.get_count = self._get_plain_1
        return self.get_count(col)

    def _get_plain_1(self, col): # nxtm1=1=col . nxt
        self._advance_plain(col)
        return 1

    def _advance_plain(self, col):
        ''' Plain middle advances '''
        self.prv = self.cur
        self.cur = self.nxt
        try:
            self.nxt = next(self.nxt_iter)
            self.get_count = [
                    [self._get_plain_3, self._get_2_plain_2, self._get_2_1_plain_1, self._get_2_1_curnxt_plain_1],
                    [self._get_plain_2, self._get_1_plain_2, self._get_1_1_plain_1, self._get_1_1_curnxt_plain_1]
                    ][min(self.cur - self.prv - 1, 1)][min(self.nxt - self.cur - 1, 3)]
        except StopIteration: # There are no more columns
            self._advance_end(col)

    # _last

    def _get_2_last_1(self, col): # prv . cur=2=col . curp1=1 . ...
        self.get_count = self._get_last_1
        return 2

    def _get_1_last_1(self, col): # cur=1=col . curp1=1 . ...
        self.get_count = self._get_last_1
        return 1

    def _get_last_1(self, col): # curp1=1=col . ...
        self._advance_last(col)
        return 1

    def _advance_last(self, col): # end
        ''' Plain last advance '''
        self.prv = self.cur
        self.cur = None # never == col
        self.get_count = self._get_0

    # _only

    def _get_curnxt_only_1(self, col): # cur_nxt=0=col . nxtm1=1 . cur=1 . curp1=1 . ...
        if col < self.nxt - 1:
            return 0
        self.get_count = self._get_only_1
        return self.get_count(col)
    def _get_only_1(self, col): # nxtm1=1=col . cur=1 . curp1=1 . ...
        self._advance_only(col)
        return 1
    def _advance_only(self, col):
        ''' The middle advance for a row with only one column '''
        self.prv = self.cur
        self.cur = self.nxt
        self.nxt = None
        self.get_count = self._get_1_last_1

    # _0

    def _get_0(self, col): # ...=0
        return 0

    def __str__(self):
        return ('cols_scanner('
                + ' prv=' + str(self.prv)
                + ' cur=' + str(self.cur)
                + ' nxt=' + str(self.nxt)
                + ' get=' + str(self.get_count)
                + ')')

class cw(object):
    ''' sparse coordinate collection: '''

    def __init__(self, initial_rows=None):
        self.rows = [] if initial_rows is None else initial_rows # [(row_number, [col_number ...])]

    # displaying

    def bounds(self): # (top, left, bottom, right)
        if len(self.rows) > 0:
            return (self.rows[0][0], min(row[1][0] for row in self.rows), self.rows[-1][0] + 1, max(row[1][-1] for row in self.rows) + 1)
        else:
            return (None, None, None, None)

    def prt(self, scr, cw_top=0, cw_left=0, top=0, left=0, bottom=None, right=None):
        if bottom is None: bottom = r_max
        if right is None: right = c_max
        row_delta = top - cw_top
        col_delta = left - cw_left
        cw_bottom = bottom - row_delta
        cw_right = right - col_delta
        scr.clear()
        for row_number, cols in self.rows: # [(row_number, [col_number ...]) ...]
            if cw_bottom <= row_number: # the rest is below the bottom of the screen
                break
            if cw_top <= row_number: # else above the top of the screen
                screen_row = row_number + row_delta
                for col_number in cols:
                    if cw_right <= col_number: # the rest is to the right of the screen
                        break
                    if cw_left <= col_number: # else to the left of the screen
                        scr.addch(screen_row, col_number + col_delta, '*')

    # editing

    def is_set(self, row, col):
        for row_number, cols in self.rows:
            if row_number == row: # found the row
                return col in cols
            elif row_number > row: # no such row
                return False
        return False # below everything

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
    def clr(self, row, col): self._change(row, col, -1)
    def toggle(self, row, col): self._change(row, col, 0)
    def set(self, row, col): self._change(row, col, 1)

    def clear(self): self.rows = []

    def _merge_row(self, old_cols, the_cols):
        if len(the_cols) <= 0: # nothing to add
            return old_cols
        the_cols_iter = the_cols.__iter__()
        the_col = next(the_cols_iter)
        new_cols = []
        try:
            old_cols_iter = old_cols.__iter__()
            old_col = next(old_cols_iter)
            while True:
                while the_col > old_col:
                    new_cols.append(old_col)
                    old_col = next(old_cols_iter)
                # the_col <= old_col
                try:
                    while the_col < old_col:
                        new_cols.append(the_col)
                        the_col = next(the_cols_iter)
                    # the_col >= old_col
                except StopIteration:
                    new_cols.append(old_col)
                    new_cols.extend(old_cols_iter)
                    break
                if the_col != old_col:
                    continue
                try:
                    new_cols.append(old_col)
                    the_col = next(the_cols_iter)
                except StopIteration:
                    # new_cols.append(old_col)
                    new_cols.extend(old_cols_iter)
                    break
                old_col = next(old_cols_iter)
        except StopIteration:
            new_cols.append(the_col)
            new_cols.extend(the_cols_iter)
        return new_cols
    def merge(self, the_rows):
        if len(the_rows) <= 0: # nothing to add
            return
        the_rows_iter = the_rows.__iter__()
        the_row_number, the_cols = next(the_rows_iter)
        new_rows = [(0, [0, 1])]
        try:
            old_rows_iter = self.rows.__iter__()
            old_row_number, old_cols = next(old_rows_iter)
            while True:
                while the_row_number > old_row_number:
                    new_rows.append((old_row_number, old_cols))
                    old_row_number, old_cols = next(old_rows_iter)
                # the_row_number <= old_row_number
                try:
                    while the_row_number < old_row_number:
                        new_rows.append((the_row_number, the_cols[:]))
                        the_row_number, the_cols = next(the_rows_iter)
                    # the_row_number >= old_row_number
                except StopIteration:
                    new_rows.append((old_row_number, old_cols))
                    new_rows.extend(old_rows_iter)
                    break
                if the_row_number != old_row_number:
                    continue
                try:
                    new_rows.append((the_row_number, self._merge_row(old_cols, the_cols))) # merge the two rows
                    the_row_number, the_cols = next(the_rows_iter)
                except StopIteration:
                    # new_rows.append((old_row_number, old_cols))
                    new_rows.extend(old_rows_iter)
                    break
                old_row_number, old_cols = next(old_rows_iter)
        except StopIteration:
            new_rows.append((the_row_number, the_cols[:]))
            new_rows.extend((row_number, cols[:]) for row_number, cols in the_rows_iter)
        self.rows = new_rows

    # generations

    def _best_col_number(self, prv, cur, nxt):
        if cur is not None and (prv is None or prv > cur): prv = cur
        if nxt is not None and (prv is None or prv > nxt): prv = nxt
        return prv

    def _first_col_number(self, prv_cols, cur_cols, nxt_cols):
        return self._best_col_number(
            prv_cols.first_interesting_column(),
            cur_cols.first_interesting_column(),
            nxt_cols.first_interesting_column())

    def _next_col_number(self, col_number, prv_cols, cur_cols, nxt_cols):
        return self._best_col_number(
            prv_cols.next_interesting_column(col_number),
            cur_cols.next_interesting_column(col_number),
            nxt_cols.next_interesting_column(col_number))

    def generation(self):
        new_rows = []
        prv_row = None # new_row_number - 1 ow/ None
        cur_row = None # new_row_number ow/ None
        nxt_row = None # new_row_number + 1 ow/ None
        r = 0 # next self.rows[*} to pull in
        len_self_rows = len(self.rows)
        while True:
            # calculate new_row_number, advance row_*, r
            if cur_row is not None: # advance to cur_row[0] + 1
                new_row_number = cur_row[0] + 1
                prv_row = cur_row
                cur_row = nxt_row
                if r < len_self_rows and self.rows[r][0] == new_row_number + 1:
                    nxt_row = self.rows[r]
                    r += 1
                else:
                    nxt_row = None
            elif nxt_row is not None: # cur_row is None, advance to nxt_row[0]
                new_row_number = nxt_row[0]
                prv_row = None
                cur_row = nxt_row
                if r < len_self_rows and self.rows[r][0] == new_row_number + 1:
                    nxt_row = self.rows[r]
                    r += 1
                else:
                    nxt_row = None
            elif r < len_self_rows: # cur_row is None and nxt_row is None, advance to self.rows[r][0] - 1
                new_row_number = self.rows[r][0] - 1
                prv_row = None
                cur_row = None
                nxt_row = self.rows[r]
                r += 1
            else: # cur_row is None and nxt_row is None and r == len_self_rows, stop
                break

            # produce new row (a new cur_row)

            prv_cols = cols_scanner(prv_row[1] if prv_row else [])
            cur_cols = cols_scanner(cur_row[1] if cur_row else [])
            nxt_cols = cols_scanner(nxt_row[1] if nxt_row else [])

            new_cols = [] # the new cur_cols
            col_number = self._first_col_number(prv_cols, cur_cols, nxt_cols)
            while col_number is not None:
                ## append new item to new_cols, if needed
                neighbor_count = prv_cols.get_count(col_number) + cur_cols.get_count(col_number) + nxt_cols.get_count(col_number)
                if cur_cols.is_live(col_number):
                    if neighbor_count - 1 in [2, 3]:
                        new_cols.append(col_number)
                else:
                    if neighbor_count == 3:
                        new_cols.append(col_number)
                col_number = self._next_col_number(col_number, prv_cols, cur_cols, nxt_cols)
            if len(new_cols) > 0:
                new_rows.append((new_row_number, new_cols))

        return cw(new_rows)

    def __str__(self):
        return '[' + ' '.join('(' + str(row_number) + ', ' + '[' + ', '.join(str(c) for c in cols) + ']' + ')' for row_number, cols in self.rows) + ']'

# utilities

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
                col += 1
            row += 1

def add_rle_at(conway, y, x, filename):
    new_rows = []
    new_row = []
    row = y
    col = x
    number = 0
    with open(filename, 'r') as f:
        for line in f:
            if len(line) <= 0:
                continue
            if line[0] == '#':
                continue
            if line[0] == 'x':
                continue
            for c in line:
                if c.isdigit():
                    number = 10 * number + ord(c) - ord('0')
                elif c == 'b':
                    col += max(number, 1)
                    number = 0
                elif c == 'o':
                    for _ in range(max(number, 1)):
                        new_row.append(col)
                        col += 1
                    number = 0
                elif c == '$':
                    if len(new_row) > 0: new_rows.append((row, new_row))
                    new_row = []
                    row += max(number, 1)
                    col = x
                    number = 0
                elif c == '!':
                    break
                # else some unknown character, ignore it
    if len(new_row) > 0: new_rows.append((row, new_row))
    conway.merge(new_rows)

menu_item_number = 0
def get_menu(scr):
    global menu_item_number
    # build menu
    filenames = sorted(glob.glob('*.cw') + glob.glob('*.rle'))
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
        menu_item_number = lim(menu_item_number, height - 2)
        scr.move(begin_y + menu_item_number + 1, begin_x + 1)
        # process menu input
        while True:
            c = scr.getch()
            if c < 0:
                continue
            if c == curses.KEY_UP:
                menu_item_number = lim(menu_item_number - 1, height - 2)
            elif c == curses.KEY_DOWN:
                menu_item_number = lim(menu_item_number + 1, height - 2)
            elif c == ord('\t'): # tab
                return None
            elif c == ord('\n'):
                return filenames[menu_item_number]
            scr.move(begin_y + menu_item_number + 1, begin_x + 1)
    finally:
        del menu

def main(stdscr):
    global r_max, c_max
    stdscr.clear()
    stdscr.nodelay(True)
    stdscr.leaveok(False)

    r_max, c_max = curses.LINES, curses.COLS # stdscr.getmaxyx()
    c_max -= 1 # TODO: did not look into why it breaks without this

    row, col = r_max // 2, c_max // 2 # cursor position
    cw_top, cw_left = 0, 0 # cw coordinates of stdscr (0, 0)

    conway = cw()
    # Add a glider
    conway.set(row + 0, col + 1)
    conway.set(row + 1, col + 2)
    conway.set(row + 2, col + 0)
    conway.set(row + 2, col + 1)
    conway.set(row + 2, col + 2)
    conway.prt(stdscr, cw_top, cw_left)

    fuse = 0 # start not running

    # convention: if you change conway, make sure conway.prt() gets called once
    while True:
        # do a generation, if running
        if fuse != 0:
            if fuse > 0: fuse -= 1
            conway = conway.generation()
            conway.prt(stdscr, cw_top, cw_left)
        # check for input character
        stdscr.refresh()
        stdscr.move(row, col)
        c = stdscr.getch()
        if c < 0:
            continue
        # process input character
        if c == ord(' '): fuse = -1 if fuse == 0 else 0 # toggle pause
        elif ord('1') <= c <= ord('9'): fuse = c - ord('0') # run n genrations
        elif c == curses.KEY_LEFT: col -= 1
        elif c == curses.KEY_RIGHT: col += 1
        elif c == curses.KEY_UP: row -= 1
        elif c == curses.KEY_DOWN: row += 1
        elif c == ord('O'): # original origin
            cw_top = 0
            cw_left = 0
            if fuse == 0: conway.prt(stdscr, cw_top, cw_left)
        elif c == ord('H'): # LEFT
            cw_left -= c_max // 2
            if fuse == 0: conway.prt(stdscr, cw_top, cw_left)
        elif c == ord('L'): # RIGHT
            cw_left += c_max // 2
            if fuse == 0: conway.prt(stdscr, cw_top, cw_left)
        elif c == ord('K'): # UP
            cw_top -= r_max // 2
            if fuse == 0: conway.prt(stdscr, cw_top, cw_left)
        elif c == ord('J'): # DOWN
            cw_top += r_max // 2
            if fuse == 0: conway.prt(stdscr, cw_top, cw_left)
        elif c == ord('h'): # left
            cw_left -= c_max // 10
            if fuse == 0: conway.prt(stdscr, cw_top, cw_left)
        elif c == ord('l'): # right
            cw_left += c_max // 10
            if fuse == 0: conway.prt(stdscr, cw_top, cw_left)
        elif c == ord('k'): # up
            cw_top -= r_max // 10
            if fuse == 0: conway.prt(stdscr, cw_top, cw_left)
        elif c == ord('j'): # down
            cw_top += r_max // 10
            if fuse == 0: conway.prt(stdscr, cw_top, cw_left)
        elif c == ord('c'): # clear the whole thing
            conway.clear()
            if fuse == 0: conway.prt(stdscr, cw_top, cw_left)
        elif c == ord('m'): # get menu input
            filename = get_menu(stdscr)
            if filename is not None:
                if filename.endswith('.cw'):
                    add_cw_at(conway, cw_top + row, cw_left + col, filename)
                elif filename.endswith('.rle'):
                    add_rle_at(conway, cw_top + row, cw_left + col, filename)
                # else we don't understand filename
                if fuse == 0: conway.prt(stdscr, cw_top, cw_left)
        elif c == ord('q'): # quit
            return
        elif c == ord('.'): # toggle (row, col)
            conway.toggle(cw_top + row, cw_left + col)
            if fuse == 0: conway.prt(stdscr, cw_top, cw_left)

curses.wrapper(main)
