#! /usr/bin/python3

import curses

def lim(n, limit):
    if n < 0: return n + limit
    if n >= limit: return n - limit
    return n

def count_neighbors(board, r, c):
    return sum(1 if board[lim(r + rr - 1, r_max)][lim(c + cc - 1, c_max)] else 0
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

def check_input(scr, board):
    scr.refresh()
    c = scr.getch()
    if c >= 0 and chr(c) == ' ': # pause for editing
        row = 0
        col = 0
        scr.move(row, col)
        while True:
            c = scr.getch()
            if c < 0:
                continue
            elif c == curses.KEY_LEFT:
                col = lim(col - 1, c_max)
                scr.move(row, col)
            elif c == curses.KEY_RIGHT:
                col = lim(col + 1, c_max)
                scr.move(row, col)
            elif c == curses.KEY_UP:
                row = lim(row - 1, r_max)
                scr.move(row, col)
            elif c == curses.KEY_DOWN:
                row = lim(row + 1, r_max)
                scr.move(row, col)
            # elif chr(c) == 'g': glider
            # elif chr(c) == 'x': ...
            # ...
            elif chr(c) == '.':
                if board[row][col]:
                    scr.addch(row, col, ' ')
                    scr.move(row, col)
                    board[row][col] = False
                else:
                    scr.addch(row, col, '*')
                    scr.move(row, col)
                    board[row][col] = True
            elif chr(c) == ' ':
                break
            # arrow keys to navigate
            # '.' key to toggle
            # ' ' key to continue
        pass
    return c >= 0 and chr(c) == 'q'

def main(stdscr):
    global r_max, c_max
    stdscr.clear()
    stdscr.nodelay(True)
    # stdscr.timeout(1)

    (r_max, c_max) = stdscr.getmaxyx()
    c_max -= 1 # not sure why it breaks without this

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
        if check_input(stdscr, board_1): break
        generation(board_1, board_2)

        # stdscr.clear()
        board_to_window(stdscr, board_2)
        if check_input(stdscr, board_2): break
        generation(board_2, board_1)

curses.wrapper(main)

class cw(object):
    # [(row_number, [col_number ...])]

    def __init__(self):
        self.rows = []

    def prt(scr, self):
        # sparse coordinate collection:
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

    def generation(self):
        rows = [None, None, None]
        row = 0
        rows_len = len(self.rows)
        cw_new = cw()
        while True:
            # calculate row_number, advance rows, row
            if rows[1] is not None: # advance to rows[1][0] + 1
                row_number = rows[1][0] + 1
                rows[0] = rows[1]
                rows[1] = rows[2]
                if row < rows_len and self.rows[row][0] == row_number + 1:
                    rows[2] = self.rows[row]
                    row += 1
                else:
                    rows[2] = None
            elif rows[2] is not None: # rows[1] is None, advance to rows[2][0]
                row_number = rows[2][0]
                rows[0] = None
                rows[1] = rows[2]
                if row < rows_len and self.rows[row][0] == row_number + 1:
                    rows[2] = self.rows[row]
                    row += 1
                else:
                    rows[2] = None
            elif row < rows_len: # rows[1] is None and rows[2] is None, advance to self.rows[row] - 1
                row_number = self.rows[row] - 1
                rows[0] = None
                rows[1] = None
                rows[2] = self.rows[row]
                row += 1
            else: # rows[1] is None and rows[2] is None and row == rows_len, stop
                break

            # produce new row (a new rows[1])

            cols_prv = [] if rows[0] else rows[0][1]
            col_prv = 0
            cols_prv_len = len(cols_prv)

            cols_cur = [] if rows[1] else rows[1][1]
            col_cur = 0
            cols_cur_len = len(cols_cur)

            cols_nxt = [] if rows[2] else rows[2][1]
            col_nxt = 0
            cols_nxt_len = len(cols_nxt)

            cols_new = [] # a new cols_cur
            ## set col_number
            if col_prv < cols_prv_len:
                col_number = cols_prv[col_prv] - 1
                if col_cur < cols_cur_len and cols_cur[col_cur] - 1 < col_number:
                    col_number = cols_cur[col_cur] - 1
                if col_nxt < cols_nxt_len and cols_nxt[col_nxt] - 1 < col_number:
                    col_number = cols_nxt[col_nxt] - 1
            elif col_cur < cols_cur_len:
                col_number = cols_cur[col_cur] - 1
                if col_nxt < cols_nxt_len and cols_nxt[col_nxt] - 1 < col_number:
                    col_number = cols_nxt[col_nxt] - 1
            elif col_nxt < cols_nxt_len:
                col_number = cols_nxt[col_cur] - 1
            else:
                break

            while True:
                ## append new item to cols_new, if needed
                neighbor_count = (self.add_col(cols_prv, col_prv, col_prv_len, col_number)
                    + self.add_col(cols_cur, col_cur, col_cur_len, col_number)
                    + self.add_col(cols_nxt, col_nxt, col_nxt_len, col_number))
                if self.col_live(cols_cur, col_cur, col_cur_len, col_number):
                    if neighbor_count - 1 in [2, 3]:
                        cols_new.append(col_number)
                else:
                    if neighbor_count == 3:
                        cols_new.append(col_number)
                ## advance to next col_number or break
                # skip past cols_*[col_*] <= col_number - 1
                if col_prv < col_prv_len and cols_prv[col_prv] <= col_number - 1: col_prv += 1
                if col_cur < col_cur_len and cols_cur[col_cur] <= col_number - 1: col_cur += 1
                if col_nxt < col_nxt_len and cols_nxt[col_nxt] <= col_number - 1: col_nxt += 1
                col_number += 1
                # calculate col_number_min = min(cols_*[col_*] - 1)
                if col_prv < col_prv_len:
                    col_number_min = cols_prv[col_prv] - 1
                    if col_cur < col_cur_len and col_number_min > cols_cur[col_cur] - 1:
                        col_number_min = cols_cur[col_cur] - 1
                    if col_nxt < col_nxt_len and col_number_min > cols_nxt[col_nxt] - 1:
                        col_number_min = cols_nxt[col_nxt] - 1
                elif col_cur < col_cur_len:
                    col_number_min = cols_cur[col_cur] - 1
                    if col_nxt < col_nxt_len and col_number_min > cols_nxt[col_nxt] - 1:
                        col_number_min = cols_nxt[col_nxt] - 1
                elif col_nxt < col_nxt_len:
                    col_number_min = cols_nxt[col_nxt] - 1
                else:
                    break # stop if we are done
                # adjust col_number if neccessary
                if col_number < col_number_min:
                    col_number = col_number_min
                ## skip past cols_*[col_*] that are less than col_number - 1
                while col_prv < col_prv_len and cols_prv[col_prv] < col_number - 1: col_prv += 1
                while col_cur < col_cur_len and cols_cur[col_cur] < col_number - 1: col_cur += 1
                while col_nxt < col_nxt_len and cols_nxt[col_nxt] < col_number - 1: col_nxt += 1
                ## stop if we fell off the end
                if col_prv >= col_prv_len and col_cur >= col_cur_len and col_nxt >= col_nxt_len:
                    break # I don't think we get here
            cw_new.rows.append((row_number, cols_new))

        return cw_new

    def col_live(self, cols_cur, col_cur, col_cur_len, col_number):
        for c in [0, 1, 2]:
            if col_cur_len <= col_cur + c:
                return False
            col_num = cols_cur[col_cur + c]
            if col_num == col_number:
                return True
            if col_num < col_number:
                return False
        return False

    def add_col(self, cols, col, col_len, col_number):
        for c in [0, 1, 2]:
            if col_len <= col + c or 1 < abs(cols[col + c] - col_number):
                return c
        return 3

    def add(self, row, col):
        for r in range(len(self.rows)):
            if self.rows[r][0] == row: # found the row
                for c in range(len(self.rows[r][1])):
                    if self.rows[r][1][c] == col: # duplicate
                        return
                    if self.rows[r][1][c] < col: # new col not at end
                        self.rows[r][1][c : c] = col
                        return
                self.rows[r][1][-1] = [col] # new col at end
                return
            if self.rows[r][0] < row: # new row not at end
                self.rows[r : r] = [col]
                return
        self.rows[-1] = (row, [col]) # new row at end

    def rem(self, row, col):
        for r in range(len(self.rows)):
            if self.rows[r][0] == row: # found the row
                if col in self.rows[r][1]:
                    self.rows[r][1].remove[col]
                    if len(self.rows[r][1]) == 0:
                        del self.rows[r] # last entry in row
                    return # removed it
                return # not there
            if self.rows[r][0] < row: # not there, no such row
                return
        # not there, after last current row
