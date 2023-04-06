import re

# Define regular expression patterns for different token types
patterns = [
    (r'[ \t\n]+', None),  # Ignore whitespace
    (r'\d+', 'INTEGER'),
    (r'[a-zA-Z_]\w*', 'IDENTIFIER'),
    (r'[+\-*/%^]', 'OPERATOR'),
    (r'[=]', 'ASSIGNMENT'),
    (r'[(]', 'LEFT_BRACKET'),
    (r'[)]', 'RIGHT_BRACKET'),
    (r'[+][+]', 'INCREMENT'),
    (r'[-][-]', 'DECREMENT')
]


# E  -> T E'
# E' -> + T E' | - T E' | e
# T  -> F T'
# T' -> * F T' | / F T' | % F T' | e
# F  -> ( E ) | id | id ^ F | ++ id | -- id | id ++ | id -- | - id
# id -> digit | digit . digit

class Parser(object):
    def __init__(self, lines):
        self.lines = lines
        self.tokens = []
        self.token_index = 0
        self.symbol_table = {}

    def parse(self):
        for line in self.lines:
            print(line)
            self.tokenize(line)
            print(self.tokens)
            self.token_index = 0
            self.parse_expression()

    def parse_expression(self):
        self.e()
        current_token = self.get_current_token()
        if current_token is not None:
            raise ValueError('Parsing error')

    def e(self):
        self.t()
        self.e_dash()

    def e_dash(self):
        current_token = self.get_current_token()
        if current_token is None:
            return
        if current_token[1] == 'OPERATOR' and current_token[0] in ['+', '-']:
            self.token_index += 1
            self.t()
            self.e_dash()

    def t(self):
        self.f()
        self.t_dash()
        pass

    def t_dash(self):
        current_token = self.get_current_token()
        if current_token is None:
            return
        if current_token[1] == 'OPERATOR' and current_token[0] in ['*', '/', '%']:
            self.token_index += 1
            self.f()
            self.t_dash()

    def f(self):
        current_token = self.get_current_token()
        if current_token is None:
            raise ValueError('Expected ( or id')
        if current_token[1] == 'LEFT_BRACKET':
            self.token_index += 1
            self.e()
            current_token = self.get_current_token()
            if current_token is not None and current_token[1] == 'RIGHT_BRACKET':
                self.token_index += 1
            else:
                raise ValueError('Expected )')
        elif current_token[1] == 'IDENTIFIER':
            self.token_index += 1
            current_token = self.get_current_token()
            if current_token is None:
                return
            if current_token is not None and current_token[1] == 'INCREMENT' or current_token[1] == 'DECREMENT':
                self.token_index += 1
            elif current_token is not None and current_token[1] == 'OPERATOR' and current_token[0] == '^':
                self.token_index += 1
                self.f()
        elif current_token[1] == 'INCREMENT' or current_token[1] == 'DECREMENT' or (
                current_token[1] == 'OPERATOR' and current_token[0] == '-'):
            self.token_index += 1
            current_token = self.get_current_token()
            if current_token is not None and current_token[1] == 'IDENTIFIER':
                self.token_index += 1
            else:
                raise ValueError('Expected identifier')
        else:
            raise ValueError('Expected ( or id')

    def match_identifier(self):
        if self.tokens[self.token_index][1] == 'IDENTIFIER':
            self.token_index += 1
            return True
        return False

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
        # print(self.tokens)
        for i in range(len(self.tokens)):
            if self.tokens[i][0].lower() == 'print':
                self.tokens[i] = (self.tokens[i][0], 'PRINT')

    def get_current_token(self):
        if self.token_index >= len(self.tokens):
            return None
        return self.tokens[self.token_index]


# Example usage:
# input_text = 'x = 42.2 ^ y * 3\nPrInt x,z'
input_text = '((x+y+z)+(w+v+u))'
parser = Parser(input_text.splitlines())
parser.parse()
