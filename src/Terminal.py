"""Primitive terminal emulator example made from a PyQt QTextEdit widget.
https://gist.github.com/ssokolow/6f93e68d2af774aebf18667a7760cd23
"""

import fcntl, locale, os, pty, struct, sys, termios
import subprocess  # nosec

from icecream import ic
# Quick hack to limit the scope of the PyLint warning disabler
try:
    # pylint: disable=no-name-in-module
    from PyQt5.QtCore import Qt, QSocketNotifier                 # type: ignore
    from PyQt5.QtGui import QFont, QPalette, QTextCursor         # type: ignore
    from PyQt5.QtWidgets import QApplication, QStyle, QTextEdit  # type: ignore
except ImportError:
    raise

# It's good practice to put these sorts of things in constants at the top
# rather than embedding them in your code
DEFAULT_TTY_CMD = ['/bin/bash']
DEFAULT_COLS = 80
DEFAULT_ROWS = 25

# NOTE: You can use any QColor instance, not just the predefined ones.
DEFAULT_TTY_FONT = QFont('Noto', 16)
DEFAULT_TTY_FG = Qt.lightGray
DEFAULT_TTY_BG = Qt.black

# The character to use as a reference point when converting between pixel and
# character cell dimensions in the presence of a non-fixed-width font
REFERENCE_CHAR = 'W'


class Terminal(QTextEdit):
    """
        Modified starting by 
        https://gist.github.com/ssokolow/6f93e68d2af774aebf18667a7760cd23
    """

    # Used to block the user from backspacing more characters than they
    # typed since last pressing Enter
    backspace_budget = 0

    def __init__(self, *args, **kwargs):
        super(Terminal, self).__init__(*args, *kwargs)

        # Customize the look and feel
        pal = self.palette()
        pal.setColor(QPalette.Base, DEFAULT_TTY_BG)
        pal.setColor(QPalette.Text, DEFAULT_TTY_FG)
        self.setPalette(pal)
        self.setFont(DEFAULT_TTY_FONT)

        # Disable the widget's built-in editing support rather than looking
        # into how to constrain it. (Quick hack which means we have to provide
        # our own visible cursor if we want one)
        self.setReadOnly(True)
        self.user_input = ''
        self.PROMPT = '> '
        #
        self.history_size = 32
        self.history = [None]*self.history_size
        self.history_index = None
        self.history_cursor = None 
        self.show_prompt()

    def write(self, text):
        # Insert the output at the end and scroll to the bottom
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)
        scroller = self.verticalScrollBar()
        scroller.setValue(scroller.maximum())


    def resizeApp(self, app):
        fontMetrics = self.fontMetrics()
        target_width = (fontMetrics.boundingRect(
            REFERENCE_CHAR * DEFAULT_COLS
        ).width() + app.style().pixelMetric(QStyle.PM_ScrollBarExtent))
        self.resize(target_width, fontMetrics.height() * DEFAULT_ROWS)

    def keyPressEvent(self, event):
        """Handler for all key presses delivered while the widget has focus"""
        char = event.text()
        #ic(str(event.key))
        #ic(str(char))



        # Move the cursor to the end
        self.moveCursor(QTextCursor.End)
        cursor = self.textCursor()

        key_pressed = event.key()
        if key_pressed == Qt.Key_Up:
            self.show_prev_command()
        elif key_pressed == Qt.Key_Down:
            self.show_next_command()
        # If the character isn't a control code of some sort,
        # then echo it to the terminal screen.
        #
        # (The length check is necessary to ignore empty strings which
        #  count as printable but break backspace_budget)
        #
        #  FIXME: I'm almost certain backspace_budget will break here if you
        #         feed in multi-codepoint grapheme clusters.
        if char and (char.isprintable() or char == '\r'):
            self.user_input += char 
            #
            cursor.insertText(char)
            self.backspace_budget += len(char)

        # Implement backspacing characters we typed
        
        if char == '\x08' and self.backspace_budget > 0:  # Backspace
            self.user_input = self.user_input[:-1]
            cursor.deletePreviousChar()
            self.backspace_budget -= 1
        elif char == '\r':                                # Enter
            self.backspace_budget = 0
            # remove '\r'
            self.user_input = self.user_input[:-1]
            #

            #try:
            if True:
                self.run_command(self.user_input)
            
            '''
            except Exception as err:
                self.write("FAILED TO RUN COMMAND\n")
                print(f"Unexpected {err=}, {type(err)=}")
                self.show_prompt()  
            '''
            self.user_input = ''
                      
        # Scroll to the bottom on keypress, but only after modifying the
        # contents to make sure we don't scroll to where the bottom was before
        # word-wrap potentially added more lines
        scroller = self.verticalScrollBar()
        scroller.setValue(scroller.maximum())

    def show_prompt(self):
        self.write(self.PROMPT)

    def clean_line(self):
        self.moveCursor(QTextCursor.End)
        cursor = self.textCursor()

        for i in range(self.backspace_budget):
            cursor.deletePreviousChar()
            self.backspace_budget -= 1

        assert(self.backspace_budget == 0)
        self.user_input = ''


    def resizeEvent(self, event):
        # Call Qt's built-in resize event handler
        super(Terminal, self).resizeEvent(event)

        # As a quick hack, scroll to the bottom on resize
        # (The proper solution would be to preserve scroll position no matter
        # what it is)
        scroller = self.verticalScrollBar()
        scroller.setValue(scroller.maximum())

    def preprocess_command(self, command):
        # TO DO: add support of "
        # e.g. load_file "./ecg/ecg 10.json" 
        splitted = command.split(' ')

        args = []
        for c in splitted:
            args.append(c.strip())
        return args

    def register_command(self, command):
        command = command.strip()
        if self.history_index is None:
            next_idx = 0
        else:
            next_idx = (self.history_index + 1)%self.history_size
        self.history[next_idx] = command
        self.history_cursor = None
        self.history_index = next_idx


    def user_write(self, command):
        self.moveCursor(QTextCursor.End)
        cursor = self.textCursor()
        #
        self.user_input = command
        #
        cursor.insertText(command)
        self.backspace_budget += len(command)

    def show_prev_command(self):

        self.clean_line()

        if self.history_index is None:
            return 

        if self.history_cursor is None:
            self.history_cursor = self.history_index

        command = self.history[self.history_cursor]
        self.user_write(command)

        if self.history_cursor == 0:
            return

        self.history_cursor -= 1
        #ic(self.history_cursor)
        #

    def show_next_command(self):
        self.clean_line()
        if self.history_cursor is None or self.history_index is None:
            return 
        
        if self.history_cursor > self.history_index-1:
            self.history_cursor = None
            return
        
        self.history_cursor += 1

        command = self.history[self.history_cursor]
        
        #
        self.user_write(command)
        #ic(self.history_cursor)



    def run_command(self, command):
        self.write(f"`{command}`\n")
        self.write(f"Result preprocessing: {self.preprocess_command(command)}")

    
   