# Standard Library and External Modules

Breeze Programming Language supports **python** modules loading and execution if they follow the requirement.

For Python module to be Breeze external module, it has to contain **ExternalModule** class definition.

## ExternalModule

This class defines common interface for external module written in Python. To be an external module, derived class has to define **dependencies** (relative paths list) and **declarations** list. **declarations** are special classes that can be executed by **Interpreter** with declaring entities in runtime. 

Path of the module, dependencies and declarations have to be passed as parameter through **__init__** function to ```super().__init__()```. 

If Python module follows all the requirements, it can be used as dependency for ```.br``` modules.

**Standard Library** of Breeze Programming Language is built on external modules.

## Applications

Python libraries can be used in **Breeze** after creating a **Breeze** wrapper!
