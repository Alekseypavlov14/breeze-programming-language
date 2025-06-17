# Interpreter

This class runs topologically sorted list of modules consecutively. The instance object has list of **modules** and **stacks** corresponding to them. 

## Stacks 

Stack is a class that controls variables, constants and declarations created in application.
The object of this class has a list of **Scopes** and each scope has a list of **Containers**. Container represents the unit of value and can be **readable**, **writable** and **transform** (both). 

Scopes are created and deleted (removed from list) during the application execution. 

Stack has a ```.copy()``` method that copies the list of scopes with **shallow copy** and saves the references to **containers**. This is extremely important for **function closures**. Closure variables can be modified through stack if the corresponding scope is available.

# Logic of consecutive execution

Each module is executed with its own stack and then the pointer to current module and current stack is changed. Stacks **are saved** after module is executed.

# Module execution

Module is executed recursively by executing statements and evaluating expressions. **Containers** are returned as a result of expressions evaluation.

Expression evaluation generates **Container** (without name) and these containers are passed in **expression evaluation tree**. 
