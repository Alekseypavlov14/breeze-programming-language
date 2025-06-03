from resolution.module import *
from resolution.registry import *
from resolution.exceptions import *
from parser.parser import *
from lexer.lexer import *
from shared.extensions import *

import os

# this class receives entry module path and gets all its dependencies recursively.
# Instance has Lexer, Parser and Registry instances as fields to perform operations.
# it provides modules being topologically sorted (based on their dependencies).
# Topological sort is required to execute modules in correct order.
# Circular dependencies are not allowed!
class Resolver:
  # resolves dependencies starting from entry point
  # entrypoint is an ABSOLUTE path to the entry module
  def __init__(self, entrypoint: str):
    self.entrypoint = entrypoint

    # instances required for operations
    self.lexer = Lexer()
    self.parser = Parser()
    self.registry = Registry()

  # returns list of dependency modules
  # based on IMPORT statements
  # adds dependency modules to registry
  # does not add duplicates
  def get_module_dependencies(self, module: Module) -> list[Module]:
    # extract statements from module
    statements = module.content.statements

    # get import statements
    # check only first-level statements
    for statement in statements:
      # filter import statements
      if is_statement_of_class(statement, ImportStatement):
        # statement: ImportStatement 
        # -> .path: LiteralExpression 
        # -> .value: Token 
        path_token: Token = statement.path.value

        # check token to be string literal
        if not is_token_of_type(path_token, STRING_TOKEN):
          raise PathError(f'Import path has to be string literal. Received {path_token.code}')

        # extract code content
        relative_path = path_token.code
        # resolve dependency ABSOLUTE path
        absolute_path = self.resolve_absolute_path(module.path, relative_path)

        # get dependency module
        module = self.get_module_by_absolute_path(absolute_path)

        # add module
        module.dependencies.append(module)

    # return module dependencies list
    return module.dependencies

  # receives the ABSOLUTE path 
  # returns Module instance
  def get_module_by_absolute_path(self, path: str) -> Module:
    # do not parse module if it is already parsed
    if self.registry.is_module_added_by_path(path):
      return self.registry.get_module_by_absolute_path(path)

    # get file content
    content = self.get_module_content_by_absolute_path(path)

    # get module tokens
    tokens = self.lexer.parse_module(content)
    # parse AST
    ast = self.parser.parse(tokens)

    # return parsed module
    # leave dependencies as empty list until they are parsed
    return Module(path, ast)    

  # allows to get absolute path of dependency module
  # base_path represents the ABSOLUTE path of dependent module (importer)
  # path represents the RELATIVE path to dependency module (exporter)
  def resolve_absolute_path(base_path: str, path: str) -> str:
    base_directory = os.path.dirname(base_directory)
    dependency_path = os.path.join(base_directory, path)
    # returns resolved absolute path without symbolic links
    return os.path.realpath(dependency_path)

  # get module content by ABSOLUTE path
  def get_module_content_by_absolute_path(self, path: str):
    # check for path to be ABSOLUTE
    if not os.path.isabs(path):
      raise PathError(f"Absolute path expected. Received {path}")
    
    # check for correct file
    if not os.path.isfile(path):
      raise ModuleError(f"Invalid module path. Received {path}")
    
    # check file extension
    if not path.endswith(f'.{MODULE_EXTENSION}'):
      raise ModuleError(f'Invalid module extension. Received {path}')
    
    # read file content
    with open(path, "r", encoding="utf-8") as file:
      return file.read()
