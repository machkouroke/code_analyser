import ast
import os
import os.path
import re

from typing.io import TextIO


def function_start(func):
    def wrapper(line: str):
        """
        Parse a line of code in ast Tree
        :param line:  Line of code to parse
        """
        line = line.lstrip()
        if not line.startswith('def'):
            return False
        line += '\n\tpass'
        tree: ast.AST = ast.parse(line)
        return func(tree)
    return wrapper


def s001(line: str) -> bool:
    """
    Check if Line's length is greater than 79 characters;
    :param line: Line of code to check
    :return: line length > 79 or not
    """
    return len(line) > 79


def s002(line: str) -> bool:
    """
    Check if Line's indentation is a multiple of four;
    :param line: Line of code to check
    :return: Line's indentation is a multiple of four or not
    """
    return bool((len(line) - len(line.lstrip())) % 4)


def s003(line: str) -> bool:
    """
    Check if Line has a semicolon at the end of the line;
    :param line:  Line of code to check
    :return: Line has a semicolon at the end of the line or not
    """
    if ';' in line:
        if '#' not in line and line.rstrip()[-1] == ';':
            return True
        elif '#' in line:
            return line.index(';') < line.index('#')
        else:
            return False
    return False


def s004(line: str) -> bool:
    """
    Check if Line has a space before inline comments;
    :param line: Line of code to check
    :return: Line has a space before inline comments or not
    """
    if line.lstrip()[0] == '#':
        return False
    try:
        l_comm = line.split('#')[0]
        return len(l_comm) - len(l_comm.rstrip()) < 2 and '#' in line
    except IndexError:
        return False


def s005(line: str) -> bool:
    """
    Check if Line has a TODO comment;
    :param line: Line of code to check
    :return: Line has a TODO comment or not
    """
    try:
        return 'todo' in ''.join(s.lower() for s in line.split('#')[1:])
    except IndexError:
        return False


def s007(line: str) -> bool:
    """
    Check if Line has too many spaces after a keyword {def, class}
    :param line: Line of code to check
    :return: Line has too many spaces after a keyword {def, class} or not
    """
    line = line.lstrip()
    if line.startswith('class') or line.startswith('def'):
        name_ = line.split()[1]
        return line[line.index(name_) - 2] == ' '
    return False


def s008(line: str) -> bool:
    """
    Check if Line has a class name not written in CamelCase
    :param line: Line of code to check
    :return: Line has a class name not written in CamelCase or not
    """
    return not bool(re.match(r'class +([A-Z][a-z]+)+(\(([A-Z][a-z]+)+\))?:', line)) if line.startswith(
        'class') else False


def s009(line: str) -> bool:
    """
    Check if Line has a function name not written in snake_case
    :param line: Line of code to check
    :return: Line has a function name not written in snake_case or not
    """
    line = line.lstrip()
    if not line.startswith('def'):
        return False
    return not bool(re.match(r'def +[\da-z_]+(_[a-z]+)*\(.*\):', line))


@function_start
def s010(tree) -> bool | str:
    """
    Check if Line has an Argument name not written in snake_case
    :param tree: Line of code parsed in ast Tree
    :return: Line has an Argument name not written in snake_case or not
    """
    if tree.body[0].args.args:
        body = tree.body[0].args.args
        answer = [(bool(re.match(r'[a-z_]', x.arg)), x.arg) for x in body]
        if all(x[0] for x in answer):
            return False
        return ' '.join(x[1] for x in answer if not x[0])
    return False


def s011(line: str) -> bool:
    """
    Check if Line has a variable name not written in snake_case
    :param line: Line of code to check
    :return: Line has a variable name not written in snake_case or not
    """
    try:
        tree = ast.parse(line.lstrip())
        if not isinstance(tree.body[0], ast.Assign):
            return False
        var_name = tree.body[0].targets[0].id
        return False if bool(re.match(r'[a-z_]+', var_name)) else var_name
    except IndentationError:
        return False


@function_start
def s012(tree) -> bool:
    """
    Check if the default argument of a function is mutable
    :param tree: Line of code parsed in ast Tree
    :return: the default argument of a function is mutable or not
    """
    if tree.body[0].args.defaults:
        answer = [isinstance(x, ast.List) for x in tree.body[0].args.defaults]
        return any(answer)
    else:
        return False


def error_manager(file: TextIO, path: str) -> None:
    """
    Manage errors in a file
    :param file: file to check
    :param path: path to the file to check
    """
    blank: int = 0
    for i, x in enumerate(file):
        error: dict = {}
        if len(x) == 1:
            blank += 1
            continue
        elif blank > 2:
            error[6] = f'{path}: Line {i + 1}: S006 More than two blank lines preceding a code line'
        blank = 0
        if s001(x):
            error[1] = f'{path}: Line {i + 1}: S001 Too long'
        if s002(x):
            error[2] = f'{path}: Line {i + 1}: S002 Indentation is not a multiple of four;'
        if s003(x):
            error[3] = f'{path}: Line {i + 1}: S003 Unnecessary semicolon'
        if s004(x):
            error[4] = f'{path}: Line {i + 1}: S004 At least two spaces required before inline comments'
        if s005(x):
            error[5] = f'{path}: Line {i + 1}: S005 TODO found'
        if s007(x):
            error[7] = f'{path}: Line {i + 1}: S007 Too many spaces after "{x.split()[0]}"'
        if s008(x):
            error[8] = f'{path}: Line {i + 1}: S008 Class name  should be written in CamelCase;'
        if s009(x):
            error[9] = f'{path}: Line {i + 1}: S009 Function name function_name should be written in snake_case.'
        if s010(x):
            error[10] = f"{path}: Line {i + 1}: S010 Argument name '{s010(x)}' should be written in snake_case;"
        if s011(x):
            error[11] = f"{path}: Line {i + 1}: S011 Variable '{s011(x)}' should be written in snake_case;"
        if s012(x):
            error[12] = f"{path}: Line {i + 1}: S012 Default argument value is mutable"
        if error:
            ordered_error = sorted(list(error.items()), key=lambda z: z[0])
            print(*sorted([x[1] for x in ordered_error]), sep='\n')


def main():
    directory: str = input('Please indicate the path to the file: ')
    if os.path.isfile(directory):
        with open(directory) as file:
            error_manager(file, directory)
    else:
        for x in os.listdir(directory):
            file_directory: str = os.path.join(directory, x)
            if os.path.isfile(file_directory) and x.endswith('.py'):
                with open(file_directory) as file:
                    error_manager(file, file_directory)


if __name__ == '__main__':
    main()
