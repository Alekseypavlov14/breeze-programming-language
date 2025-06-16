# Lexer 

Lexer is a part of an interpreter that parses **the source code** and returns the **list of tokens**.

## Token 

Class **Token** contains **code** and **type**
- code: stores piece of code
- type: contains type of token

## Exceptions
- LexerError - for invalid token parsing

## Logic

Lexer parses source code (string) using **Regular Expressions** and position pointer, the list of known (valid) tokens is created. Every part of code (string) is mapped to **Token** described above. As a result, the list of Tokens is obtained. For unknown symbols, **LexerError** is raised.
