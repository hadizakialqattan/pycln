"""System hacks utility."""
import sys
from contextlib import contextmanager
from enum import Enum, unique
from io import StringIO
from typing import Generator


@unique
class STD(Enum):
    OUT: int = 0
    ERR: int = 1


@contextmanager
def std_redirect(type_: STD) -> Generator:
    """Redirect stdout/err to a variable.

    :param type_: `STD.OUT` or `STD.ERR`.
    :returns: Generator of `StringIO` represents `sys.stdout/stderr`.
    """
    std_capture = StringIO()
    if type_ is STD.OUT:
        default_std = sys.stdout
        sys.stdout = std_capture
    else:
        default_std = sys.stderr
        sys.stderr = std_capture
    yield std_capture
    if type_ is STD.OUT:
        sys.stdout = default_std
    else:
        sys.stderr = default_std


@contextmanager
def hide_sys_argv():
    """Hide `sys.argv`"""
    sys_argv = sys.argv.copy()
    sys.argv.clear()
    yield
    sys.argv = sys_argv


class Pass(Exception):
    """Raises to pass some tests."""
