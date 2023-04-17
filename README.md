# Adventure Game

## Student Information

- Name: Jigar Chhatrala
- Stevens Login: jchhatra@stevens.edu

## Project Information

- Public GitHub Repo URL: https://github.com/jigargc/PosixParser
- Estimated Hours Spent: 30+ hours

## Testing

I thoroughly tested my code by writing unit tests for each function, as well as manually testing edge cases and
verifying the correctness of the output.

## Known Bugs and Issues

- In some cases, the application might not handle incorrect user input gracefully, causing unexpected behavior.

## Resolving a Difficult Issue

N/A

## Implemented Extensions

1. **Extension 1: Op-equals**
    - New verb: "op-equals" to compare two items.
    - To exercise this new verb, use " <item1> == <item2>"
    - If the two items are the same, the application will return 1
    - If the two items are not the same, the application will return 0
    - example usage : 1==2 will return 0
    - example usage : 1==1 will return 1
    - example usage : a = 1==2 then a will be 0
    - example usage : a == 1==1 returns 0

2. **Extension 2: Relational operations**
    - Implemented relational operations ==, <=, >=, !=, <, >, using 1 to mean true and 0 to mean false.
    - To exercise this new verb, use " <item1> <operator> <item2>"
    - example usage : 1 < 2 will return 1
    - example usage : 1 > 2 will return 0
    - example usage : a = 1 < 2 then a will be 1
    - example usage : a < 1 < 2 returns 1
    - example usage : a < 1 > 2 returns 0
    - example usage : a < 1 == 2 returns 0
    - example usage : a < 1 != 2 returns 1
    - example usage : a < 1 <= 2 returns 1

3. **Extension 3: Boolean operations**
    - Implemented boolean operations &&, ||, !.
    - For the boolean operations, the application will return 1 if the condition is true, and 0 if the condition is
      false.
    - example usage : 1 && 0 will return 0
    - example usage : 1 && 1 will return 1
    - example usage : 1 || 0 will return 1
    - example usage : 0 || 0 will return 0
    - example usage : !1 will return 0
    - example usage : !0 will return 1
    - example usage : a = 1 && 0 then a will be 0

4. **Extension 4: Comments**
    - Implemented comments using the # symbol and /* comment */.
    - \# symbol is used for single line comments
    - /* comment */ is used for multi line comments
    - example usage : # this is a comment
    - example usage : /* this is a comment */
    - example usage : /* this is a comment /* this is a nested comment */ this is a comment */