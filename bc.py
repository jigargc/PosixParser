import re

# Define regular expression patterns for different token types
patterns = [
    (r'[ \t\n]+', None),  # Ignore whitespace
    (r'\d+\.\d+', 'IDENTIFIER'),
    (r'\d+', 'IDENTIFIER'),
    (r'[a-zA-Z_]\w*', 'IDENTIFIER'),
    (r'[+][+]', 'INCREMENT'),
    (r'[-][-]', 'DECREMENT'),
    (r'[+\-*/%^]', 'OPERATOR'),
    (r'[=]', 'ASSIGNMENT'),
    (r'[(]', 'LEFT_BRACKET'),
    (r'[)]', 'RIGHT_BRACKET')
]


# var -> =E
# E  -> T E'
# E' -> + T E' | - T E' | e
# T  -> F T'
# T' -> * F T' | / F T' | % F T' | e
# F  -> ( E ) | id | id ^ F | ++ id | -- id | id ++ | id -- | - id
# id -> digit | digit . digit


def remove_comments(code):
    return re.sub(r"(?s)/\\*.*?\\*/|//.*", " ", code)


class Parser(object):

    def __init__(self, code):
        self.lines = remove_comments(code).strip().splitlines()
        print(self.lines)
        self.tokens = []
        self.token_index = 0
        self.symbol_table = {}
        self.parse()

    def parse(self):
        for line in self.lines:
            self.tokenize(line)
            # print(self.tokens)
            self.token_index = 0
            self.parse_line()

    def parse_line(self):
        current_token = self.get_current_token()
        # print(current_token)
        if current_token[1] == 'PRINT':
            return self.parse_print()
        elif current_token[1] == 'IDENTIFIER' and re.match(patterns[3][0], current_token[0]):
            self.parse_assignment()

    def parse_print(self):
        pass

    def parse_assignment(self):
        prev_token = self.get_current_token()
        self.token_index += 1
        current_token = self.get_current_token()
        if current_token is not None and current_token[1] == 'ASSIGNMENT':
            self.token_index += 1
            val = self.parse_expression()
            self.symbol_table[prev_token[0]] = val
            print(self.symbol_table)
            return
        self.token_index += -1
        self.parse_expression()

    def parse_expression(self):
        val = self.e()
        current_token = self.get_current_token()
        if current_token is not None:
            raise ValueError('Parsing error')
        return val

    def e(self):
        t_val = self.t()
        return self.e_dash(t_val)

    def e_dash(self, val):
        current_token = self.get_current_token()
        if current_token is None:
            return val
        if current_token[1] == 'OPERATOR' and current_token[0] in ['+', '-']:
            self.token_index += 1
            t_val = self.t()
            if current_token[0] == '+':
                val = val + t_val
            elif current_token[0] == '-':
                val = val - t_val
            return self.e_dash(val)
        return val

    def t(self):
        f_val = self.f()
        return self.t_dash(f_val)

    def t_dash(self, val):
        current_token = self.get_current_token()
        if current_token is None:
            return val
        if current_token[1] == 'OPERATOR' and current_token[0] in ['*', '/', '%']:
            self.token_index += 1
            f_val = self.f()
            if current_token[0] == '*':
                val = val * f_val
            elif current_token[0] == '/' and f_val != 0:
                val = val / f_val
            elif current_token[0] == '/' and f_val == 0:
                raise ValueError('Division by zero')
            elif current_token[0] == '%' and f_val != 0:
                val = val % f_val
            elif current_token[0] == '%' and f_val == 0:
                raise ValueError('Division by zero')
            return self.t_dash(val)
        return val

    def f(self):
        current_token = self.get_current_token()
        if current_token is None:
            raise ValueError('Expected ( or id')
        if current_token[1] == 'LEFT_BRACKET':
            self.token_index += 1
            val = self.e()
            current_token = self.get_current_token()
            if current_token is not None and current_token[1] == 'RIGHT_BRACKET':
                self.token_index += 1
                return val
            else:
                raise ValueError('Expected )')
        elif current_token[1] == 'IDENTIFIER':
            identifier_val = self.get_identifier_val()
            pre_token = current_token
            self.token_index += 1
            current_token = self.get_current_token()
            if current_token is None:
                return identifier_val
            if current_token is not None and current_token[1] == 'INCREMENT' or current_token[1] == 'DECREMENT':
                self.token_index += 1
                return identifier_val
            elif current_token is not None and current_token[1] == 'OPERATOR' and current_token[0] == '^':
                self.token_index += 1
                other_val = self.f()
                return identifier_val ** other_val
            return identifier_val
        elif current_token[1] == 'INCREMENT' or current_token[1] == 'DECREMENT' or (
                current_token[1] == 'OPERATOR' and current_token[0] == '-'):
            self.token_index += 1
            operation = current_token[1]
            current_token = self.get_current_token()
            if current_token is not None and current_token[1] == 'IDENTIFIER':
                identifier_val = self.get_identifier_val()
                if operation == 'INCREMENT':
                    self.symbol_table[current_token[0]] = identifier_val + 1
                if operation == 'DECREMENT':
                    self.symbol_table[current_token[0]] = identifier_val - 1
                if operation == 'OPERATOR':
                    self.symbol_table[current_token[0]] = -identifier_val
                self.token_index += 1
                return self.symbol_table[current_token[0]]
            else:
                raise ValueError('Expected identifier')
        else:
            raise ValueError('Expected ( or id')

    def get_identifier_val(self):
        current_token = self.get_current_token()
        if current_token is None:
            raise ValueError('Expected identifier')

        regex, token_type = patterns[1]
        match = re.match(regex, current_token[0])
        if match:
            return float(current_token[0])
        regex, token_type = patterns[2]
        match = re.match(regex, current_token[0])
        if match:
            return int(current_token[0])
        if current_token[0] in self.symbol_table:
            return self.symbol_table[current_token[0]]
        raise ValueError(f'Undefined identifier: {current_token[0]}')

    def tokenize(self, inp):
        self.tokens = []
        while inp:
            match = None
            for pattern in patterns:
                regex, token_type = pattern
                match = re.match(regex, inp)
                if match:
                    if token_type:
                        self.tokens.append((match.group(), token_type))
                    break
            if not match:
                raise ValueError(f'Invalid input: {inp}')
            inp = inp[match.end():]
        for i in range(len(self.tokens)):
            if self.tokens[i][0].lower() == 'print':
                self.tokens[i] = (self.tokens[i][0], 'PRINT')

    def get_current_token(self):
        if self.token_index >= len(self.tokens):
            return None
        return self.tokens[self.token_index]

# Example usage:
# input_text = 'x = 42.2 ^ y * 3\nPrInt x,z'
# input_text = """
# pi = 3.14159
# r = 2
# area = pi * r^2
# """
# parser = Parser(input_text)
# parser.parse()
