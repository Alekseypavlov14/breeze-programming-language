# Parser

Parser is a part of interpreter that receives list of tokens and generates AST

## Hierarchy of Nodes

Node is a component of a Tree data structure used is **Abstract Syntax Tree** (AST).

**Node** is a root class in this hierarchy. It has two subclasses:
- Expression - represents expression in programming language
- Statement - represents statements in programming language

Both statements and expressions classes have a list of subclasses that specify a concrete type.

## Recursive parsing

Parsing starts with defining root statement (block of statements, equivalent of {})
Then, skipping spaces, each statement is parsed. 

If the statement is a **standard** one (condition, loop, function declaration etc.), it is parsed separately using defined template (specifies **required** tokens and expressions). If standard statement does not match the template, **ParserError** is raised.

All other statements (computations, assignments, function calls) are considered **expression statement** (statement that contains single expression). 

Expression is a part of code that can be evaluated and have side effect. They are built from **fundamental** expressions (literal and identifiers) and operators (plus, minus, brackets etc.). Together, **expression statement** is a **tree** that contains nodes with other expressions. Operators form a tree based on their **precedence** (for example, operator **MULTIPLICATION** (*) has higher precedence than operator **PLUS** (+))

Examples of expressions:
- `a + b`
- `print()`
- `[ a, b, c ]`

Operators can be **unary**: prefix, suffix and affix (both), **binary**, **grouping** (for brackets) and **association** (curly braces that are parsed as **hashmap** literal). 

Expressions are parsed until specified separator (usually NEWLINE) and parser recursively generates tree of operations based on their **precedence**. 

Expressions cannot follow each other in the same AST node without operator between them. Every pair of expressions is connected by **operator** or belongs to different **expression statements**.

## Parser methods

Parser methods are built on two basic methods: match_token and require_token
**match_token** returns bool for current token match and does not move position pointer
**require_token** returns found token and raises exception if it is not received (spaces are skipped)

There are other methods to get tokens and move pointer but they are utilities.

## Exceptions
- ParserError - is raised when required token is not present
