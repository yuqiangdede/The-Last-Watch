#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tempfile
import unittest
from pathlib import Path

from scan_chapter import is_han, prose_lines, scan

class ScanTests(unittest.TestCase):
    def test_han_and_title_exclusion(self):
        self.assertTrue(is_han("霰"))
        self.assertFalse(is_han("。"))
        self.assertEqual(list(prose_lines("# 标题\n\n正文。\n")), [(3, "正文。")])

    def test_pattern_is_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / "第001章.md"
            file.write_text("# 第一章\n\n这一刻他终于明白了。\n\n普通一句话。\n", encoding="utf8")
            result = scan(file)
            self.assertEqual(result["han_characters"], 14)
            self.assertEqual(result["non_whitespace_characters"], 16)
            self.assertEqual(result["length_status"], "NOT_BLOCKED_BY_LENGTH")
            self.assertTrue(any(h["type"] == "总结式顿悟" and h["line"] == 3
                                for h in result["potential_patterns"]))

    def test_first_four_volume_length_gate(self):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / "06-正文" / "第一卷" / "第001章.md"
            file.parent.mkdir(parents=True)
            file.write_text("# 题目\n\n" + "我" * 3999, encoding="utf8")
            self.assertEqual(scan(file)["length_status"], "BLOCKED")
            file.write_text("# 题目\n\n" + "我" * 4000, encoding="utf8")
            self.assertEqual(scan(file)["length_status"], "NOT_BLOCKED_BY_LENGTH")

if __name__ == "__main__":
    unittest.main()
