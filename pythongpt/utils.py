import inspect
from pathlib import Path
import shutil
from typing import Callable, Any, Optional

def get_meta_data(function: Callable) -> tuple[str, str, str]:
    name = function.__name__
    signature = f"{name}{inspect.signature(function)}"
    spec = function.__doc__ if function.__doc__ else ""
    spec = "\n".join(line.strip() for line in spec.strip().split("\n"))
    return name, signature, spec

def trim_text(text: str) -> str:
    lines = text.split("\n")
    index = 0
    offset = None
    for line in lines:
        if line.strip():
            offset = len(line) - len(line.lstrip())
            break
        index += 1
    if offset is None:
        return ""
    lines = [line[offset:] for line in lines[index:]]
    index = 0
    for line in lines[::-1]:
        if line.strip():
            return "\n".join(lines[:len(lines)-index])
        index += 1
    assert False, "Unreachable code"

def dummy_call(function: Callable) -> Any:
    params = inspect.signature(function).parameters
    args: list[Any] = []
    kwargs: dict[str, Any]= {}
    for name, param in params.items():
        if param.default == inspect.Parameter.empty:
            if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                args.append(None)
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                kwargs[name] = None
    return function(*args, **kwargs)#

def wrap(wrapped: Callable) -> Callable:
    def decorator(wrapper: Callable) -> Callable:
        for attr in ("__name__", "__qualname__", "__module__", "__doc__", "__defaults__", "__annotations__"):
            if hasattr(wrapped, attr):
                setattr(wrapper, attr, getattr(wrapped, attr))
        return wrapper
    return decorator

def create_dir(dst_path: Path, src_path: Optional[Path] = None, overwrite: bool = False) -> None:
    if overwrite:
        shutil.rmtree(dst_path, ignore_errors=True)
    if src_path is None:
        dst_path.mkdir(parents=True, exist_ok=True)
    else:
        shutil.copytree(src_path, dst_path, dirs_exist_ok=True, symlinks=True)

def create_file(dst_path: Path, src_path: Optional[Path] = None, content: Optional[str] = None) -> None:
    create_dir(dst_path.parent)
    if src_path is None:
        dst_path.write_text("" if content is None else content)
    else:
        dst_path.write_text(src_path.read_text())

cache_path = Path("__pythongpt_cache__")