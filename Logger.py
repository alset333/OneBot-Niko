#!/usr/bin/env python3

"""
Logging and printing utility.
Copyright (C) 2019 Peter Maar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

"""

from time import time

logfile_location = 'log.txt'
logfile = open(logfile_location, 'a', encoding='utf-8')  # Open for appending.
# UTF-8 helps with some special characters that happen sometimes (like the "No Category:" line of the output of ?help)

# To use, just add this import:
# "from Logger import log"

logfile_closed = False


def log(*args, sep=' ', end='\n', flush=False):
    """
    Print and log the values.
    Optional keyword arguments:
    sep:   string inserted between values, default a space.
    end:   string appended after the last value, default a newline.
    flush: whether to forcibly flush the log stream.
    """

    time_string = 'Time ' + str(time())[:15] + ":\t"
    output_string = time_string

    for value in args:
        output_string += str(value) + sep

    output_string = output_string[:-len(sep)]

    # Add to the newlines spaces and a tab to match the time string length
    output_string = output_string.replace('\n', '\n' + ' '*(len(time_string)-1) + '\t')

    output_string += end

    print(output_string, end='')
    if not logfile_closed:
        logfile.write(output_string)
    else:
        print("Error:\tOops! You tried to log with the logfile closed!")

    if flush:
        logfile.flush()


def close_log():
    global logfile_closed

    logfile.close()
    logfile_closed = True
