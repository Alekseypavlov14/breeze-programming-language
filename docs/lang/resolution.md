# Resolution

This module is responsible for creating a modules graph (dependency tree) and parse modules.
**Resolver** class uses Lexer and Parser instances to parse modules code.

## Logic

Resolution starts with getting entry module absolute path. 
Then module is parsed (AST is created) and the process repeats for dependency modules creating the dependency tree. (Only top-level **import** statements are valid).

**Registry** class is a storage of application modules. It does not contain duplicated modules and circular dependencies while sorting.

# Aliases

Resolver receives **aliases dict** during initialization. All aliases must start with ```@``` symbol.
