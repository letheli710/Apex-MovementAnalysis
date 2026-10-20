import os
import subprocess
import sys
import unittest

from _common import PREP, TOOLS
from hsdtel import schema


class TestDocs(unittest.TestCase):
    def test_schema_table_in_doc_is_current(self):
        with open(os.path.join(PREP, "TELEMETRY-SCHEMA.md"), encoding="utf-8") as fh:
            text = fh.read()
        start = text.index(schema.BEGIN_MARK) + len(schema.BEGIN_MARK)
        end = text.index(schema.END_MARK)
        self.assertEqual(text[start:end], schema.as_markdown(),
                         "regenerate: python tools/hsd_tel.py schema --update-doc TELEMETRY-SCHEMA.md")

    def test_references_resolve(self):
        # External references are only checked when the source clones exist
        # (HSD_SRC_ROOT); repository paths and Markdown links always are.
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "check_refs.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
