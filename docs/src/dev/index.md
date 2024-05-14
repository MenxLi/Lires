# Development Guide

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Development Guide](#development-guide)
  - [Contribution](#contribution)
  - [Naming convention](#naming-convention)
  - [Build for distribution](#build-for-distribution)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Contribution
Any contribution is welcome! 
**But please fire an issue before you start working on it.** 

The principle is to **Keep this project simple and maintainable**:
- **Use type annotations whenever possible**
- Adding features for common use cases
- Minimal dependencies for each module

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

## Build for distribution
Please run the following commands to build for the distribution:
```bash
# build necessary files
make build

# fetch third party libs
lrs-utils update_pdfjs

# build for distribution
python setup.py sdist
```

