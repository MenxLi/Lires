# Development Guide


## Principles
**Keep it simple and maintainable**

Simple:
- Always present easy-to-use user interface
- Adding features for common use cases
- Minimal dependencies for each module

Maintainable:
- **Use type annotations whenever possible**
- Modularized & well documented.
- Isolate the logic, from the UI
- Abstract common logics and reduce code duplication
- Module isolation, expose only the necessary interfaces (use `_protected` and `__private` for internal use)
- Not afraid of refactoring, but do it gradually and carefully

## Naming convention
**Python**

Alough [PEP-8](https://peps.python.org/pep-0008/#function-and-variable-names) suggests use `lower_case_with_underscores` for methods and functions...  

By my personal preference, I use the following naming rules: 
- `snake_case` (Lowercase / Lower case with underscore) for variables, properties
- `lowerCamelCase` (Mixed case) for functions, methods
- `UpperCamelCase` (Pascal case) for classes

**Please follow this style if you are working on this repository**, these naming makes it very clear to distinguish between different types of code.

**Javascript**   

I follow Javascript naming convention, which is:
- `lowerCamelCase` for variables, properties, functions and methods.
- `UpperCamelCase` for classes.

**Http path**  

use `lowercase-with-dash` for http path, e.g. `/api/v1/your-path`