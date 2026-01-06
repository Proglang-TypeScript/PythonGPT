from dataclasses import dataclass
import importlib
import traceback
from typing import Any, Callable, Optional

from easy_prompting.prebuilt import GPT, PrintLogger, PrintDebugger, Prompter, list_text, pad_text, CodeInstr, delimit_code
from pythongpt.utils import create_file, dummy_call, get_meta_data, trim_text, wrap, cache_path

@dataclass
class Config:
    model: str
    sketch: str
    functions: list[Callable]
    tests: list[str]
    max_attempts: Optional[int]
    log: bool
    debug: bool

def config(
    model: str = "gpt-5-nano",
    sketch: str = "# Todo",
    functions: Optional[list[Callable]] = None,
    tests: Optional[list[str]] = None,
    max_attempts: int = 5,
    log: bool = True,
    debug: bool = False,
) -> Any:
    functions = [] if functions is None else functions
    tests = [] if tests is None else tests
    return Config(model, sketch, functions, tests, max_attempts, log, debug)

class ImplementationError(Exception):
    pass

class Implementer:
    def __init__(self, function: Callable, config: Config):
        self.function = function
        self.config = config
    
    def implement(self) -> Callable:
        function, config = self.function, self.config
        name, signature, doc = get_meta_data(function)
        logger = PrintLogger()
        logger.set_verbose(config.log or config.debug)
        with logger:
            implementor = Prompter(GPT(config.model))
            implementor.set_tag(f"implementor ({name})")
            implementor.set_cache(cache_path / "completions" / config.model)
            implementor.set_logger(logger)
            if config.debug:
                implementor.set_debugger(PrintDebugger())
            implementor.add_message(
                list_text(
                    f"You are an autonomous agent and a Python expert.",
                    f"The user is a program that can only interact with you in predetermined ways.",
                    f"Follow the instructions of the user"
                ),
                role="developer"
            )
            implementor.add_message(
                f"Please help me implement the following function:\n"
                + delimit_code(
                    f"def {signature}:"
                    + pad_text(
                        f"\n\"\"\"{trim_text(doc)}\"\"\""
                        f"\n{trim_text(config.sketch)}",
                        "    "
                    ),
                    f"python"
                )
                + f"\nOnly use Python's standard library unless stated otherwise."
            )
            if config.functions:
                message = [f"You may use the following helper functions without defining them, I will add their definitions later:"]
                for function_ in config.functions:
                    name_, signature_, doc_ = get_meta_data(function_)
                    message.append(
                        delimit_code(
                            f"def {signature_}:"
                            + pad_text(
                                f"\n\"\"\"{trim_text(doc_)}\"\"\""
                                f"\n...",
                                "    "
                            ),
                            f"python"
                        )
                    )
                implementor.add_message("\n".join(message))
            attempt = 0
            while True:
                attempt += 1
                if config.max_attempts is not None and attempt > config.max_attempts:
                    raise ImplementationError(f"Agent failed to implement function {name!r} in {config.max_attempts} attempts")
                code = implementor.get_data(
                    CodeInstr(
                        f"Write the function implementation, including imports and anything else that might be needed to define the function.",
                        "python"
                    )
                )
                file_path = cache_path / "implementations" / f"{name}.py"
                create_file(file_path, content=code)
                try:
                    spec = importlib.util.spec_from_file_location(name, file_path) # type:ignore
                    module = importlib.util.module_from_spec(spec)  # type:ignore
                    spec.loader.exec_module(module)
                except Exception as e:
                    trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
                    implementor.add_message(f"Your implementation caused a syntax error:\n{trace}")
                    continue
                if not hasattr(module, name):
                    implementor.add_message(f"Your implementation does not contain a top level function called \"{name}\"")
                    continue
                for function_ in config.functions:
                    name_ = get_meta_data(function_)[0]
                    setattr(module, name_, function_)
                implementation: Callable = wrap(function)(getattr(module, name))
                errors = []
                for test in config.tests:
                    assertion = f"assert {test}, 'assertion failed'"
                    try:
                        exec(assertion, locals={name: implementation})
                    except Exception as e:
                        errors.append(f"{assertion!r} should pass, but your implementation caused the error: {e}")
                if errors:
                    implementor.add_message(list_text(*errors))
                    continue
                break
            return implementation

def implement(function: Callable) -> Callable:
    config = dummy_call(function)
    assert isinstance(config, Config), "Function needs to return a implementation config object for generating an implementation."
    return Implementer(function, config).implement()