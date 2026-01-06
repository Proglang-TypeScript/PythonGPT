# PythonGPT

PythonGPT is a Python library that lets you program using natural language in Python.

## Demo

```python
from pythongpt import implement, config

@implement
def mean(ls: list[float]) -> float:
    """Returns the mean of a list of floats."""
    return config(tests=["mean([1,2,3]) == 2.0"])

print(mean([1,2,3]))  # prints 2.0
```

More examples can be found in `./pythongpt/__main__.py`

## Setup

`SETUP.md` contains all the setup instructions.

## Manual

PythonGPT implements functions by using OpenAI's large language models (LLMs). It does this by prompting an LLM with the signature and doc-string of a given function and letting the LLM suggest an implementation that fits this specification.

The basic use-case is to simply add the `@implement` decorator to a given function declaration and letting that function return `config()` which can contain additional configuration information for the implementation. Subsequently at run-time, the function will be implemented and the implementation conversation will be cached for next time.

### `Config`

`config(...)` will return a `Config` object which configures the implementation of a given function. The available parameters are:
- `model (str)`: The specific OpenAI model that should be used
- `sketch (str)`: A sketch of how the function implementation should look like
- `functions (list[Callable])`: A list of helper functions that the function implementation may use without defining them
- `tests (list[str])`: A list of test statements that will be evaluated on the generated implementation
- `max_attempts (Optional[int])`: The maximum number of attempts that the LLM gets for generating the implementation such that it is error free and passes all tests
- `log (bool)`: Whether to print the interactions with the LLM
- `debug (bool)`: Whether to wait between prompts for user input