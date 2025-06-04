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
  def __init__(self):
    # instances required for operations
    self.lexer = Lexer()
    self.parser = Parser()
    self.registry = Registry()

  # this method receives the ABSOLUTE path to entry point module
  # It recursively receives modules dependencies and adds them to Registry
  def resolve_modules(self, entrypoint: str):
    # initialize analyzed modules paths
    analyzed_paths = set()
    # initialize currently analyzing modules paths
    analyzing_paths = set()

    # get module by ABSOLUTE path
    # gets module dependencies
    # continues search until tree is not searched
    def search(path):
      # do not search analyzed path again
      if path in analyzed_paths:
        return

      # if this module is analyzing - Circular Dependency
      if path in analyzing_paths:
        raise (f'Circular dependency including module by path {path}')

      # get module and dependencies
      module = self.get_module_by_absolute_path(path)
      dependencies = self.get_module_dependencies(module)

      # set module dependencies
      module.dependencies = dependencies
      
      # add resolved module in registry
      self.registry.add_module(module)

      # make path currently analyzing
      analyzing_paths.add(path)

      # add new paths
      for dependency in dependencies:
        search(dependency.path)

      # make path analyzed
      analyzing_paths.remove(path)
      analyzed_paths.add(path)

    # start search from entry point
    search(entrypoint)

  # this method sorts modules in place and returns the sorted list
  def sort_modules(self) -> list[Module]:
    self.registry.sort_topologically()
    return self.registry.get_modules()

  # returns list of dependency modules
  # based on IMPORT statements
  # does not return duplicates
  def get_module_dependencies(self, module: Module) -> list[Module]:
    # extract statements from module
    statements = module.content.statements

    # dependencies set to prevent duplicates
    dependencies = set()

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
        dependencies.add(module)

    # return dependencies list
    return list(dependencies)

  # receives the ABSOLUTE path 
  # returns Module instance
  # does NOT parse dependencies
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
  def resolve_absolute_path(self, base_path: str, path: str) -> str:
    base_directory = os.path.dirname(base_path)
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
