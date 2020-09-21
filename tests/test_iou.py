"""pycln/utils/iou.py tests."""
import os
import tempfile
from pathlib import Path

import pytest

from pycln.utils import iou
from pycln.utils._exceptions import (
    ReadPermissionError,
    UnparsableFile,
    WritePermissionError,
)

from .utils import sysu


class TestIOU:

    """`iou.py` functions test case."""

    @pytest.mark.parametrize(
        "content, expec_code, expec_err, chmod",
        [
            pytest.param(
                "print('Hello')",
                "print('Hello')",
                sysu.Pass,
                0o0644,
                id="base case",
            ),
            pytest.param(
                "code...",
                None,
                ReadPermissionError,
                0o000,
                id="no read permission",
            ),
            pytest.param(
                "code...",
                None,
                WritePermissionError,
                0o444,
                id="no read write",
            ),
            pytest.param(
                #: Make conflict between BOM and encoding Cookie.
                #: For more information: https://bit.ly/32o3eVl
                "\ufeff\n# -*- coding: utf-32 -*-\nbad encoding",
                None,
                UnparsableFile,
                0o0644,
                id="bad encoding",
            ),
        ],
    )
    def test_safe_read(self, content, expec_code, expec_err, chmod):
        with pytest.raises(expec_err):
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".py") as tmp:
                tmp.write(content)
                tmp.seek(0)
                tmp_path = Path(tmp.name)
                os.chmod(tmp_path, chmod)
                # default param: permissions: tuple = (os.R_OK, os.W_OK).
                source_code, _ = iou.safe_read(tmp_path)
            assert source_code == expec_code
            raise sysu.Pass()

    @pytest.mark.parametrize(
        "fixed_lines, expec_code, expec_err, chmod",
        [
            pytest.param(
                ["import time\n", "time.time()\n"],
                "import time\ntime.time()\n",
                sysu.Pass,
                0o0644,
                id="best case",
            ),
            pytest.param(
                ["code...\n", "code...\n"],
                None,
                WritePermissionError,
                0o444,
                id="no write permission",
            ),
        ],
    )
    def test_safe_write(self, fixed_lines, expec_code, expec_err, chmod):
        with pytest.raises(expec_err):
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".py") as tmp:
                tmp_path = Path(tmp.name)
                os.chmod(tmp_path, chmod)
                iou.safe_write(tmp_path, fixed_lines, "utf-8")
                tmp.seek(0)
                assert tmp.read() == expec_code
            raise sysu.Pass()
