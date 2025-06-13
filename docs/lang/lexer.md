# Lexer 

Lexer is a part of an interpreter that parses **the source code** and returns the **list of tokens**.

## Token 

Class **Token** contains **code** and **type**
- code: stores piece of code
- type: contains type of token

## Exceptions
- LexerError - for invalid token parsing

## Logic

Lexer parses source code using **Regular Expressions**, the list of known (valid) tokens is defined. Every part of code (string) is mapped to **Token** described above. As a result, the list of Tokens is obtained. For unknown symbols, **LexerError** is raised.
