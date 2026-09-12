---
name: python-implementation
description: The mechanics of splitting an oversized module or directory, and the pydantic-settings config pattern with its subpackage split. Invoke when a file or directory has passed a size limit and needs splitting, or when creating or restructuring a package's configs.py.
---

# Python implementation mechanics

The procedures behind `project-structure`. That skill says *when* something must split and
*where* config lives; this one says how to actually do it.

Invoke this when you are about to split something or write a `configs.py` — not before. It is
kept out of the always-loaded path because most runs never need it.

## 1. Splitting a module

Split along responsibility seams, never at an arbitrary line. A split at line 400 of a
900-line module produces two modules that both import each other; a split along a seam produces
two modules that read as separate ideas.

In order of preference:

1. **Extract a class or a cohesive group of functions** into a sibling module named for the
   noun it owns — `parsers.py`, `calendar.py`. Use this when one class exceeds its soft limit,
   or the module has two groups that never call each other. The second condition is the
   clearest seam you will ever get: if group A never calls group B, they were already two
   modules.

2. **Promote the module to a package** when it has three or more natural groups:
   `foo.py` → `foo/core.py`, `foo/io.py`, with an **empty** `foo/__init__.py`.

   Internal call sites change: `from mypkg.foo import Thing` becomes
   `from mypkg.foo.core import Thing` everywhere inside the package, because nested
   `__init__.py` files are empty and there is no re-export layer below the top level. External
   callers are unaffected *if* `Thing` is re-exported in the package's top-level `__init__.py`
   — update that one import there and `from mypkg import Thing` keeps working.

   Size the blast radius before you start:

   ```
   grep -rn "from mypkg\.foo import\|import mypkg\.foo\b" packages/ src/ tests/
   ```

   Because it touches call sites, a promotion is planned work: if you hit it mid-implementation
   and the grep stays inside your section, do it deliberately, update every import, and run the
   full suite. If it reaches other sections, file a follow-up naming the moved names and leave
   the module oversized with a note — reaching into another section's imports is not yours to
   do. If it reaches another *package* (the name is re-exported and a consumer uses it), the
   move is invisible to them as long as the top-level re-export is updated in the same change.

3. **Move shared helpers down, not up.** A helper used by two subpackages becomes a module in
   their common parent, never a top-level `utils.py`. "Up" collects unrelated things into one
   file that then belongs to nobody.

After any split, run the tests and an import check (`python -c "import <pkg>"`) before
continuing. The import check catches the circular import a split can introduce, which tests
sometimes miss if they import in a lucky order. A split is complete only when nothing else
changed.

## 2. Splitting a directory

When a package directory passes the module limit, group by the prefix or noun the files already
share — the naming usually reveals the grouping before you do:

- **Three or more modules sharing a prefix** (`parse_pdf.py`, `parse_html.py`, `parse_csv.py`)
  → a subpackage named for the prefix: `parsers/pdf.py`, `parsers/html.py`, `parsers/csv.py`.
- **Otherwise group by layer**: `models/`, `io/`, `services/`, `cli/`.

Do not mix the two schemes inside one package — half the files grouped by domain and half by
layer means nobody can guess where a new file goes.

Move the tests to mirror the new paths in the same change, and apply the §3 config split below
at the same time if the new subpackage owns a third of the fields.

## 3. Configuration

One `configs.py` per package, `pydantic-settings`, secrets as `SecretStr`:

```python
# src/<pkg>/configs.py
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="<PKG>_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="forbid",
    )

    database_url: SecretStr
    batch_size: int = 500
```

`extra="forbid"` turns a typo'd env var into a startup error instead of a silently ignored
setting. `SecretStr` keeps the value out of `repr`, logs, and tracebacks.

### Subpackage split

When a subpackage owns a third or more of the fields, or `configs.py` passes the soft module
limit, give the subpackage its own settings class and nest it:

```python
# src/<pkg>/ingest/configs.py
class IngestSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="forbid")

    workers: int = 4
    retry_limit: int = 3


# src/<pkg>/configs.py
from .ingest.configs import IngestSettings


class Settings(BaseSettings):
    ...
    ingest: IngestSettings = IngestSettings()   # env: <PKG>_INGEST__WORKERS
```

The parent stays the single entry point. Modules import the subsettings they need *from the
parent*, never constructing their own — two instances of a settings class read the environment
twice and can disagree after any change.

### Instantiation

Never put a module-level `settings = Settings()` anywhere the package's top-level `__init__.py`
can reach — and since that file re-exports from the sections, it reaches most of them. A
required field with no default turns `import <pkg>` into a crash at import time, which surfaces
as a broken CLI, a broken test collection, and a broken IDE all at once. Construct it in the
entry point, or behind a cached accessor:

```python
from functools import lru_cache


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
```
