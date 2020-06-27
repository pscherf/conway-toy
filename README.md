# conway-toy
A python curses script that loads/edits/runs Conway's game of life

Viewing commands:
space - toggle between pause and free run mode
digit - run for "digit" genrations then pause
H - pan left half a screen
L - pan right half a screen
K - pan up half a screen
J - pan down half a screen
h - pan left a tenth of a screen
l - pan right a tenth of a screen
k - pan up a tenth of a screen
j - pan down a tenth of a screen
O - reset the generation origin to the top left of the screen

Editing commands:
left arrow - move the cursor left on the screen
right arrow - move the cursor right on the screen
up arrow - move the cursor up on the screen
down arrow - move the cursor down on the screen
m - select a file to load at the cursor from the "menu"
. - toggle the cell under the cursor between alive and gone
c - clear, i.e. remove all individuals

q - quit

New menu items can be added by adding .rle or .cw files to the main directory.

Many of the .rle files contain a url for where they came from.
There are several web sites containing .rle files.
The .rle file is a file format convention used by several web sites.

The .cw format is just a hack layout for stuff to load.
A '*' means a live cell and '.' means not a live cell.
Each line is loaded in its own row.
