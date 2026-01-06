from typing import Optional
from pythongpt import implement, config

log = True
debug = False

@implement
def hello_world() -> None:
    """Prints "Hello World!" in german."""
    return config(model="gpt-4o-mini", log=log, debug=debug)

hello_world()

@implement
def mean(ls: list[float]) -> float:
    """Returns the mean of a list of floats."""
    return config(tests=["mean([1,2,3]) == 2.0"], log=log, debug=debug)

print(mean([0,5,10]))

@implement
def variance(ls: list[float]) -> float:
    """Returns the variance of a function."""
    return config(
        functions=[mean],
        tests=[
            "variance([]) == 0",
            "variance([1]) == 0",
            "abs(variance([1,2]) - 0.25) <= 1e-9",
            "abs(variance([1,2,3]) - 2/3) <= 1e-9"
        ],
        log=log,
        debug=debug
    )

print(variance([1,2,3,4]))

@implement
def binary_search(ls: list[int], el: int) -> Optional[int]:
    """Finds the index of int el in the sorted list ls in log(|ls|) steps if it is contained in ls."""
    return config(tests=["binary_search([1,2,5,8],5) == 2"], log=log, debug=debug)

print(binary_search(list(range(100000)), 10))

def check_github_url(url: str) -> bool:
    """Returns true if the given url is a valid GitHub url, else returns False"""
    return "github.com" in url

@implement
def get_github_url(package_name: str) -> Optional[int]:
    """Gets the GitHub URL of an npm package if it has one."""
    sketch = f"""
    # Use a shell to run npm view
    # Parse the npm view result, and extract the url
    return url if check_github_url(url) else None
    """
    return config(
        sketch=sketch,
        functions=[check_github_url],
        tests=["'IonicaBizau/abs' in get_github_url('abs')"],
        log=log,
        debug=debug
    )

print(get_github_url("lodash"))