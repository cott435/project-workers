---
name: python-style-guide
description: How to write the code inside a Python file — imports, exceptions, type annotations, docstrings, naming, strings, and modern language features, based on Google's Python Style Guide. Preloaded into the implementer and reviewer; invoke directly when you need a specific pattern. Structure and file placement are owned by project-structure.
license: Google Python Style Guide, CC BY 3.0. Complete terms in LICENSE.
---

# Python Style Guide

Comprehensive guidelines for writing clean, maintainable Python code based on [Google's Python Style Guide](https://google.github.io/styleguide/pyguide.html).

## Scope

This file governs what goes **inside** a Python file. Where files go, how big they get before
splitting, config placement, and module naming belong to `project-structure`; the mechanics of a
split belong to `python-implementation`. Nothing is stated in both places. Three sections here
are marked *Project convention* — docstring requirements, function shape, and `__init__.py`
policy — because they go beyond or beside what Google's guide says.

Detailed patterns live in `references/` and load only when read:

- `references/docstring_examples.md` — docstrings for every construct
- `references/advanced_types.md` — `Protocol`, `TypedDict`, `Literal`, `ParamSpec`, generics
- `references/antipatterns.md` — common mistakes and their fixes

## Core Philosophy

**BE CONSISTENT.** Match the style of the code around you. These are defaults; consistency with
the surrounding code beats any external guide, including this one.

## Language Rules

### Imports

Use `import` statements for packages and modules in application code to avoid circular dependencies. For standard library and third-party packages, importing classes is acceptable.

**Yes:**
```python
from pydantic import BaseModel  # Third-party: Class import OK
from pathlib import Path        # Stdlib: Class import OK
import sound_effects.utils      # App: Module import
from myproject import config    # App: Module import
```

**No:**
```python
from myproject.utils import heavy_function  # App: Avoid direct function import if circular dep risk
```

#### Import Formatting

- Group imports: standard library, third-party, application-specific
- Alphabetize within each group
- Use absolute imports (not relative imports)
- One import per line (except for multiple items from `typing` or `collections.abc`)

```python
# Standard library
import os
import sys

# Third-party
import numpy as np
import tensorflow as tf

# Application-specific
from myproject.backend import api_utils
```

### Exceptions

Use exceptions appropriately. Do not suppress errors with bare `except:` clauses.

**Yes:**
```python
try:
    result = risky_operation()
except ValueError as e:
    logging.error(f"Invalid value: {e}")
    raise
```

**No:**
```python
try:
    result = risky_operation()
except:  # Too broad, hides bugs
    pass
```

### Type Annotations

Annotate all function signatures. Type annotations improve code readability and catch errors early.

**General rules:**
- Annotate all public APIs
- Use built-in types (`list`, `dict`, `set`) instead of `typing.List`, etc. (Python 3.9+)
- Import typing symbols directly: `from typing import Any, Union`
- Use `None` instead of `type(None)` or `NoneType`

```python
def fetch_data(url: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch data from URL."""
    ...

def process_items(items: list[str]) -> None:
    """Process a list of items."""
    ...
```

### Default Argument Values

Never use mutable objects as default values in function definitions.

**Yes:**
```python
def foo(a: int, b: list[int] | None = None) -> None:
    if b is None:
        b = []
```

**No:**
```python
def foo(a: int, b: list[int] = []) -> None:  # Mutable default - WRONG!
    b.append(a)
```

### True/False Evaluations

Use implicit false where possible. Empty sequences, `None`, and `0` are false in boolean contexts.

**Yes:**
```python
if not users:  # Preferred
if not some_dict:
if value:
```

**No:**
```python
if len(users) == 0:  # Verbose
if users == []:
if value == True:  # Never compare to True/False explicitly
```

### Comprehensions & Generators

Use comprehensions and generators for simple cases. Keep them readable.

**Yes:**
```python
result = [x for x in data if x > 0]
squares = (x**2 for x in range(10))
```

**No:**
```python
# Too complex
result = [
    x.strip().lower() for x in data 
    if x and len(x) > 5 and not x.startswith('#')
    for y in x.split(',') if y
]  # Use a regular loop instead
```

### Lambda Functions

Use lambdas for one-liners only. For anything complex, define a proper function.

**Yes:**
```python
sorted(data, key=lambda x: x.timestamp)
```

**Acceptable but prefer named function:**
```python
def get_timestamp(item):
    return item.timestamp

sorted(data, key=get_timestamp)
```

## Style Rules

### Line Length

Maximum line length: 88 characters. Exceptions allowed for imports, URLs, and long strings that can't be broken.

### Indentation

Use 4 spaces per indentation level. Never use tabs.

For hanging indents, align wrapped elements vertically or use 4-space hanging indent:

```python
# Aligned with opening delimiter
foo = long_function_name(var_one, var_two,
                         var_three, var_four)

# Hanging indent (4 spaces)
foo = long_function_name(
    var_one, var_two, var_three,
    var_four)
```

### Blank Lines

- Two blank lines between top-level definitions
- One blank line between method definitions
- Use blank lines sparingly within functions to show logical sections

### Naming Conventions

Naming *inside* a file. Module, package, and test-file naming is owned by
`project-structure` §4.

| Type | Convention | Examples |
|------|-----------|----------|
| Classes | `CapWords` | `MyClass` |
| Functions/Methods | `lower_with_under()` | `my_function()` |
| Constants | `CAPS_WITH_UNDER` | `MAX_SIZE` |
| Variables | `lower_with_under` | `my_var` |
| Private | `_leading_underscore` | `_private_var` |

**Avoid:**
- Single character names except for counters/iterators (`i`, `j`, `k`)
- Dashes in any name
- `__double_leading_and_trailing_underscore__` (reserved for Python)

### Comments and Docstrings

#### Docstring requirements

> Project convention. Google's guide requires docstrings on public APIs; this project requires
> them everywhere, because the docs site is built from them and a missing one is a hole in the
> rendered reference.

**Every module, class, function, and method has a docstring**, Google style. A private helper
(`_name`) may be a single summary line; everything public gets the full shape below.

- **Module** — a summary line, then a short paragraph on what the module owns and its entry
  points. This becomes the page header in the rendered site, so write it for a reader who
  arrived from the navigation, not from the code.
- **Class** — summary, description, `Attributes:`. Constructor parameters are documented on
  `__init__`; the site merges them into the class page.
- **Function or method** — an imperative summary line ("Fetch rows…", not "This fetches…");
  `Args:` *without* types, since annotations carry them; `Returns:` or `Yields:`; `Raises:`;
  and, on public entry points, an `Examples:` block in doctest form so
  `pytest --doctest-modules` can execute it.
- **CLI commands** — a command is a function in `cli.py` whose parameters are its arguments
  and whose docstring is its help. The summary line says what the command does; `Args:` names
  every parameter as the user will type it (`--start`, not `start`) with its meaning, unit, and
  default when the default is not obvious from the signature. With `cyclopts` that docstring
  *is* the `--help` text, and mkdocstrings renders the same thing on the docs site, so a bare
  `"""Run the download."""` leaves the user with an argument list and no idea what to pass.
  The `cli.py` module docstring lists the commands, one line of usage each.
- **Cross-references** — when the thing you name has a page, link it in the renderer's syntax
  rather than bare backticks. The repo's renderer is stated in `docs/architecture.md`
  (Toolchain); the default is MkDocs + mkdocstrings, whose syntax is
  `` [`load_bars`][data.ingest.loaders.load_bars] `` or `[data.ingest.loaders.load_bars][]`.
  A repo on Sphinx uses `` :func:`data.ingest.loaders.load_bars` `` instead.

The docs build runs in CI with warnings as errors (`mkdocs build --strict`). An unresolved
reference or a malformed section fails the build — that is how docstring rot gets caught, and
it is the only reason the generated site matters to this workflow. Agents never read the
generated HTML; they read the curated `interface.md` and section READMEs.

#### Docstring Format

**Function docstring:**
```python
def fetch_smalltable_rows(
    table_handle: smalltable.Table,
    keys: Sequence[bytes | str],
    require_all_keys: bool = False,
) -> Mapping[bytes, tuple[str, ...]]:
    """Fetches rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle. String keys will be UTF-8 encoded.

    Args:
        table_handle: An open smalltable.Table instance.
        keys: A sequence of strings representing the key of each table
            row to fetch. String keys will be UTF-8 encoded.
        require_all_keys: If True, raise ValueError if any key is missing.

    Returns:
        A dict mapping keys to the corresponding table row data
        fetched. Each row is represented as a tuple of strings.

    Raises:
        IOError: An error occurred accessing the smalltable.
        ValueError: A key is missing and require_all_keys is True.
    """
    ...
```

**Class docstring:**
```python
class SampleClass:
    """Summary of class here.

    Longer class information...
    Longer class information...

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """

    def __init__(self, likes_spam: bool = False):
        """Initializes the instance based on spam preference.

        Args:
            likes_spam: Defines if instance exhibits this preference.
        """
        self.likes_spam = likes_spam
        self.eggs = 0
```

#### Block and Inline Comments

- Use complete sentences with proper capitalization
- Block comments indent to the same level as the code
- Inline comments should be separated by at least 2 spaces
- Use inline comments sparingly

```python
# Block comment explaining the following code.
# Can span multiple lines.
x = x + 1  # Inline comment (use sparingly)
```

### Strings

Use f-strings for formatting (Python 3.6+).

**Yes:**
```python
x = f"name: {name}; score: {score}"
```

**Acceptable:**
```python
x = "name: %s; score: %d" % (name, score)
x = "name: {}; score: {}".format(name, score)
```

**No:**
```python
x = "name: " + name + "; score: " + str(score)  # Avoid + for formatting
```

#### Logging

Use **Loguru** for logging with brace-style lazy formatting:

```python
logger.info("Request from {} resulted in {}", ip_address, status_code)
```

**Avoid** standard `logging` with `%` formatting.

### Files and Resources

For simple text operations, prefer `pathlib` methods:

```python
data = Path("file.txt").read_text()
Path("output.txt").write_text("content")
```

For complex operations or non-text files, use context managers:

```python
with open("image.png", "rb") as f:
    data = f.read()
```

### Statements

Generally avoid multiple statements on one line.

**Yes:**
```python
if foo:
    bar()
```

**No:**
```python
if foo: bar()  # Avoid
```

### Main

For executable scripts, use:

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

### Function shape

> Project convention. The goal is a main path a reader can follow top to bottom without
> losing the thread — not the smallest possible functions, and not the fewest.

- **One job, one level of abstraction.** A function may have several phases — validate, fetch,
  reshape — and that is fine. Each phase, and each loop whose purpose is not obvious from its
  first line, gets a one-line comment naming what it is *for*, not what the next statement
  does:

  ```python
  # Drop bars outside the session so the resample does not bridge the overnight gap.
  for symbol, frame in bars.groupby("symbol"):
      ...
  ```

- **Extract a phase into its own function only when the jump buys something.** It does when at
  least one holds:
  - the phase is reused;
  - it is I/O — network, database, file — mixed with a pure transformation: split so the
    transformation is testable without the I/O;
  - it is a retry loop or error handling wrapped around business logic: extract the wrapper
    or a decorator, so the logic reads without the plumbing;
  - it needs its own docstring to be understood — a name plus `Args:`/`Returns:` says more
    than the inline code would;
  - it is the seam that brings the parent under the soft statement limit.

- **Do not extract a single-use helper whose name merely restates a few lines of code.** Every
  helper costs the reader a jump. A helper that adds no name worth having is a net loss even
  if it makes the parent shorter.

- **The soft statement limit in `project-structure` §2 is the signal to look for a seam**, not
  a line to cut at. Past the hard limit you must split; between the two, split where the
  seams are and note the size in your return.

- **In a class, public methods come first, then private.** Once there are more than a handful
  of private methods, group them under banner comments so the structure scans at a glance,
  each helper placed after its first caller:

  ```python
      # --- symbol mapping ---

      def _resolve_symbol(self, raw: str) -> str: ...
      def _load_alias_table(self) -> dict[str, str]: ...

      # --- session filtering ---
  ```

- **The reviewer's test:** the main path reads top to bottom with at most one jump per phase,
  and no phase's purpose has to be inferred from its code.

### Function length and file size

Owned by `project-structure` §2, which ties the numbers to the ruff and pylint rules that
enforce them. Do not restate them here.

## Type Annotation Details

### Forward Declarations

Use string quotes for forward references:

```python
class MyClass:
    def method(self) -> "MyClass":
        return self
```

### Type Aliases

Create aliases for complex types:

```python
from typing import TypeAlias

ConnectionOptions: TypeAlias = dict[str, str]
Address: TypeAlias = tuple[str, int]
Server: TypeAlias = tuple[Address, ConnectionOptions]
```

### TypeVars

Use descriptive names for TypeVars:

```python
from typing import TypeVar

_T = TypeVar("_T")  # Good: private, unconstrained
AddableType = TypeVar("AddableType", int, float, str)  # Good: descriptive
```

### Generics

Always specify type parameters for generic types:

**Yes:**
```python
def get_names(employee_ids: list[int]) -> dict[int, str]:
    ...
```

**No:**
```python
def get_names(employee_ids: list) -> dict:  # Missing type parameters
    ...
```

### Imports for Typing

Import typing symbols directly:

```python
from collections.abc import Mapping, Sequence
from typing import Any, Union

# Use built-in types for containers (Python 3.9+)
def foo(items: list[str]) -> dict[str, int]:
    ...
```

## Modern Python Features

### Match Statements (Python 3.10+)

Use structural pattern matching for complex conditionals:

```python
def handle_response(response: dict) -> str:
    match response:
        case {"status": "ok", "data": data}:
            return f"Success: {data}"
        case {"status": "error", "message": msg}:
            return f"Error: {msg}"
        case {"status": status}:
            return f"Unknown status: {status}"
        case _:
            return "Invalid response"
```

Pattern matching with types:

```python
def process(value: int | str | list) -> str:
    match value:
        case int(n) if n > 0:
            return f"Positive int: {n}"
        case int(n):
            return f"Non-positive int: {n}"
        case str(s):
            return f"String: {s}"
        case [first, *rest]:
            return f"List starting with {first}"
```

### Dataclasses with Slots (Python 3.10+)

Use `slots=True` for memory efficiency and faster attribute access:

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: float
    y: float

@dataclass(slots=True, frozen=True)
class ImmutableConfig:
    host: str
    port: int
    timeout: float = 30.0
```

### Postponed Annotation Evaluation

Use `from __future__ import annotations` for:
- Forward references without quotes
- Faster module import (annotations not evaluated at definition time)

```python
from __future__ import annotations

class Node:
    def __init__(self, children: list[Node]) -> None:  # No quotes needed
        self.children = children

    def add_child(self, child: Node) -> None:
        self.children.append(child)
```

### Exception Groups (Python 3.11+)

Handle multiple exceptions simultaneously:

```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(task1())
        tg.create_task(task2())
except* ValueError as eg:
    for exc in eg.exceptions:
        logger.error("ValueError: {}", exc)
except* TypeError as eg:
    for exc in eg.exceptions:
        logger.error("TypeError: {}", exc)
```

## Common Patterns

### Properties

Use properties for simple attribute access:

```python
class Square:
    def __init__(self, side: float):
        self._side = side
    
    @property
    def area(self) -> float:
        return self._side ** 2
```

### Conditional Expressions

Use ternary operators for simple conditions:

```python
x = "yes" if condition else "no"
```

### Context Managers

Create custom context managers when appropriate:

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(*args, **kwargs):
    resource = acquire_resource(*args, **kwargs)
    try:
        yield resource
    finally:
        release_resource(resource)
```

## Linting

`ruff check` and `ruff format` are the gate. The thresholds live in `pyproject.toml` under
`[tool.ruff.lint]`, so the config rather than this file is the source of truth.

Suppress a warning only when the alternative is worse, and only with the specific code:

```python
dict = 'something'  # noqa: A001
```

A bare `# noqa` suppresses everything on the line, including the error you did not know was
there.

### Package `__init__.py` Files

> Project convention, not Google's. Google's style guide never mentions `__init__.py`; what it
> says is about call sites — import modules, not individual names. The rule below is this
> project's, chosen after weighing the two absolutes.

**The top-level `__init__.py` of a package exposes its public API — only the names a
consumer outside the package needs — lists them in `__all__`, and resolves them lazily. Every
nested `__init__.py` is empty.**

Lazily, because a stable surface should not cost anything to import: `import data` in a
consumer that only wants `Lot` must not load pandas for `load_bars`. PEP 562's module
`__getattr__` gives exactly that — the name resolves on first touch and is cached — while a
`TYPE_CHECKING` block keeps static analyzers, IDEs, and the docs build seeing ordinary imports.

```python
# src/data/__init__.py — written by /project-workers:finalize-package from docs/packages/data/surface.md
"""Market data: download, clean, audit, and store bars.

Public surface of the ``data`` package. Consumers import from here and nowhere deeper.
Names resolve lazily: importing ``data`` loads no section until a name is first used.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # real imports for type checkers and the docs build; never executed at runtime
    from data.ingest.loaders import load_bars
    from data.storage.models import Lot

__all__ = ["Lot", "load_bars"]

_EXPORTS = {  # public name → defining module; keep in sync with __all__
    "Lot": "data.storage.models",
    "load_bars": "data.ingest.loaders",
}


def __getattr__(name: str) -> object:
    """Resolve a public name on first access and cache it (PEP 562)."""
    try:
        module = _EXPORTS[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
    value = getattr(import_module(module), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Advertise the public names to ``dir()`` and tab completion."""
    return sorted(__all__)
```

```python
# src/data/ingest/__init__.py
# empty
```

What goes in `__all__` is decided in `surface.md`, not here: a name is public because a
downstream package or a CLI command consumes it, and for no other reason. Sections expose
many entry points to their siblings; consumers need a few of them, and every name on the
surface is a promise a later change has to keep.

Inside a package, import from the module that defines the thing — `from data.ingest.loaders
import load_bars`, never `from data import load_bars` — so that nothing under `data/` triggers
the top-level re-exports and their import cost. From another package, import from the top
level only — `from data import load_bars` — so the provider can reorganize its internals
without breaking you.

Why one boundary and not zero or all: *empty everywhere* gives up a stable public surface, so
every internal reorganization becomes a breaking change for outside callers. *Re-exports
everywhere* is worse: code in an `__init__.py` runs whenever any module below it is imported,
which is where circular imports come from and why `import pkg.one_small_thing` ends up paying
for numpy and scipy. Publishing at exactly one boundary buys the stable surface where it is
worth having and confines the eager-import cost to one rarely-edited file.

Two consequences: never put a module-level `settings = Settings()` anywhere the top-level
`__init__.py` can reach (see `python-implementation` §3); and promoting `foo.py` to `foo/`
changes *internal* call sites only — external callers on the re-exported name are unaffected.

### Preferred Libraries

Use these libraries when applicable:

| Purpose | Library |
|---------|---------|
| Data validation/models | `pydantic` |
| Logging | `loguru` |
| CLI | `cyclopts`, `rich` |
| Testing | `pytest`, `pytest-mock` |

## Summary

When writing Python code:

1. Use type annotations for all functions
2. Follow naming conventions consistently
3. Write a docstring on every module, class, function, and method — one line is enough for a private helper
4. Keep functions focused; comment each phase, and extract only when the jump buys something
5. Use comprehensions for simple cases
6. Prefer implicit false in boolean contexts
7. Use f-strings for formatting
8. Always use context managers for resources
9. Run `ruff check` and `ruff format`
10. Top-level `__init__.py` re-exports the public API with `__all__`; every nested one is empty
11. **BE CONSISTENT** with existing code

## Additional resources

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) — the source
- `references/` — see **Scope** at the top of this file
