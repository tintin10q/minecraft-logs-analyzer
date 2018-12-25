"""
Author: Hawkpath (hawkpathas@gmail.com)
Description: Defines functions that operate on Minecraft chat logs.
             If the file is run directly, it will attempt to compute your
             total playtime by finding your Minecraft logs folder.
             Due to the text encoding used, this will likely only work on
             Windows.
Version: 1.1.0
"""

from datetime import timedelta
from io import TextIOBase, SEEK_END
from glob import iglob
import gzip
import os
from pathlib import Path
import re
from types import GeneratorType

def read_backward_until(stream, delimiter, buf_size=32, stop_after=1,
                        trim_start=0):
    """
    `stream` (TextIOBase): Stream to read from
    `delimiter` (str|re._pattern_type): Delimeter marking when to stop reading
    `buf_size` (int): Number of characters to read/store in buffer while
                      progressing backwards. Ensure this is greater than or
                      equal to the intended length of `delimiter` so that the
                      entire delimiter can be detected
    `stop_after` (int): Return the result after detecting this many delimiters
    `trim_start` (int): If not 0, this many characters will be skipped
                        from the beginning of the output (to return only
                        what comes after delimiter, for instance)
    """
    if not isinstance(stream, TextIOBase):
        raise TypeError('Expected type of `stream` to be TextIOBase, got %s'
                        % type(stream))
    if not (isinstance(delimiter, str)
            or isinstance(delimiter, re._pattern_type)):
        raise TypeError('Expected type of `delimiter` to be str or '
                        'regex pattern, got %s' % type(delimiter))

    stop_after -= 1
    original_pos = stream.tell()
    cursor = stream.seek(0, SEEK_END)
    buf = ' ' * (buf_size*2)

    while cursor >= 0:
        if cursor >= buf_size:
            cursor -= buf_size
        else:
            cursor = 0
        stream.seek(cursor)
        # Combine the previous two buffers in case delimiter runs
        # across two buffers
        buf = stream.read(buf_size) + buf[:buf_size]

        if isinstance(delimiter, str):
            delim_pos = buf.find('\n')
        else:
            delim_pos = delimiter.search(buf)
            delim_pos = delim_pos.start() if delim_pos else -1

        if delim_pos == -1 or delim_pos >= buf_size:
            # Skip if no delimiter found or if it's in the second half of
            # the buffer (it will turn up twice as it moves to the end of
            # the buffer)
            pass
        elif stop_after > 0:
            # Decrement since we found delimiter
            stop_after -= 1
        else:
            # Move to the start of the final line
            stream.seek(cursor + delim_pos + trim_start - 1)
            last_line = stream.read()
            stream.seek(original_pos)
            return last_line
    # No match
    return None

def read_last_line(stream):
    return read_backward_until(stream, os.linesep, stop_after=2, trim_start=2)

def iter_logs(path):
    if isinstance(path, str):
        path = Path(path)
    elif not isinstance(path, Path):
        raise TypeError('Expected type of `path` to be str or Path, got %s'
                        % type(path))
    open_methods = {'.log': open, '.gz': gzip.open}

    for file in path.iterdir():
        if file.suffix not in open_methods:
            continue
        elif not file.name.startswith('20'):
            continue
        with open_methods[file.suffix](file, 'rt', encoding='ansi',
                                       errors='replace', newline='') as f:
            yield f


def count_playtime(path, count=-1, print_files='file'):
    time_pattern = re.compile(
        r'\[(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\]', re.I
    )
    time_pattern_simple = re.compile(r'\d{2}:\d{2}:\d{2}')
    total_time = timedelta()

    for log in iter_logs(path):
        if count == 0:
            return
        count -= 1

        try:
            start_time = time_pattern.match(log.readline()).groupdict()
            end_time = time_pattern.match(
                    read_backward_until(log, time_pattern_simple)).groupdict()
        except AttributeError:
            # Not a recognized chat log
            continue
        except EOFError:
            print('### Error: %s may be corrupted -- skipping ###'
                  % Path(log.name).name)
            continue
        start_time = timedelta(
            hours=int(start_time['hour']),
            minutes=int(start_time['min']),
            seconds=int(start_time['sec'])
        )
        end_time = timedelta(
            hours=int(end_time['hour']),
            minutes=int(end_time['min']),
            seconds=int(end_time['sec'])
        )
        if end_time < start_time:
            end_time += timedelta(days=1)
        delta = end_time - start_time
        total_time += delta
        if print_files == 'full':
            print(log.name, delta)
        elif print_files == 'file':
            print(Path(log.name).name, delta)

    return total_time


def search_logs(pattern, return_after=-1, output_file=None):
    # if sub is not None:
    #     pattern =   r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\S+ ' \
    #               + r'\[(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\] ' \
    #               + r'\[(?P<caller>[\w ]+?/)(?P<level>[A-Z]+)\]: ' \
    #               + pattern
    pattern = re.compile(pattern, flags=re.I)

    try:
        out = None
        if output_file:
            out = open(output_file, 'wt', encoding='utf_8')

        for log in iter_logs():
            for line in log:
                search = re.search(pattern, line)
                if search:
                    return_after -= 1
                    # Set what will be output
                    if pattern.groups != 0:
                        # There is a capturing group in the pattern regex;
                        # use the first one available
                        to_output = search.group(1)
                    else:
                        to_output = line

                    if out:
                        # Write to file
                        out.write(to_output)
                    else:
                        print(to_output)

                if return_after == 0:
                    return
    finally:
        if out:
            out.close()



if __name__ == '__main__':

    def input_validate(input_str, validate, default=None, convert_in=None,
                       fail_msg='Please enter a valid value.'):
        valid = False
        while not valid:
            out = input(input_str)
            if not out and default:
                out = default
            if out == 'exit':
                exit()
            if convert_in:
                try:
                    out = convert_in(out)
                except:
                    # Ignoring errors in conversion, so the value
                    # may remain a string
                    pass
            try:
                valid = validate(out)
            except Exception as e:
                # Assume errors in validation as invalid
                valid = False
            if not valid:
                print(fail_msg)
        return out

    clear = lambda: os.system('cls')

    print('''\
== Welcome to the Minecraft log analyzer ==

You may press enter at any prompt to select the default option
(if it exists) or type exit to leave.

What would you like to do?
[1] Count total playtime
[exit] Exit the program (default)

''')
    operation = input_validate('Operation: ', lambda x: x in {'1'},
                               default='exit')
    clear()

    if operation == '1':
        # Count playtime
        print('''\
How do you want to locate your logs folders?

[1] Automatic (default)
[2] Enter path(s)
[3] Enter glob

''')
        locate_method = input_validate('Locate method: ',
                                       lambda x: x in range(1,5),
                                       convert_in=int)
        clear()

        if locate_method == 1:
            default_logs_path = Path('C:/Users', os.getlogin(),
                                     'AppData/Roaming/.minecraft', 'logs')
            if default_logs_path.exists():
                print('\nTotal playtime:', count_playtime(default_logs_path))
            else:
                print(
'''\
Could not automatically locate your .minecraft/logs folder.
Please try running this program again and enter a path manually.\
''')

        elif locate_method == 2:
            print(
'''\
Please enter every logs folder path that you want to scan.
Separate multiple paths with pipes (vertical bar: | ).

''')
            paths = input_validate(
                'Path(s): ', lambda path_list: all(
                    [path.exists() for path in path_list]
                ), convert_in=lambda path_str: tuple(
                    Path(path.strip()) for path in path_str.split('|')
                        if path
                ), fail_msg='One or more of your paths do not exist.'
            )
            total_time = timedelta()
            for path in paths:
                total_time += count_playtime(
                    path,
                    print_files='full' if len(paths) > 1 else 'file'
                )
            print('\nTotal playtime:', total_time)

        elif locate_method == 3:
            print(
'''\
Enter a glob(s) to select every log folder you want to scan.
Separate multiple globs with pipes (vertical bar: | ).

Folders that start with period must be explicitly specified
(AppData/Roaming/.*/logs)

Example: To find all logs folders in folders that start with . in AppData,
C:/Users/USERNAME/AppData/Roaming/.*/**/logs

'''
)
            globs = input_validate(
                'Glob(s): ',
                lambda g: g and all([isinstance(i, GeneratorType) for i in g]),
                convert_in=lambda g: g and tuple(
                    iglob(i, recursive=True) for i in g.split('|')
                )
            )
            total_time = timedelta()
            for glob in globs:
                for path in glob:
                    if Path(path).is_dir():
                        total_time += count_playtime(path, print_files='full')
            print('\nTotal playtime:', total_time)


    os.system('pause')
