# Development Guide

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Development Guide](#development-guide)
  - [Contribution](#contribution)
  - [Naming convention](#naming-convention)
  - [Build for distribution](#build-for-distribution)
  - [Future plan](#future-plan)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Contribution
Any contribution is welcome! 

**But please fire an issue before you start working on it.** 
This is to avoid duplicated work and make sure the changes are necessary.

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
# build fronted
cd lires_web && npm install && npm run build && cd ..

# fetch third party libs
lrs-utils update_pdfjs

# build for distribution
python setup.py sdist
```


## Future plan

The current version mainly focus on the core features including data storage, user management, and basic data visualization.

In my plan, the next step is to optimize for large data sets, and add more features for collaboration between users, 
as these are the key features that really leverages the power of the server-side library.
- [ ] Move all data filtering to backend; frontend use partial async data loading to optimize bandwidth and rendering speed.
- [ ] Add a discussion board, anyone can post a topic and discuss with others, the topic can be linked to a paper or a tag. The data can be stored in the user database as table `posts`, and refer to the paper by id. 
- [ ] Record user activities, e.g. who added/edited/removed a tag/note/paper, the reading history of a paper, etc. The data can be stored in the user database as table `activities`.


<details>
<summary>Finished</summary>

- [x] Long connection between the server and the client, so that the client can receive notifications when there are new activities. This may be done by using [Websocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) or [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events).

</details>