from resolution.module import *
from resolution.registry import *
from resolution.exceptions import *
from resolution.aliases import *
from lib.module import *
from parser.parser import *
from lexer.lexer import *
from shared.extensions import *

import importlib.util
import importlib
import os
import re

# this class receives entry module path and gets all its dependencies recursively.
# Instance has Lexer, Parser and Registry instances as fields to perform operations.
# Instance has aliases field which is dictionary (str -> str)
# it provides modules being topologically sorted (based on their dependencies).
# Topological sort is required to execute modules in correct order.
# Circular dependencies are not allowed!
class Resolver:
  def __init__(self, aliases = dict()):
    # instances required for operations
    self.lexer = Lexer()
    self.parser = Parser()
    self.registry = Registry()
    # aliases dict
    self.aliases: dict = aliases

  # Step 1: Resolve module graph (dependency tree)
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
        raise ResolutionError(f'Circular dependency including module by path {path}')

      # get module and dependency paths
      module = self.get_module_by_absolute_path(path)
      dependencies = self.get_module_dependency_paths(module)

      # set module dependency paths
      module.dependencies = dependencies
      
      # add resolved module in registry
      self.registry.add_module(module)

      # make path currently analyzing
      analyzing_paths.add(path)

      # search dependencies
      for dependency in dependencies:
        search(dependency)

      # make path analyzed
      analyzing_paths.remove(path)
      analyzed_paths.add(path)

    # start search from entry point
    search(entrypoint)

  # Step 2: Topological sort of modules graph
  # this method sorts modules in place and returns the sorted list
  def sort_modules(self) -> list[Module]:
    self.registry.sort_topologically()
    return self.registry.get_modules()
  


  # PATH resolution

  # allows to get absolute path of dependency module
  # base_path represents the ABSOLUTE path of dependent module (importer)
  # path represents the RELATIVE path to dependency module (exporter)
  # aliases are resolved in this method
  def resolve_absolute_path(self, base_path: str, path: str) -> str:
    base_directory = os.path.dirname(base_path)

    # resolve alias path
    if path.startswith(ALIAS_SYMBOL):
      # flag that indicates if alias is resolved
      resolved = False

      # check all aliases
      for alias, full in self.aliases.items():
        # resolve matched alias
        if path.startswith(f'{ALIAS_SYMBOL}{alias}'):
          dependency_path = re.sub(f"^{ALIAS_SYMBOL}{alias}", full, path)
          resolved = True
          break 

      if not resolved:
        raise ResolutionError(f'Undefined alias is used: {path}')
          
    # handle default path
    else:
      dependency_path = os.path.join(base_directory, path)
    
    # returns resolved absolute path without symbolic links
    return os.path.realpath(dependency_path)



  # COMMON module resolution

  # receives resolved ABSOLUTE path
  # based on specific module type methods
  def get_module_by_absolute_path(self, path: str) -> Module:
    # do not parse module if it is already parsed
    if self.registry.is_module_added_by_path(path):
      return self.registry.get_module_by_absolute_path(path)

    # check if source module    
    if path.endswith(f'.{SOURCE_MODULE_EXTENSION}'):
      return self.get_source_module_by_absolute_path(path)
    
    # check if external module
    if path.endswith(f'.{EXTERNAL_MODULE_EXTENSION}'):
      return self.get_external_module_by_absolute_path(path)
    
    raise ModuleError('Invalid module extension')

  # returns dependency absolute paths
  # based on specific module type methods
  def get_module_dependency_paths(self, module: Module) -> list[str]:
    if is_module_of_type(module, SourceModule):
      return self.get_source_module_dependency_paths(module)
    if is_module_of_type(module, ExternalModule):
      return self.get_external_module_dependency_paths(module)

    raise ModuleError('Cannot get dependencies of invalid module')



  # EXTERNAL module resolution

  def get_external_module_by_absolute_path(self, path: str) -> ExternalModule:
    # check for absolute path
    if not os.path.isabs(path):
      raise PathError(f"Absolute path expected. Received {path}")

    # check it to lead to a file
    if not os.path.isfile(path):
      raise ModuleError(f"Invalid module path. Received {path}")

    # check extension
    if not path.endswith(f'.{EXTERNAL_MODULE_EXTENSION}'):
      raise ModuleError(f"Invalid external module extension. Received {path}")

    # generate a unique module name from the path
    module_name = re.sub(r'\W+', '_', path)

    # dynamically load the external Python module
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
      raise ModuleError(f"Cannot load external module: {path}")

    # execute module
    module = importlib.util.module_from_spec(spec)
    try:
      spec.loader.exec_module(module)
    except Exception as e:
      raise ModuleError(f"Failed to execute external module at {path}: {e}")

    # search for a class that extends ExternalModule
    for _, obj in inspect.getmembers(module, inspect.isclass):
      if issubclass(obj, ExternalModule) and obj is not ExternalModule:
        try:
          # instantiate the class with required path
          instance = obj(path)

          return instance
        except Exception as e:
          raise ModuleError(f"Failed to instantiate ExternalModule class in {path}: {e}")

    raise ModuleError(f"No class extending ExternalModule found in {path}")

  # returns list of dependency absolute paths
  # does not return duplicated dependencies
  def get_external_module_dependency_paths(self, module: ExternalModule) -> list[str]:
    dependencies = set()

    # dependency is relative path (str)
    for dependency in module.dependencies:
      absolute_path = self.resolve_absolute_path(module.path, dependency)
      dependencies.add(absolute_path)

    return list(dependencies)



  # SOURCE module resolution

  # receives the ABSOLUTE path 
  # returns SourceModule instance
  # does NOT parse dependencies
  def get_source_module_by_absolute_path(self, path: str) -> SourceModule:
    # get file content
    content = self.read_source_module_by_absolute_path(path)

    # parse module content
    tokens = self.lexer.parse(content)
    ast = self.parser.parse(tokens)

    # return parsed module
    # leave dependencies as empty list until they are parsed
    return SourceModule(path, [], ast)    

  # returns list of dependency absolute paths 
  # does not return duplicated dependencies
  # based on IMPORT statements
  def get_source_module_dependency_paths(self, module: SourceModule) -> list[str]:
    # extract statements from module
    statements = module.content.statements

    # dependency paths set to prevent duplicates
    dependencies = set()

    # get import statements
    # check only first-level statements
    for statement in statements:
      # filter import statements
      if is_statement_of_class(statement, ImportStatement):
        # statement: ImportStatement 
        # -> .path: Token 
        path_token: Token = statement.path

        # check token to be string literal
        if not is_token_of_type(path_token, STRING_TOKEN):
          raise PathError(f'Import path has to be string literal. Received {path_token.code}')

        # resolve dependency ABSOLUTE path
        relative_path = path_token.code
        absolute_path = self.resolve_absolute_path(module.path, relative_path)

        # add module
        dependencies.add(absolute_path)

    # return dependency paths list
    return list(dependencies)

  # get source module content (str) by ABSOLUTE path
  def read_source_module_by_absolute_path(self, path: str) -> str:
    # check for path to be ABSOLUTE
    if not os.path.isabs(path):
      raise PathError(f"Absolute path expected. Received {path}")
    
    # check for correct file
    if not os.path.isfile(path):
      raise ModuleError(f"Invalid module path. Received {path}")
    
    # check file extension
    if not path.endswith(f'.{SOURCE_MODULE_EXTENSION}'):
      raise ModuleError(f'Invalid module extension. Received {path}')
    
    # read file content
    with open(path, "r", encoding="utf-8") as file:
      return file.read()
