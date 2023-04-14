import re
import sys

# Regular expressions for the tokens
token_regex = {
    'space': r'[ \t\n]+',
    'id': r'[a-zA-Z_]\w*',
    'num': r'\d+(\.\d*)?',
    'inc': r'\+\+',
    'dec': r'--',
    'lpar': r'\(',
    'rpar': r'\)',
    'plus': r'\+',
    'minus': r'-',
    'mul': r'\*',
    'div': r'/',
    'mod': r'%',
    'pow': r'\^',
    'not': r'!',
    'eq': r'==',
    'neq': r'!=',
    'lt': r'<',
    'le': r'<=',
    'gt': r'>',
    'ge': r'>=',
    'and': r'&&',
    'or': r'\|\|',
    'assign': r'=',
    'comma': r','
}


def remove_comments(code: str):
    while True:
        ind = code.find('/*')
        if ind == -1:
            break
        tmp = code[ind:]
        j = tmp.find('*/')
        code = code[:ind] + ('' if j == -1 else tmp[j + 2:])
    new_code = []
    for _line in code.splitlines():
        i = _line.find('#')
        if i != -1:
            new_code.append(_line[:i])
        else:
            new_code.append(_line)
    return ('\n'.join(new_code)).strip()


def tokenize(code):
    _tokens = []
    code = code.strip()
    _i = 0
    while _i < len(code):
        match = None
        for token_type, regex in token_regex.items():
            _pattern = re.compile(regex)
            match = _pattern.match(code, _i)
            if match:
                tok = (token_type, match.group(0))
                if tok[0] != 'space':
                    _tokens.append(tok)
                _i = match.end(0)
                break
        if not match:
            raise ValueError("Invalid input:")
    return _tokens


class Parser:
    def __init__(self, tokens, symbol_table):
        self.tokens = tokens
        self.pos = 0
        self.symbol_table = symbol_table

    def parse(self):
        val = self.a()
        if self.pos < len(self.tokens):
            raise ValueError('Parse error')
        return val, self.symbol_table

    def a(self):
        val = self.b()
        return self.a_dash(val)

    def a_dash(self, val):
        current_token = self.current_token()
        if current_token is None:
            return val
        if current_token[1] == '||':
            self.pos += 1
            b_val = self.b()
            return self.a_dash(float(val != 0 or b_val != 0))
        return val

    def b(self):
        val = self.c()
        return self.b_dash(val)

    def b_dash(self, val):
        current_token = self.current_token()
        if current_token is None:
            return val
        if current_token[1] == '&&':
            self.pos += 1
            c_val = self.c()
            return self.b_dash(float((val != 0 and c_val != 0)))
        return val

    def c(self):
        val = self.d()
        return self.c_dash(val)

    def c_dash(self, val):
        current_token = self.current_token()
        if current_token is None:
            return val
        if current_token[1] in ['==', '!=']:
            self.pos += 1
            d_val = self.d()
            if current_token[1] == '==':
                val = val == d_val
            elif current_token[1] == '!=':
                val = val != d_val
            return self.c_dash(float(val))
        return val

    def d(self):
        val = self.e()
        return self.d_dash(val)

    def d_dash(self, val):
        current_token = self.current_token()
        if current_token is None:
            return val
        if current_token[1] in ['<', '<=', '>', '>=']:
            self.pos += 1
            e_val = self.e()
            if current_token[1] == '<':
                val = val < e_val
            elif current_token[1] == '<=':
                val = val <= e_val
            elif current_token[1] == '>':
                val = val > e_val
            elif current_token[1] == '>=':
                val = val >= e_val
            return self.d_dash(float(val))
        return val

    def e(self):
        val = self.f()
        return self.e_dash(val)

    def e_dash(self, val):
        current_token = self.current_token()
        if current_token is None:
            return val
        if current_token[1] in ['+', '-']:
            self.pos += 1
            t_val = self.f()
            if current_token[1] == '+':
                val = val + t_val
            elif current_token[1] == '-':
                val = val - t_val
            return self.e_dash(val)
        return val

    def f(self):
        val = self.g()
        return self.f_dash(val)

    def f_dash(self, val):
        current_token = self.current_token()
        if current_token is None:
            return val
        if current_token[1] in ['*', '/', '%']:
            self.pos += 1
            g_val = self.g()
            if current_token[1] == '*':
                val = val * g_val
            elif current_token[1] == '/' and g_val != 0:
                val = val / g_val
            elif current_token[1] == '/' and g_val == 0:
                raise ZeroDivisionError('divide by zero')
            elif current_token[1] == '%' and g_val != 0:
                val = val % g_val
            elif current_token[1] == '%' and g_val == 0:
                raise ZeroDivisionError('divide by zero')
            return self.f_dash(val)
        return val

    def g(self):
        val = self.h()
        current_token = self.current_token()
        if current_token is None:
            return val
        if current_token[1] == '^':
            self.pos += 1
            g_val = self.g()
            return val ** g_val
        return val

    def h(self):
        current_token = self.current_token()
        if current_token is None:
            raise ValueError('Expected identifier')
        if current_token[0] == 'not':
            self.pos += 1
            return not self.i()
        elif current_token[0] == 'minus':
            self.pos += 1
            return -self.i()
        else:
            return self.i()

    def i(self):
        current_token = self.current_token()
        if current_token is None:
            raise ValueError('Expected identifier')
        if current_token[0] == 'lpar':
            self.pos += 1
            val = self.a()
            current_token = self.current_token()
            if current_token is None:
                raise ValueError('Expected )')
            if current_token[0] != 'rpar':
                raise ValueError('Expected )')
            else:
                self.pos += 1
                return val
        elif current_token[0] == 'id':
            prev_token = current_token
            self.pos += 1
            current_token = self.current_token()
            if current_token is None:
                return self.get_value(prev_token[1])
            if current_token[0] in ['inc', 'dec']:
                self.pos += 1
                val = self.get_value(prev_token[1]) + 1 if current_token[0] == 'inc' else -1
                self.symbol_table[prev_token[1]] = val
                return val
            return self.get_value(prev_token[1])
        elif current_token[0] in ['inc', 'dec']:
            self.pos += 1
            prev_token = current_token
            current_token = self.current_token()
            if current_token is None:
                raise ValueError('Expected identifier')
            if current_token[0] != 'id':
                raise ValueError('Expected identifier')
            else:
                self.pos += 1
                val = self.get_value(current_token[1]) + 1 if prev_token[0] == 'inc' else -1
                self.symbol_table[current_token[1]] = val
                return val
        elif current_token[0] == 'num':
            self.pos += 1
            return float(current_token[1])
        else:
            raise ValueError('Expected ( or id')

    def current_token(self):
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def get_value(self, var):
        if var == 'print':
            raise ValueError('print is a reserved keyword')
        if var not in self.symbol_table:
            self.symbol_table[var] = 0.0
            return 0.0
        return self.symbol_table[var] * 1.0


class Interpreter:
    def __init__(self, inp):
        self.inp = inp
        self.symbol_table = {}
        self.output = []

    def print_output(self):
        for line in self.output:
            print(line)

    def interpret(self):
        lines = self.inp.splitlines()
        if len(lines) == 0:
            print("parse error")
            return
        for line in lines:
            line = line.strip()
            # print(line)
            if line == '':
                continue
            try:
                if len(line) > 5 and line[:5] == 'print' and len(line) > 6 and line[5] == ' ':
                    self.print_exp(line[5:].strip())
                else:
                    self.identifier(line)
            except ValueError as e:
                # print(e)
                # self.print_output()
                print("parse error")
                return
            except ZeroDivisionError:
                # self.print_output()
                print("divide by zero")
                return
        self.print_output()

    def print_exp(self, line):
        sub_expression = line.split(',')
        _val = []
        if len(sub_expression) == 0:
            self.output.append('')
            return
        for exp in sub_expression:
            tokens = tokenize(exp)
            if len(tokens) == 0:
                continue
            try:
                val, s = Parser(tokens, self.symbol_table).parse()
            except ZeroDivisionError:
                val = 'divide by zero'
            except ValueError:
                val = 'parse error'
            _val.append(str(val))
        self.output.append(' '.join(_val))

    def identifier(self, line):
        tokens = tokenize(line)
        # print(tokens)
        if len(tokens) > 2 and tokens[1][0] == 'assign':
            self.assignment(tokens)
        else:
            # print(tokens)
            val, s = Parser(tokens, self.symbol_table).parse()
            # self.output.append(val)

    def assignment(self, tokens):
        if tokens[0][0] != 'id' and tokens[0][1] != 'print':
            raise ValueError('Expected identifier')
        val, s = Parser(tokens[2:], self.symbol_table).parse()
        self.symbol_table[tokens[0][1]] = val


def readLines():
    inpLines = ""
    for line in sys.stdin:
        if line.strip() == '':
            continue
        inpLines += line.strip() + "\n"
    return inpLines


i = Interpreter(readLines())
i.interpret()