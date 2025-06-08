from interpreter.containers import *
from interpreter.exceptions import *

# defines the environment Stack 
# contains list of Scopes
class Stack:
  def __init__(self):
    self.scopes: list[Scope] = []

  def add_scope(self):
    self.scopes.append(Scope)

  def remove_scope(self):
    self.scopes.pop()

  # adds container to last scope
  def add_container(self, container):
    if not len(self.scopes):
      raise StackError('No scopes available!')

    self.scopes[len(self.scopes) - 1].add_container(container)

  # gets container searching from last to first scope
  def get_container_by_name(self, name):
    if not len(self.scopes):
      raise StackError('No scopes available!')

    reversed_scopes = self.scopes.copy()
    reversed_scopes.reverse()

    for scope in reversed_scopes:
      container, found = scope.get_container_by_name(name)

      if found: 
        return container

    raise NameError(f'{name} is not found!')
  
  # deletes container searching from last to first scope
  def remove_container_by_name(self, name):
    if not len(self.scopes):
      raise StackError('No scopes available!')

    reversed_scopes = self.scopes.copy()
    reversed_scopes.reverse()

    for scope in reversed_scopes:
      is_deleted = scope.remove_container_by_name(name)

      if is_deleted: 
        return
      
    raise NameError(f'{name} is not found!')

# defines the Scope (slice of stack)
# Scope stores containers with values
# Provides methods to add, get and delete containers
class Scope:
  def __init__(self):
    self.containers: list[Container] = []

  def add_container(self, container):
    self.containers.append(container)

  # returns tuple with container|None and boolean indicating if the container is found
  def get_container_by_name(self, name):
    for container in self.containers:
      if container.name == name:
        return (container, True)
      
    return (None, False)

  # returns boolean indicating if container was deleted
  def remove_container_by_name(self, name):
    rest_containers = []
    is_deleted = False

    for container in self.containers:
      if container.name != name:
        rest_containers.append(container)
      else:
        is_deleted = True

    self.containers = rest_containers
    return is_deleted
