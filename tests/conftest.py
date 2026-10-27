"""Load api.py/const.py as a standalone package so tests don't need Home Assistant."""
import importlib.util
import pathlib
import sys
import types

PKG = "shl_scoreboard_standalone"
SRC = pathlib.Path(__file__).parent.parent / "custom_components" / "shl_scoreboard"

if PKG not in sys.modules:
    package = types.ModuleType(PKG)
    package.__path__ = [str(SRC)]
    sys.modules[PKG] = package
    for name in ("const", "api"):
        spec = importlib.util.spec_from_file_location(f"{PKG}.{name}", SRC / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"{PKG}.{name}"] = module
        spec.loader.exec_module(module)
