# Simple XYZ interpreter

An interpreter for XYZ, a Lua-like embeddable scripting language.

`main.py` runs a provided file while providing some basic functions to the program.

## Usage

`uv run main.py <file>`
(Or one of the `xyzrun` wrappers, depending on platform)

Setting the environment variable `XYZ_DEBUG` to anything other than `0` prints debug information,
including the return value of a file.

## Development

`uv sync` - install dev dependencies

`uv run ty check` - runs the type checker

`uv run pytest -v` - runs the tests to make sure things parse as expected
