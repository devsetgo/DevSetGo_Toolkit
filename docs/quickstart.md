# Quick Start

## Installation

Install the current code from the Github repo
```bash
pip install git+https://github.com/devsetgo/DevSetGo_Toolkit.git@main
```

Install the development version (may not work or be stable)
```bash
pip install git+https://github.com/devsetgo/DevSetGo_Toolkit.git@development
```

## Use

### HTTP Codes GET Requests

Use GET Codes and create a custom list
```python
from devsetgo_toolkit import GET_CODES, generate_code_dict

# Print the default GET_CODES
print(GET_CODES)

# Now add an additional status code (418) to the list and generate a new dictionary
MY_CODES = generate_code_dict(GET_CODES + [418], description_only=False)
print(MY_CODES)
```

### Base Schema

```python
from base_schema import SchemaBase
from sqlalchemy import Column, Integer, String

class User(SchemaBase):
    __tablename__ = 'users'

    name = Column(String, index=True)
    age = Column(Integer)

```

```python
from devsetgo_toolkit import *

```

