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
        self.col_list = col_list # TODO: for debugging
        self.nxt_iter = col_list.__iter__()
        self.on_empty = on_empty
        #
        self.prv = None
        if len(col_list) == 0:
            self.cur = None # None never == col
            self.nxt = None
            self.on_empty()
            self.get_count = self.get_end
            return
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
        if self.prv is None or self.cur is None or self.nxt is None or self.prv + 1 != self.cur or self.cur != self.nxt - 1: raise AssertionError('get_00:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur: raise AssertionError('get_00:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' self=' + str(self))
        if col <= self.cur:
            return 3
        return self._advance_not_end(col)

    def get_10(self, col):
        ''' prv  .  cur nxt
             .   2   2   . '''
        if self.prv is None or self.cur is None or self.nxt is None or self.prv + 2 != self.cur or self.cur != self.nxt - 1: raise AssertionError('get_10:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur - 1: raise AssertionError('get_10:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 1' + ' self=' + str(self))
        if col <= self.cur:
            return 2
        return self._advance_not_end(col)

    def get_20(self, col):
        ''' prv  .   .  cur nxt
             .   1   1   2   . '''
        if self.prv is None or self.cur is None or self.nxt is None or self.prv + 3 != self.cur or self.cur != self.nxt - 1: raise AssertionError('get_20:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur - 2: raise AssertionError('get_20:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 2' + ' self=' + str(self))
        if col < self.cur:
            return 1
        if col == self.cur:
            return 2
        return self._advance_not_end(col)

    def get_n0(self, col):
        ''' ...  .  cur nxt
             0   1   2   . '''
        if self.cur is None or self.nxt is None or (self.prv is not None and self.prv + 3 >= self.cur) or self.cur != self.nxt - 1: raise AssertionError('get_n0:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if self.prv is not None and col <= self.prv + 1: raise AssertionError('get_n0:' + ' col=' + str(col) + ' <= self.cur=' + str(self.prv) + ' + 1' + ' self=' + str(self))
        if col < self.cur - 1:
            return 0
        if col < self.cur:
            return 1
        if col <= self.cur:
            return 2
        return self._advance_not_end(col)

    def get_01(self, col):
        ''' prv cur  .  nxt
             .   2   2   . '''
        if self.prv is None or self.cur is None or self.nxt is None or self.prv + 1 != self.cur or self.cur != self.nxt - 2: raise AssertionError('get_01:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur: raise AssertionError('get_01:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' self=' + str(self))
        if col <= self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def get_11(self, col):
        ''' prv  .  cur  .  nxt
             .   2   1   2   . '''
        if self.prv is None or self.cur is None or self.nxt is None or self.prv + 2 != self.cur or self.cur != self.nxt - 2: raise AssertionError('get_11:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur - 1: raise AssertionError('get_11:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 1' + ' self=' + str(self))
        if col < self.cur:
            return 2
        if col <= self.cur:
            return 1
        if col <= self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def get_21(self, col):
        ''' prv  .   .  cur  .  nxt
             .   1   1   1   2   . '''
        if self.prv is None or self.cur is None or self.nxt is None or self.prv + 3 != self.cur or self.cur != self.nxt - 2: raise AssertionError('get_21:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur - 2: raise AssertionError('get_21:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 2' + ' self=' + str(self))
        if col <= self.cur:
            return 1
        if col <= self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def get_n1(self, col):
        ''' ...  .  cur  .  nxt
             0   1   1   2   . '''
        if self.cur is None or self.nxt is None or (self.prv is not None and self.prv + 3 > self.cur) or self.cur != self.nxt - 2: raise AssertionError('get_n1:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if self.prv is not None and col <= self.prv + 1: raise AssertionError('get_n1:' + ' col=' + str(col) + ' <= self.prv=' + str(self.prv) + ' + 1' + ' self=' + str(self))
        if col < self.cur - 1:
            return 0
        if col <= self.cur:
            return 1
        if col <= self.cur + 1:
            return 2
        return self._advance_not_end(col)

    def get_0n(self, col):
        ''' prv cur  .  ... nxt
             .   2   1   .   . '''
        if self.prv is None or self.cur is None or self.nxt is None or self.prv + 1 != self.cur or self.cur >= self.nxt - 2: raise AssertionError('get_0n:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur: raise AssertionError('get_0n:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' self=' + str(self) + ' self=' + str(self))
        if col <= self.cur:
            return 2
        if col <= self.cur + 1:
            return 1
        return self._advance_not_end(col)

    def get_1n(self, col):
        ''' prv  .  cur  .  ... nxt
             .   2   1   1   .   . '''
        if self.prv is None or self.cur is None or self.nxt is None or self.prv + 2 != self.cur or self.cur >= self.nxt - 2: raise AssertionError('get_21:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur - 1: raise AssertionError('get_1n:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 1' + ' self=' + str(self))
        if col < self.cur:
            return 2
        if col <= self.cur + 1:
            return 1
        return self._advance_not_end(col)

    def get_2n(self, col):
        ''' prv  .   .  cur  .  ... nxt
             .   1   1   1   1   .   .'''
        if self.prv is None or self.cur is None or self.nxt is None or self.prv + 3 != self.cur or self.cur >= self.nxt - 2: raise AssertionError('get_21:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur - 2: raise AssertionError('get_2n:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 2' + ' self=' + str(self))
        if col <= self.cur + 1:
            return 1
        return self._advance_not_end(col)

    def get_nn(self, col):
        ''' ...  .  cur  .  ... nxt
             0   1   1   1   .   . '''
        if self.cur is None or self.nxt is None or (self.prv is not None and self.prv + 3 >= self.cur) or self.cur > self.nxt - 2: raise AssertionError('get_21:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if self.prv is not None and col <= self.prv + 1: raise AssertionError('get_nn:' + ' col=' + str(col) + ' <= self.prv=' + str(self.prv) + ' + 1' + ' self=' + str(self))
        if col < self.cur - 1:
            return 0
        if col <= self.cur + 1:
            return 1
        return self._advance_not_end(col)

    def get_0x(self, col):
        ''' prv cur  .  ...
             .   2   1   . '''
        if self.prv is None or self.cur is None or self.nxt is not None or self.prv + 1 != self.cur: raise AssertionError('get_0x:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur: raise AssertionError('get_0x:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' self=' + str(self))
        if col <= self.cur:
            return 2
        if col <= self.cur + 1:
            return 1
        return self._advance_from_end(col)

    def get_1x(self, col):
        ''' prv  .  cur  .  ...
             .   2   1   1   . '''
        if self.prv is None or self.cur is None or self.nxt is not None or self.prv + 2 != self.cur: raise AssertionError('get_1x:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur - 1: raise AssertionError('get_1x:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 1' + ' self=' + str(self))
        if col < self.cur:
            return 2
        if col <= self.cur + 1:
            return 1
        return self._advance_from_end(col)

    def get_2x(self, col):
        ''' prv  .   .  cur  .  ...
             .   1   1   1   1   . '''
        if self.prv is None or self.cur is None or self.nxt is not None or self.prv + 3 != self.cur: raise AssertionError('get_2x:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if col < self.cur - 2: raise AssertionError('get_2x:' + ' col=' + str(col) + ' < self.cur=' + str(self.cur) + ' - 2' + ' self=' + str(self))
        if col <= self.cur + 1:
            return 1
        return self._advance_from_end(col)

    def get_nx(self, col):
        ''' ...  .  cur  .  ...
             0   1   1   1   . '''
        if self.cur is None or self.nxt is not None or (self.prv is not None and self.prv + 3 > self.cur): raise AssertionError('get_nx:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if self.prv is not None and col <= self.prv + 1: raise AssertionError('get_nx:' + ' col=' + str(col) + ' <= self.prv=' + str(self.prv) + ' + 1' + ' self=' + str(self))
        if col < self.cur - 1:
            return 0
        if col <= self.cur + 1:
            return 1
        return self._advance_from_end(col)

    def get_end(self, col):
        ''' ...
             0 '''
        if self.cur is not None or self.nxt is not None: raise AssertionError('get_end:' + ' prv=' + str(self.prv) + ' cur=' + str(self.cur) + ' nxt=' + str(self.nxt) + ' self=' + str(self))
        if self.prv is not None and col <= self.prv + 1: raise AssertionError('get_nx:' + ' col=' + str(col) + ' <= self.prv=' + str(self.prv) + ' + 1' + ' self=' + str(self))
        return 0

    def _advance_not_end(self, col):
        ''' Advance from the current get_*[01n] to the next get_* '''
        if col <= self.cur: raise AssertionError('_advance_not_end:' + ' col=' + str(col) + ' <= self.cur=' + str(self.cur) + ' self=' + str(self))
        while col > self.cur:
            self.prv = self.cur
            self.cur = self.nxt
            try:
                self.nxt = next(self.nxt_iter)
            except StopIteration: # *x
                self.nxt = None
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

    def _advance_from_end(self, col): # end
        ''' Advance from the current get_*x to get_end '''
        self.prv = self.cur
        self.cur = self.nxt # None, never == col
        self.on_empty()
        self.get_count = self.get_end
        return self.get_count(col) # parameter ignored

    def is_live(self, col): return col == self.cur or col == self.prv or col == self.nxt

    def first_interesting_column(self): # ow/ None
        if self.prv is not None: # should not happen
            raise AssertionError('first_intersting_column:' + ' self.prv=' + str(self.prv) + ' is not None' + ' self=' + str(self))
            return self.prv - 1
        if self.cur is not None: # only false on empty row
            return self.cur - 1
        if len(self.col_list) != 0: raise AssertionError('first_interesting_column:' + ' self.cur is None but len(self.col_list) != 0 ' + str(self))
        if self.nxt is not None: # should not happen (return self.cur - 1 should have occured first)
            raise AssertionError('first_intersting_column:' + ' self.nxt=' + str(self.nxt) + ' is not None' + ' self=' + str(self))
            return self.nxt - 1
        return None # nothing is interesting
    def next_interesting_column(self, col): # ow/ None
        if self.prv is not None and self.cur is not None and (self.prv >= col or col > self.cur + 1): raise AssertionError('next_interesting_column:' + ' prv=' + str(self.prv) + ' >= col=' + str(col) + ' or col > cur=' + str(self.cur) + ' + 1' + ' self=' + str(self))
        if self.nxt is not None and col >= self.nxt: raise AssertionError('next_interesting_column:' + ' col=' + str(col) + ' >= nxt=' + str(self.nxt) + ' self=' + str(self))
        # assert: self.prv < col <= self.cur + 1, unless self.prv or self.cur are None
        if self.prv is not None: # prv - 1, prv, prv + 1
            if col < self.prv - 1: # should not happen
                raise AssertionError('next_interesting_column:' + ' col=' + str(col) + ' < self.prv=' + str(self.prv) + ' - 1' + ' self=' + str(self))
                return self.prv - 1
            if col < self.prv + 1: # should not happen
                raise AssertionError('next_interesting_column:' + ' col=' + str(col) + ' < self.prv=' + str(self.prv) + ' + 1' + ' self=' + str(self))
                return col + 1
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
            raise AssertionError('next_interesting_column:' + ' col=' + str(col) + ' >= self.nxt=' + str(self.nxt) + ' + 1' + ' self=' + str(self))
        return None # nothing is interesting

    def __str__(self):
        return ('column_scanner('
                # + ' iter=' + str(self.nxt_iter)
                # + ' empty=' + str(self.on_empty)
                + ' prv=' + str(self.prv)
                + ' cur=' + str(self.cur)
                + ' nxt=' + str(self.nxt)
                + ' col_list=' + str(self.col_list) # TODO: for debugging
                + ' get=' + str(self.get_count)
                + ')')

if False: # column_scanner tests
    def test_col_gen(cols, attempts):
        empty_list = [0]
        def on_empty(empty_list=empty_list):
            empty_list[0] += 1
            print('on_empty')
        print(str(cols) + ' ' + str(attempts))
        c = column_scanner(cols, on_empty)
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
        for row_number, cols in self.rows: # [(row_number, [col_number ...]) ...]
            if r_max <= row_number: # more stuff below the bottom of the screen
                break
            if 0 <= row_number: # else stuff above the top of the screen
                for col_number in cols:
                    if c_max <= col_number: # stuff to the right of the screen
                        break
                    if 0 <= col_number: # else stuff to the left of the screen
                        scr.addstr(row_number, col_number, '*')

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
        cw_new = cw()
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
                cw_new.rows.append((row_number_new, cols_new))

        return cw_new

    def toggle(self, row, col):
        for r in range(len(self.rows)):
            row_r = self.rows[r]
            row_number = row_r[0]
            if row_number == row: # found the row
                cols = row_r[1]
                for c in range(len(cols)):
                    col_number = cols[c]
                    if col_number == col: # existing col not at end
                        cols.remove(col)
                        if len(cols) == 0: # last entry in row
                            del self.rows[r]
                        return
                    elif col_number > col: # new col not at end
                        cols.insert(c, col)
                        return
                cols.append(col) # new col at end
                return
            elif row_number > row: # new row not at end
                self.rows.insert(r, (row, [col]))
                return
        self.rows.append((row, [col])) # new row at end

    def is_set(self, row, col):
        for r in range(len(self.rows)):
            row_r = self.rows[r]
            row_number = row_r[0]
            if row_number == row: # found the row
                cols = row_r[1]
                for c in range(len(cols)):
                    col_number = cols[c]
                    if col_number == col: # found it
                        return True
                    if col_number > col: # no such column
                        return False
                return False # to the right of everything
            elif row_number > row: # no such row
                return False
        return False # below everything

    def set(self, row, col):
        for r in range(len(self.rows)):
            row_r = self.rows[r]
            row_number = row_r[0]
            if row_number == row: # found the row
                cols = row_r[1]
                for c in range(len(cols)):
                    col_number = cols[c]
                    if col_number == col: # duplicate
                        return
                    elif col_number > col: # new col not at end
                        cols.insert(c, col)
                        return
                cols.append(col) # new col at end
                return
            elif row_number > row: # new row not at end
                self.rows.insert(r, (row, [col]))
                return
        self.rows.append((row, [col])) # new row at end

    def clr(self, row, col):
        for r in range(len(self.rows)):
            row_r = self.rows[r]
            row_number = row_r[0]
            if row_number == row: # found the row
                cols = row_r[1]
                if col in cols:
                    cols.remove(col)
                    if len(cols) == 0:
                        del row_r # last entry in row
                return
            if row_number > row: # not there, no such row
                return
        # not there, after last current row

    def clear(self): self.rows = []

    def __str__(self):
        return '[' + ' '.join('(' + str(row_number) + ', ' + '[' + ', '.join(str(c) for c in cols) + ']' + ')' for row_number, cols in self.rows) + ']'

# cw tests

if False:
    c = cw()
    def test_add(c, row, col):
        c.set(row, col)
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
        c.clr(row, col)
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

def scr_lim(n, limit): return n

def lim(n, limit):
    while n < 0: n += limit
    while n >= limit: n -= limit
    return n

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
                col = scr_lim(col + 1, c_max)
            row = scr_lim(row + 1, r_max)

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
                        col = scr_lim(col + 1, c_max)
                    number = 0
                elif c == 'o':
                    for _ in range(max(number, 1)):
                        conway.set(row, col)
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

def has_bit(n, r, c):
    return n >> (3 * r + c) & 1 != 0

def mk_cell_test(stdscr, conway, n):
    conway.clear()
    r_org = r_max // 2
    c_org = c_max // 2
    for r in range(3):
        for c in range(3):
            if has_bit(n, r, c):
                conway.set(r_org + r, c_org + c)
    conway.prt(stdscr)
    stdscr.addstr(0, 0, 'test ' + str(n))

def get_s(conway, r_org, c_org):
    return ' '.join(''.join('*' if conway.is_set(r_org + r, c_org + c) else '.' for c in range(3)) for r in range(3))
def get_t(n):
    return ' '.join(''.join('*' if has_bit(n, r, c) else '.' for c in range(3)) for r in range(3))

def mk_big_test(stdscr):
    max_failures = 130
    failures = 0
    first_failure = None
    for n in range(512):
        conway = cw()
        r_org = r_max // 2
        c_org = c_max // 2

        before_live = False
        count = 0
        for r in range(3):
            for c in range(3):
                if has_bit(n, r, c):
                    if r == 1 and c == 1:
                        before_live = True
                    else:
                        count += 1
                    conway.set(r_org + r, c_org + c)
        before_s = get_s(conway, r_org, c_org)
        before_t = get_t(n)
        if before_s != before_t:
            if failures < max_failures:
                stdscr.addstr(failures + 1, 0, 'test' + ' ' + before_s + ' -> ' + before_t + ' ' + str(n) + ' before not set up right')
            failures += 1


        new_conway = conway.generation()
        if before_live:
            expected_live = count in [2, 3]
        else:
            expected_live = count == 3
        got_live = new_conway.is_set(r_org + 1, c_org + 1)

        if expected_live != got_live:
            if first_failure is None: first_failure = n
            if failures < max_failures:
                after_s = get_s(new_conway, r_org, c_org)
                stdscr.addstr(failures + 1, 0, 'test' + ' ' + before_s + ' -> ' + after_s + ' ' + str(n) + ' expected_live=' + str(expected_live) + ', got ' + str(got_live))
            failures += 1

    stdscr.addstr(0, 0, str(failures) + ' total failures')
    return first_failure

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

test_number = 0

def column_scanner_test(stdscr):
    global test_number

    left_col = 10
    status_row = 10 # row 0: status message

    calc_row = 12 # row 2: calculated neighbor count
    cs_row = 13 # row 3: column_scanner neighbor count
    scan_row = 14 # row 1: row to scan
    get_count_row = 15 # row 4: get_count key
    other_get_count_row = 16 # row 5: get_count key

    stdscr.clear()
    # status_row
    stdscr.addstr(status_row, left_col, 'column_scanner_test ' + str(test_number))

    if test_number == 0:
        col_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    elif test_number == 1:
        col_list = [0, 1, 2, 4, 5, 6, 7, 8, 9, 10]
    elif test_number == 2:
        col_list = [0, 1, 2, 4, 5, 10, 12, 14, 20, 30, 33, 34, 37, 39, 42, 50, 51 ]
        # get_n0
        # get_00
        # get_01
        # get_10
        # get_0n
        # get_n1
        # get_11
        # get_1n
        # get_nn
        # get_20
        # get_21
        # get_2n
        # get_end
    elif test_number == 3:
        col_list = [0, 1]
        # get_0x
    elif test_number == 4:
        col_list = [0, 2]
        # get_1x
    elif test_number == 5:
        col_list = [0, 3]
        # get_2x
    else:
        col_list = [0, 4]
        # get_nx
        test_number = -1

    test_number += 1

    # scan_row
    on_empty_counter = [0]
    def on_empty(): on_empty_counter[0] += 1
    cs = column_scanner(col_list, on_empty)
    for c in col_list:
        stdscr.addch(scan_row, left_col + c, '*')
    # calc_row and cs_row
    def set_get_count_row(col):
        def set_one(top, bot):
            stdscr.addch(get_count_row, left_col + col, top)
            stdscr.addch(other_get_count_row, left_col + col, bot)
        if cs.get_count == cs.get_00: set_one('0', '0')
        elif cs.get_count == cs.get_10: set_one('1', '0')
        elif cs.get_count == cs.get_20: set_one('2', '0')
        elif cs.get_count == cs.get_n0: set_one('n', '0')
        elif cs.get_count == cs.get_01: set_one('0', '1')
        elif cs.get_count == cs.get_11: set_one('1', '1')
        elif cs.get_count == cs.get_21: set_one('2', '1')
        elif cs.get_count == cs.get_n1: set_one('n', '1')
        elif cs.get_count == cs.get_0n: set_one('0', 'n')
        elif cs.get_count == cs.get_1n: set_one('1', 'n')
        elif cs.get_count == cs.get_2n: set_one('2', 'n')
        elif cs.get_count == cs.get_nn: set_one('n', 'n')
        elif cs.get_count == cs.get_0x: set_one('0', 'x')
        elif cs.get_count == cs.get_1x: set_one('1', 'x')
        elif cs.get_count == cs.get_2x: set_one('2', 'x')
        elif cs.get_count == cs.get_nx: set_one('n', 'x')
        elif cs.get_count == cs.get_end: set_one('e', 'n')
        else: set_one('?', '?')
    prv = 0
    cur = 0
    nxt = 0
    cc = 0
    len_col_list = len(col_list)
    col_cnt = (col_list[-1] if len_col_list > 0 else 0) + 5
    for col in range(-3, col_cnt):
        # calc_row
        prv = cur
        cur = nxt
        if cc < len_col_list and col + 1 == col_list[cc]:
            nxt = 1
            cc += 1
        else:
            nxt = 0
        stdscr.addch(calc_row, left_col + col, str(prv + cur + nxt))
        # cs_row
        stdscr.addch(cs_row, left_col + col, str(cs.get_count(col)))
        # get_count_row
        set_get_count_row(col)

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

    test_number = 23 # TODO: for debugging

    while True:
        if fuse != 0:
            if fuse > 0: fuse -= 1
            conway = conway.generation()
            conway.prt(stdscr)
            if fuse == 0:
                row = r_max // 2
                col = c_max // 2
        stdscr.refresh()
        stdscr.move(row, col)
        c = stdscr.getch()
        if c < 0:
            continue
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
        elif c == curses.KEY_LEFT: col = scr_lim(col - 1, c_max)
        elif c == curses.KEY_RIGHT: col = scr_lim(col + 1, c_max)
        elif c == curses.KEY_UP: row = scr_lim(row - 1, r_max)
        elif c == curses.KEY_DOWN: row = scr_lim(row + 1, r_max)
        elif c == ord('c'):
            conway.clear()
            conway.prt(stdscr)
        elif c == ord('m'):
            filename = get_menu(stdscr)
            if filename is not None:
                if filename.endswith('.cw'):
                    add_cw_at(conway, row, col, filename)
                elif filename.endswith('.rle'):
                    add_rle_at(conway, row, col, filename)
                # else we don't understand filename
                conway.prt(stdscr)
        elif c == ord('p'):
            fuse = 0 # make sure we are paused
            row = 0
            col = 0
            conway = parallel(stdscr, conway)
        elif c == ord('s'):
            screen_test(stdscr)
        elif c == ord('t'):
            mk_cell_test(stdscr, conway, test_number)
            test_number += 1
        elif c == ord('T'):
            test_number = mk_big_test(stdscr)
            if test_number is None: test_number = 0
        elif c == ord('q'):
            return
        elif c == ord('x'):
            column_scanner_test(stdscr)
        elif c == ord('.'):
            conway.toggle(row, col)
            conway.prt(stdscr)

curses.wrapper(main)
