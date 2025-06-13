# defines container wrapper for values
# name can be accessed directly
class Container:
  def __init__(self, name, value):
    self.name = name
    self.value = value

class ReadableContainer(Container):
  def __init__(self, name, value):
    super().__init__(name, value)

  def read(self):
    return self.value

class WriteableContainer(Container):
  def __init__(self, name, value):
    super().__init__(name, value)

  def write(self, value):
    self.value = value

# both readable and writeable
class TransformContainer(Container, ReadableContainer, WriteableContainer):
  def __init__(self, name, value):
    super().__init__(name, value)


def is_container_of_type(container, *types: Container):
  return container in types
