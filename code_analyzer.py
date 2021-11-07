import ast
import sys
import os
import os.path
import re


def function_start(func):
    def wrapper(line):
        line = line.lstrip()
        if not line.startswith('def'):
            return False
        line += '\n\tpass'
        tree = ast.parse(line)
        v = func(tree)
        return v

    return wrapper


def s001(line):  # long line
    return len(line) > 79


def s002(line):  # Indentation is not a multiple of four;
    return (len(line) - len(line.lstrip())) % 4


def s003(line):  # Unnecessary semicolon after a statement

    if ';' in line:
        if '#' not in line and line.rstrip()[-1] == ';':
            return True
        elif '#' in line:
            return line.index(';') < line.index('#')
        else:
            return False


def s004(line):  # Less than two spaces before inline comments;
    if line.lstrip()[0] == '#':
        return False
    try:
        l_comm = line.split('#')[0]
        return len(l_comm) - len(l_comm.rstrip()) < 2 and '#' in line
    except IndexError:
        return False


def s005(line):
    try:
        return 'todo' in ''.join(s.lower() for s in line.split('#')[1:])
    except IndexError:
        return False


def s007(line):
    line = line.lstrip()
    if line.startswith('class') or line.startswith('def'):
        name_ = line.split()[1]
        return line[line.index(name_)-2] == ' '
    return False


def s008(line):
    if not line.startswith('class'):
        return False
    return not bool(re.match(r'class +([A-Z][a-z]+)+(\(([A-Z][a-z]+)+\))?:', line))


def s009(line):
    line = line.lstrip()
    if not line.startswith('def'):
        return False
    return not bool(re.match(r'def +[0-9a-z_]+(_[a-z]+)*\(.*\):', line))


@function_start
def s010(tree):
    if tree.body[0].args.args:
        body = tree.body[0].args.args
        answer = [(bool(re.match(r'[a-z_]', x.arg)), x.arg) for x in body]
        if all(x[0] for x in answer):
            return False
        return ' '.join(x[1] for x in answer if not x[0])
    return False


def s011(line):
    try:
        tree = ast.parse(line.lstrip())
        if not isinstance(tree.body[0], ast.Assign):
            return False
        var_name = tree.body[0].targets[0].id
        return var_name if not bool(re.match(r'[a-z_]+', var_name)) else False
    except:
        return False


@function_start
def s012(tree):

    if tree.body[0].args.defaults:
        answer = [isinstance(x, ast.List) for x in tree.body[0].args.defaults]
        return any(answer)
    else:
        return False


def error_manager(file, path):
    blank = 0
    for i, x in enumerate(file):
        error = {}
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
            error[8] = f'{path}: Line {i + 1}: S008 Class name class_name should be written in CamelCase;'
        if s009(x):
            error[9] = f'{path}: Line {i + 1}: S009 Function name function_name should be written in snake_case.'
        if s010(x):
            error[10] = f"{path}: Line {i + 1}: S010 Argument name '{s010(x)}' should be written in snake_case;"
        if s011(x):
            error[11] = f"{path}: Line {i + 1}: S011 Variable '{s011(x)}' should be written in snake_case;"
        if s012(x):
            error[12] = f"{path}: Line {i + 1}: S012 Default argument value is mutable"
        if error:
            ordered_error = sorted([y for y in error.items()], key=lambda z: z[0])
            print(*sorted([x[1] for x in ordered_error]), sep='\n')


def main():
    directory = sys.argv[1]
    if os.path.isfile(directory):
        with open(directory) as file:
            error_manager(file, directory)
    else:
        for x in os.listdir(directory):
            file_directory = os.path.join(directory, x)
            if os.path.isfile(file_directory) and x.endswith('.py'):
                with open(file_directory) as file:
                    error_manager(file, file_directory)


if __name__ == '__main__':
    main()
