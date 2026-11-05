#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只读设定巡检脚本的离线回归测试。"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

FILE = Path(__file__).with_name("audit_setting_structure.py")
spec = importlib.util.spec_from_file_location("audit_setting_structure", FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SettingMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.put("03-剧情/全书主线.md", "# 主线\n> 最后修订时间：2026-01-01 09:00:00 +08:00\n")
        self.put("03-剧情/卷大纲.md", "# 卷纲\n[第一卷](章大纲/第01卷.md)\n[第二卷](章大纲/第02卷.md)\n")
        self.put("03-剧情/章大纲/第01卷.md", "# 第一卷\n- 编号章节数：2章\n| 第001章 | 标题 | 情节 | 状态 |\n| 第002章 | 标题 | 情节 | 状态 |\n")
        self.put("03-剧情/章大纲/第02卷.md", "# 第二卷\n- 编号章节数：1章\n| **003 / 001** | 标题 | 情节 | 结果 | 关联 | 状态 |\n")
        self.put("06-正文/第一卷/第001章.md", "正文保护\n")
        self.put("06-正文-TXT/第一卷/第001章.txt", "TXT保护\n")
        self.put("05-写作计划/章节简写/第01卷/第001章.md", "简写保护\n")
        self.put("05-写作计划/章节规划总表.md", "只读索引\n")
        self.put("02-人物/角色.md", "# 角色\n> 最后修订时间：2026-01-01 09:00:00 +08:00\n联域不是第八强权\n")

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, rel, body):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

    def test_covers_every_volume_and_both_row_formats(self):
        data = module.scan(self.root, expected_volumes=2)
        self.assertEqual(data["summary"]["volumes_read"], 2)
        self.assertEqual(data["summary"]["chapter_rows_recognized"], 3)
        self.assertEqual(data["summary"]["errors"], 0)

    def test_unexpanded_volume_and_plain_numeric_declared_count(self):
        self.put("03-剧情/章大纲/第02卷.md", "# 第二卷\n- 编号章节数：待定\n")
        data = module.scan(self.root, expected_volumes=2)
        self.assertEqual(data["summary"]["volumes_unexpanded"], 1)
        self.assertIn("PLANNED_NOT_SPLIT", [x["code"] for x in data["issues"]])
        self.assertEqual(data["volume_coverage"][0]["declared_count"], 2)

    def test_missing_volume_is_error_not_silent_pass(self):
        data = module.scan(self.root, expected_volumes=3)
        self.assertIn("MISSING_CHAPTER_OUTLINE", [issue["code"] for issue in data["issues"]])

    def test_duplicate_and_mismatch_are_errors(self):
        self.put("03-剧情/章大纲/第01卷.md", "# 第一卷\n- 编号章节数：3章\n| 第001章 | X | X | X |\n| 第001章 | X | X | X |\n")
        data = module.scan(self.root, expected_volumes=2)
        self.assertIn("DUPLICATE_CHAPTER", [x["code"] for x in data["issues"]])
        self.assertIn("CHAPTER_COUNT_MISMATCH", [x["code"] for x in data["issues"]])

    def test_term_evidence_and_protected_content(self):
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        data = module.scan(self.root, expected_volumes=2, terms=["联域"])
        after = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertTrue(data["term_evidence"]["联域"])
        self.assertFalse(any("06-正文" in i["path"] for i in data["inventory"]))
        self.assertFalse(any("章节简写" in i["path"] for i in data["inventory"]))
        self.assertFalse(any("章节规划总表" in i["path"] for i in data["inventory"]))

    def test_legacy_path_is_candidate_not_safe_auto_change(self):
        self.put("03-剧情/备注.md", "此前在05-写作计划/章大纲/第01卷.md，已迁移。\n")
        data = module.scan(self.root, expected_volumes=2)
        self.assertIn("LEGACY_OUTLINE_PATH", [x["code"] for x in data["issues"]])
        self.assertEqual((self.root / "03-剧情/备注.md").read_text(encoding="utf-8"),
                         "此前在05-写作计划/章大纲/第01卷.md，已迁移。\n")


if __name__ == "__main__":
    unittest.main()
