#! /usr/bin/python3

import curses
import glob
import sys

class col_gen(object):
    '''
    Scan the columns in a row.
    col_gen.get_count(col) returns the number of neighbors in this row at col.
    get_count is set to the appropriate (get_*) method as the scan progresses.
    Arguments to get_count must be non-decreasing.

    self.nxt_iter is the column iterator.
    self.prv is the previous column scanned ow/ None.
    self.cur is the current column being scanned ow/ None.
    self.nxt is the next colum to scan ow/ None.
    self.on_empty is called when the scan passes the last column
    assert: self.prv < self.cur < self.nxt, if they are not None

    self.get_XY
        X in [012n] is the number of empty cells between self.cur and self.prv, n means > 2
        Y in [01nx] is the number of empty cells between self.cur and self.nxt, n means > 1, x means there are no more self.nxt
    '''

    def __init__(self, col_list, on_empty):
        self.col_list = col_list # TODO: for debugging
        self.nxt_iter = col_list.__iter__()
        self.prv = None
        if len(col_list) == 0:
            self.cur = None # None never == col
            self.nxt = None
            on_empty()
            self.get_count = self.get_end
            return
        self.on_empty = on_empty
        # get a first self.cur
        self.cur = next(self.nxt_iter)
        if len(col_list) == 1:
            self.nxt = None
            self.get_count = self.get_nx
            return
        # get a first self.nxt
        self.nxt = next(self.nxt_iter)
        if self.cur == self.nxt - 1:
            self.get_count = self.get_n0
        elif self.cur == self.nxt - 2:
            self.get_count = self.get_n1
        else:
            self.get_count = self.get_nn

    def get_00(self, col):
        ''' prv cur nxt
             .   3   . '''
        if col < self.cur: raise AssertionError('get_00:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur))
        if col <= self.cur:
            return 3
        return self._advance_not_end(col)

    def get_10(self, col):
        ''' prv  .  cur nxt
             .   2   2   . '''
        if col < self.cur - 1: raise AssertionError('get_10:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 1')
        if col <= self.cur:
            return 2
        return self._advance_not_end(col)

    def get_20(self, col):
        ''' prv  .   .  cur nxt
             .   1   1   2   . '''
        if col < self.cur - 2: raise AssertionError('get_20:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 2')
        if col < self.cur:
            return 1
        if col == self.cur:
            return 2
        return self._advance_not_end(col)

    def get_n0(self, col):
        ''' ...  .  cur nxt
             0   1   2   . '''
        if col < self.cur - 1:
            return 0
        if col < self.cur:
            return 1
        if col == self.cur:
            return 2
        return self._advance_not_end(col)

    def get_01(self, col):
        ''' prv cur  .  nxt
             .   2   2   . '''
        if col < self.cur: raise AssertionError('get_01:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur))
        if col <= self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def get_11(self, col):
        ''' prv  .  cur  .  nxt
             .   2   1   2   . '''
        if col < self.cur - 1: raise AssertionError('get_11:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 1')
        if col < self.cur:
            return 2
        if col == self.cur:
            return 1
        if col == self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def get_21(self, col):
        ''' prv  .   .  cur  .  nxt
             .   1   1   1   2   . '''
        if col < self.cur - 2: raise AssertionError('get_21:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 2')
        if col <= self.cur:
            return 1
        if col == self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def get_n1(self, col):
        ''' ...  .  cur  .  nxt
             0   1   1   2   . '''
        if col <= self.cur:
            return 1
        if col == self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def get_0n(self, col):
        ''' prv cur  .  ... nxt
             .   2   1   . '''
        if col < self.cur: raise AssertionError('get_0n:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' self=' + str(self))
        if col == self.cur:
            return 2
        if col == self.cur + 1:
            return 1
        return self._advance_not_end(col)

    def get_1n(self, col):
        ''' prv  .  cur  .  ... nxt
             .   2   1   1   . '''
        if col < self.cur - 1: raise AssertionError('get_1n:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 1')
        if col < self.cur:
            return 2
        if col <= self.cur + 1:
            return 1
        return self._advance_not_end(col)

    def get_2n(self, col):
        ''' prv  .   .  cur  .  ... nxt
             .   1   1   1   1   . '''
        if col < self.cur - 2: raise AssertionError('get_2n:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 2')
        if col <= self.cur + 1:
            return 1
        return self._advance_not_end(col)

    def get_nn(self, col):
        ''' ...  .  cur  .  ... nxt
             0   1   1   1   . '''
        if col < self.cur - 1:
            return 0
        if col <= self.cur + 1:
            return 1
        return self._advance_not_end(col)

    # x means there is no cur.nxt

    def get_0x(self, col):
        ''' prv cur  .  ...
             .   2   1   . '''
        if col < self.cur: raise AssertionError('get_0x:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur))
        if col == self.cur:
            return 2
        if col == self.cur + 1:
            return 1
        return self._advance_end(col)

    def get_1x(self, col):
        ''' prv  .  cur  .  ...
             .   2   1   1   . '''
        if col < self.cur - 1: raise AssertionError('get_1x:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 1')
        if col < self.cur:
            return 2
        if col <= self.cur + 1:
            return 1
        return self._advance_end(col)

    def get_2x(self, col):
        ''' prv  .   .  cur  .  ...
             .   1   1   1   1   . '''
        if col < self.cur - 2: raise AssertionError('get_2x:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 2')
        if col <= self.cur + 1:
            return 1
        return self._advance_end(col)

    def get_nx(self, col):
        ''' cur is the last column
            ...  .  cur  .  ...
             0   1   1   1   . '''
        if col < self.cur - 1:
            return 0
        if col <= self.cur + 1:
            return 1
        return self._advance_end(col)

    def get_end(self, col):
        ''' ...
             0 '''
        return 0

    def _advance_not_end(self, col):
        ''' Advance from the current get_*[01n] to the next get_* '''
        while col > self.cur:
            self.prv = self.cur
            self.cur = self.nxt
            try:
                self.nxt = next(self.nxt_iter)
            except StopIteration: # *x
                # self.nxt = None
                if self.prv + 1 == self.cur:
                    self.get_count = self.get_0x
                elif self.prv + 2 == self.cur:
                    self.get_count = self.get_1x
                elif self.prv + 3 == self.cur:
                    self.get_count = self.get_2x
                else:
                    self.get_count = self.get_nx
                break
        else:
            if self.cur == self.nxt - 1: # *0
                if self.prv + 1 == self.cur:
                    self.get_count = self.get_00
                elif self.prv + 2 == self.cur:
                    self.get_count = self.get_10
                elif self.prv + 3 == self.cur:
                    self.get_count = self.get_20
                else:
                    self.get_count = self.get_n0
            elif self.cur == self.nxt - 2: # *1
                if self.prv + 1 == self.cur:
                    self.get_count = self.get_01
                elif self.prv + 2 == self.cur:
                    self.get_count = self.get_11
                elif self.prv + 3 == self.cur:
                    self.get_count = self.get_21
                else:
                    self.get_count = self.get_n1
            else: # *n
                if self.prv + 1 == self.cur:
                    self.get_count = self.get_0n
                elif self.prv + 2 == self.cur:
                    self.get_count = self.get_1n
                elif self.prv + 3 == self.cur:
                    self.get_count = self.get_2n
                else:
                    self.get_count = self.get_nn
        return self.get_count(col)

    def _advance_end(self, col): # end
        ''' Advance from the current get_*x to get_end '''
        self.cur = None # None never == col
        self.on_empty()
        self.get_count = self.get_end
        return self.get_count(col)

    def is_live(self, col): return col == self.cur

    def _past_end(self): return self.get_count == self.get_end
    def amend_col_number(self, col_number):
        if self._past_end():
            return col_number
        if col_number is None:
            return self.cur - 1
        return min(self.cur - 1, col_number)
    def next_interesting_column(self, col): # ow/ None
        if col is None:
            if self.cur is None:
                return None
            else:
                return self.cur - 1
        if self.prv is not None:
            if col < self.prv - 1:
                return self.prv - 1
            if col < self.prv + 1:
                return col + 1
        if self.cur is not None:
            if col < self.cur - 1:
                return self.cur - 1
            if col < self.cur + 1:
                return col + 1
        if self.nxt is not None:
            if col < self.nxt - 1:
                return self.nxt - 1
            if col < self.nxt + 1:
                return col + 1
        return None # nothing is interesting

    def __str__(self):
        return ('col_gen('
                # + ' iter=' + str(self.nxt_iter)
                # + ' empty=' + str(self.on_empty)
                + ' prv=' + str(self.prv)
                + ' cur=' + str(self.cur)
                + ' nxt=' + str(self.nxt)
                + ' get=' + str(self.get_count)
                + ' col_list=' + str(self.col_list) # TODO: for debugging
                + ')')

if False: # col_gen tests
    def test_col_gen(cols, attempts):
        empty_list = [0]
        def on_empty(empty_list=empty_list):
            empty_list[0] += 1
            print('on_empty')
        print(str(cols) + ' ' + str(attempts))
        c = col_gen(cols, on_empty)
        print('c=' + str(c))
        for a in attempts:
            print('get_count(' + str(a) + ') = ' + str(c.get_count(a)) + ' c=' + str(c))
        print()
    test_col_gen([], [10, 20, 30])
    test_col_gen([10, 11, 12], [8, 9, 10, 11, 12, 13, 14])
    test_col_gen([10, 20, 30], [18, 19, 20, 21, 22, 23, 24])
    sys.exit(0)

class cw(object):
    ''' sparse coordinate collection: '''

    def __init__(self):
        self.rows = [] # [(row_number, [col_number ...])]

    def prt(self, scr):
        scr.clear()
        for row_number, cols in self.rows: # list((row_number, list(col_number)))
            if r_max <= row_number:
                break
            if 0 <= row_number:
                for col_number in cols:
                    if c_max <= col_number:
                        break
                    if 0 <= col_number:
                        scr.addstr(row_number, col_number, '*')

    def _next_col_number(self, col_number, cols_prv, cols_cur, cols_nxt):
        default_interesting_column = None if col_number is None else col_number + 1
        min_interesting_column = min((interesting_column for interesting_column in [
            cols_prv.next_interesting_column(col_number),
            cols_cur.next_interesting_column(col_number),
            cols_nxt.next_interesting_column(col_number)
            ] if interesting_column is not None),
            default=default_interesting_column)
        if col_number is None:
            return min_interesting_column
        else:
            return max(col_number + 1, min_interesting_column)

    def generation(self):
        row_prv = None # old row_number_new - 1 ow/ None
        row_cur = None # old row_number_new ow/ None
        row_nxt = None # old row_number_new + 1 ow/ None
        r = 0 # next self.rows[*} to pull in
        len_self_rows = len(self.rows)
        cw_new = cw()
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
            cols_prv = col_gen(row_prv[1] if row_prv else [], on_past_end)
            cols_cur = col_gen(row_cur[1] if row_cur else [], on_past_end)
            cols_nxt = col_gen(row_nxt[1] if row_nxt else [], on_past_end)

            cols_new = [] # the new cols_cur
            col_number = None
            # amended_col_number = cols_nxt.amend_col_number(cols_cur.amend_col_number(cols_prv.amend_col_number(None)))
            # col_number = amended_col_number if col_number is None else max(col_number + 1, amended_col_number)
            while past_end_list[0] < 3:
                col_number = self._next_col_number(col_number, cols_prv, cols_cur, cols_nxt)
                ## append new item to cols_new, if needed
                neighbor_count = cols_prv.get_count(col_number) + cols_cur.get_count(col_number) + cols_nxt.get_count(col_number)
                # print('col=' + str(col_number) + ' neighbor_count=' + str(neighbor_count))
                if cols_cur.is_live(col_number):
                    if neighbor_count - 1 in [2, 3]:
                        cols_new.append(col_number)
                else:
                    if neighbor_count == 3:
                        cols_new.append(col_number)
            if len(cols_new) > 0:
                cw_new.rows.append((row_number_new, cols_new))

        return cw_new

    def add(self, row, col):
        for r in range(len(self.rows)):
            row_r = self.rows[r]
            row_number = row_r[0]
            if row_number == row: # found the row
                cols = row_r[1]
                for c in range(len(cols)):
                    col_number = cols[c]
                    if col_number == col: # duplicate
                        return
                    if col_number > col: # new col not at end
                        cols[c : c] = [col]
                        return
                cols.append(col) # new col at end
                return
            if row_number > row: # new row not at end
                self.rows[r : r] = [(row, [col])]
                return
        self.rows.append((row, [col])) # new row at end

    def rem(self, row, col):
        for r in range(len(self.rows)):
            if self.rows[r][0] == row: # found the row
                if col in self.rows[r][1]:
                    self.rows[r][1].remove(col)
                    if len(self.rows[r][1]) == 0:
                        del self.rows[r] # last entry in row
                return
            if self.rows[r][0] > row: # not there, no such row
                return
        # not there, after last current row

    def clear(self): self.rows = []

    def __str__(self):
        return '[' + ' '.join('(' + str(row_number) + ', ' + '[' + ', '.join(str(c) for c in cols) + ']' + ')' for row_number, cols in self.rows) + ']'

# cw tests

if False:
    c = cw()
    def test_add(c, row, col):
        c.add(row, col)
        # print('test_add: ' + str(row) + ', ' + str(col) + ': ' + str(c))

    def glider(y, x):
        test_add(c, y + 0, x + 1)
        test_add(c, y + 1, x + 2)
        test_add(c, y + 2, x + 0)
        test_add(c, y + 2, x + 1)
        test_add(c, y + 2, x + 2)
    glider(0, 0)
    glider(0, 100)
    glider(100, 100)

    print('test_generation: before: ' + str(c))
    print('test_generation: new ' + str(c.generation()))
    sys.exit(0)

if False:
    c = cw()

    test_add(c, 5, 55)
    test_add(c, 5, 51)
    test_add(c, 5, 58)
    test_add(c, 8, 85)
    test_add(c, 8, 81)
    test_add(c, 8, 88)
    test_add(c, 3, 35)
    test_add(c, 3, 31)
    test_add(c, 3, 38)

    def test_rem(c, row, col):
        c.rem(row, col)
        # print('test_rem: ' + str(row) + ', ' + str(col) + ': ' + str(c))
    # print('c.rows=' + str(c))
    test_rem(c, 5, 55) # middle column
    test_rem(c, 8, 88) # last column
    test_rem(c, 3, 31) # first column
    test_rem(c, 5, 100) # after last column
    test_rem(c, 5, 52) # between columns
    test_rem(c, 5, 0) # before first column
    test_rem(c, 10, 12) # after last row
    test_rem(c, 6, 66) # between rows
    test_rem(c, 1, 1) # before first row

    test_rem(c, 5, 58) # middle row
    test_rem(c, 5, 51)

    test_rem(c, 8, 81) # last row
    test_rem(c, 8, 85)

    test_rem(c, 3, 38) # first row
    test_rem(c, 3, 35)
    sys.exit(0)

old_way = False

def scr_lim(n, limit):
    if old_way:
        return lim(n, limit)
    else:
        return n

def lim(n, limit):
    while n < 0: n += limit
    while n >= limit: n -= limit
    return n

def count_neighbors(board, r, c):
    return sum(1 if board[scr_lim(r + rr - 1, r_max)][scr_lim(c + cc - 1, c_max)] else 0
        for rr in range(3)
        for cc in range(3)
        if rr != 1 or cc != 1)

def generation(old_board, new_board):
    # live cell wth 2 or 3 neighbors continues
    # dead cell with exactly 3 neighbors is born
    for r in range(r_max):
        for c in range(c_max):
            count = count_neighbors(old_board, r, c)
            new_board[r][c] = count in [2, 3] if old_board[r][c] else count == 3

def make_board(): return [[False for c in range(c_max)] for r in range(r_max)]

if False:
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    ###

    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

def board_to_window(scr, b):
    for r in range(r_max):
        for c in range(c_max):
            scr.addstr(r, c, '*' if b[r][c] else ' ')

def add_cw_at(scr, board, conway, y, x, filename):
    with open(filename, 'r') as f:
        row = y
        while True:
            line = f.readline()
            if len(line) == 0:
                break
            col = x
            for ch in line:
                if ch == '*':
                    if old_way:
                        board[row][col] = True
                    else:
                        conway.add(row, col)
                    scr.addch(row, col, '*')
                col = scr_lim(col + 1, c_max)
            row = scr_lim(row + 1, r_max)
    scr.refresh()

def add_rle_at(scr, board, conway, y, x, filename):
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
                        if old_way:
                            board[row][col] = False
                        else:
                            conway.rem(row, col)
                        scr.addch(row, col, ' ')
                        col = scr_lim(col + 1, c_max)
                    number = 0
                elif c == 'o':
                    for _ in range(max(number, 1)):
                        if old_way:
                            board[row][col] = True
                        else:
                            conway.add(row, col)
                        scr.addch(row, col, '*')
                        col = scr_lim(col + 1, c_max)
                    number = 0
                elif c == '$':
                    for _ in range(max(number, 1)):
                        row = scr_lim(row + 1, r_max)
                    col = x
                    number = 0
                elif c == '!':
                    return
                # else some unknown character
            line = f.readline()
    scr.refresh()

def get_menu(scr):
    filenames = glob.glob('*.cw') + glob.glob('*.rle')
    height = len(filenames) + 2
    width = max((1 + len(filename) + 1 for filename in filenames), default=40)
    begin_y = curses.LINES // 16
    begin_x = curses.COLS // 16
    menu = curses.newpad(height, width)
    scr.leaveok(False)
    menu.border('|', '|', '-', '-', '+', '+', '+', '+')
    for i, filename in enumerate(filenames):
        menu.addstr(i + 1, 1, filename)
    number = 0
    escaped = False
    scr.move(begin_y + number + 1, begin_x + 1)
    menu.refresh(0,0, begin_y,begin_x, begin_y+height-1,begin_x+width-1)
    while True:
        c = scr.getch()
        if c < 0:
            continue
        if c == curses.KEY_UP:
            number = lim(number - 1, height - 2)
            scr.move(begin_y + number + 1, begin_x + 1)
        elif c == curses.KEY_DOWN:
            number = lim(number + 1, height - 2)
            scr.move(begin_y + number + 1, begin_x + 1)
        elif c == ord('\t'): # tab
            escaped = True
            break
        elif c == ord('\n'):
            break
        # menu.refresh(0,0, begin_y,begin_x, begin_y+height-1,begin_x+width-1)
    del menu
    return None if escaped else filenames[number]

def check_input(scr, board, conway):
    scr.refresh()
    c = scr.getch()
    if c >= 0 and chr(c) == ' ': # pause for editing
        row = curses.LINES // 2
        col = curses.COLS // 2
        scr.move(row, col)
        while True:
            c = scr.getch()
            if c < 0:
                continue
            elif c == curses.KEY_LEFT:
                col = scr_lim(col - 1, c_max)
                scr.move(row, col)
            elif c == curses.KEY_RIGHT:
                col = scr_lim(col + 1, c_max)
                scr.move(row, col)
            elif c == curses.KEY_UP:
                row = scr_lim(row - 1, r_max)
                scr.move(row, col)
            elif c == curses.KEY_DOWN:
                row = scr_lim(row + 1, r_max)
                scr.move(row, col)
            elif chr(c) == 'c':
                if old_way:
                    for r in range(r_max):
                        for c in range(c_max):
                            board[r][c] = False
                else:
                    conway.clear()
                scr.clear()
                scr.move(row, col)
            elif chr(c) == 'm':
                filename = get_menu(scr)
                if old_way:
                    board_to_window(scr, board)
                else:
                    conway.prt(scr)
                scr.refresh()
                if filename is None:
                    pass
                elif filename.endswith('.cw'):
                    add_cw_at(scr, board, conway, row, col, filename)
                elif filename.endswith('.rle'):
                    add_rle_at(scr, board, conway, row, col, filename)
            elif chr(c) == 'q':
                return True
            elif chr(c) == '.':
                if board[row][col] if old_way else conway.is_set(row, col):
                    scr.addch(row, col, ' ')
                    scr.move(row, col)
                    if old_way:
                        board[row][col] = False
                    else:
                        conway.rem(row, col)
                else:
                    scr.addch(row, col, '*')
                    scr.move(row, col)
                    if old_way:
                        board[row][col] = True
                    else:
                        conway.add(row, col)
            elif chr(c) == ' ':
                break
            # arrow keys to navigate
            # '.' key to toggle
            # ' ' key to continue
    return c >= 0 and chr(c) == 'q'

def main(stdscr):
    global r_max, c_max
    stdscr.clear()
    stdscr.nodelay(True)
    # stdscr.timeout(1)

    (r_max, c_max) = stdscr.getmaxyx()
    c_max -= 1 # not sure why it breaks without this

    if old_way:
        board_1 = make_board()
        # .*.
        # ..*
        # ***
        board_1[3][2] = True
        board_1[3][3] = True
        board_1[3][4] = True
        board_1[2][4] = True
        board_1[1][3] = True
        board_2 = make_board()

        while True:
            # stdscr.clear()
            board_to_window(stdscr, board_1)
            if check_input(stdscr, board_1, None): break
            generation(board_1, board_2)

            # stdscr.clear()
            board_to_window(stdscr, board_2)
            if check_input(stdscr, board_2, None): break
            generation(board_2, board_1)

    else:
        conway = cw()
        y = 0
        x = 0
        conway.add(y + 0, x + 1)
        conway.add(y + 1, x + 2)
        conway.add(y + 2, x + 0)
        conway.add(y + 2, x + 1)
        conway.add(y + 2, x + 2)

        while True:
            conway.prt(stdscr)
            if check_input(stdscr, None, conway): break
            conway = conway.generation()
            conway.prt(stdscr) # TODO: for debugging

curses.wrapper(main)
