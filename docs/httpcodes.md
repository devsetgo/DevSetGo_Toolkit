# HTTP Response Codes

This Python file defines a dictionary of HTTP error codes and their respective descriptions. The dictionary provides a mapping between HTTP error codes and their description strings, which can be used to define or handle custom error responses for an API.

The file also includes the function `generate_code_dict(codes, description_only=False)`, which generates a dictionary of specific HTTP error codes from the `http_codes` dictionary.

## Usage

You can use this file in the following ways:

### Using the `http_codes` Dictionary

Access any HTTP code's information as follows:

```python
# Accessing the "OK" status code
http_codes[200]
```

This will output:

```python
{
    "description": "OK",
    "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200"
}
```

### Using the `generate_code_dict` Function

Generate a dictionary of specific HTTP error codes as follows:

```python
# Define a list of common HTTP status codes
common_codes = [200, 400, 401, 403, 404, 408, 429, 500, 503]

# Generate a dictionary of these status codes with their descriptions
MY_CODES = generate_code_dict(common_codes + [206, 304, 307, 410, 418, 502], description_only=True)
```

This will return a dictionary where each key is an HTTP error code from the input list and each value is the corresponding description.

## Generating Common Error Codes for Different Request Methods

Use the `generate_code_dict` function to generate dictionaries of common error codes for different request methods:

### GET Requests

```python
from devsetgo_toolkit import GET_CODES

# Print the default GET_CODES
print(GET_CODES)

# Now add an additional status code (418) to the list and generate a new dictionary
MY_CODES = generate_code_dict(GET_CODES + [418], description_only=False)
print(MY_CODES)
```

### POST Requests

```python
from devsetgo_toolkit import POST_CODES

# Print the default POST_CODES
print(POST_CODES)

# Add an additional status code (418) to the list and generate a new dictionary
MY_CODES = generate_code_dict(POST_CODES + [418], description_only=False)
print(MY_CODES)
```

### PUT Requests

```python
from devsetgo_toolkit import PUT_CODES

# Print the default PUT_CODES
print(PUT_CODES)

# Add an additional status code (418) to the list and generate a new dictionary
MY_CODES = generate_code_dict(PUT_CODES + [418], description_only=False)
print(MY_CODES)
```

### PATCH Requests

```python
from devsetgo_toolkit import PATCH_CODES

# Print the default PATCH_CODES
print(PATCH_CODES)

# Add an additional status code (418) to the list and generate a new dictionary
MY_CODES = generate_code_dict(PATCH_CODES + [418], description_only=False)
print(MY_CODES)
```

### DELETE Requests

```python
from devsetgo_toolkit import DELETE_CODES

# Print the default DELETE_CODES
print(DELETE_CODES)

# Add an additional status code (418) to the list and generate a new dictionary
MY_CODES = generate_code_dict(DELETE_CODES + [418], description_only=False)
print(MY_CODES)
```

These dictionaries can be used to define HTTP error codes commonly encountered with each type of request method in an API.