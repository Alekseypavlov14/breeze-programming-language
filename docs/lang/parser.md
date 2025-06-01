# Parser

Parser is a part of interpreter that receives list of tokens and generates AST

## Hierarchy of Nodes

Node is a component of a Tree data structure used is **Abstract Syntax Tree** (AST).

**Node** is a root class in this hierarchy. It has two subclasses:
- Expression - represents expression in programming language
- Statement - represents statements in programming language

Both statements and expressions classes have a list of subclasses that specify a concrete type.

## Parser methods

Parser methods are built on two basic methods: match_token and require_token
**match_token** returns bool for current token match and does not move position pointer
**require_token** returns found token and raises exception if it is not received (spaces are skipped)

(TODO)

## Exceptions
- ParserError - is raised when required token is not present
