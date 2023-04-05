import re

# Define regular expression patterns for different token types
patterns = [
    (r'[ \t\n]+', None),  # Ignore whitespace
    (r'\d+', 'INTEGER'),
    (r'[a-zA-Z_]\w*', 'IDENTIFIER'),
    (r'[+][+]', 'INCREMENT'),
    (r'[-][-]', 'DECREMENT'),
    (r'[+\-*/%^]', 'OPERATOR'),
    (r'[=]', 'ASSIGNMENT'),
    (r'[()]', 'PUNCTUATION'),
    (r'.', 'DOT'),
]


def tokenize(text):
    tokens = []
    while text:
        match = None
        for pattern in patterns:
            regex, token_type = pattern
            match = re.match(regex, text)
            if match:
                if token_type:
                    tokens.append((match.group(), token_type))
                break
        if not match:
            raise ValueError(f'Invalid input: {text}')
        text = text[match.end():]
    return tokens


# Example usage:
input_text = 'x = 42.2 ^ y * 3\nz++ - --w'
tokens = tokenize(input_text)
print(tokens)
