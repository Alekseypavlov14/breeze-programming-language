from interpreter.containers import *
from interpreter.exceptions import *

# define module exports
# Use ony instance for one module
# encapsulates containers list
# raises NameError on duplicates
class Exports:
  def __init__(self):
    self.containers: list[Container] = []

  def add_container(self, container: Container):
    if self.is_container_added(container.name):
      raise NameError('This name is already in exports list')
    
    self.containers.append(container)

  def is_container_added(self, name: str):
    return bool(self.get_container_by_name(name))

  def get_container_by_name(self, name: str):
    for container in self.containers:
      if container.name == name:
        return container
      
    return None