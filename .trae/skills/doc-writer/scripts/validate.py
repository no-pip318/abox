#!/usr/bin/env python3
"""文档结构自检脚本（demo 版）。

用法:
    python3 validate.py <生成的文档.md>

校验:
    1. 存在必备章节: 摘要 / 大纲 / 正文 / 参考来源
    2. 章节顺序正确（大纲在正文之前）
    3. 存在一级标题（标题）
    4. 正文非空
    5. 正文中出现 [n] 引用时，参考来源中需有对应条目
"""
import re
import sys

REQUIRED = ["摘要", "大纲", "正文", "参考来源"]


def headings(text):
    return [(len(m.group(1)), m.group(2).strip())
            for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)]


def section_body(text, name):
    """返回该章节的正文，包含其所有子章节，直到出现同级或更高级标题为止。"""
    hs = list(re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, re.MULTILINE))
    for i, m in enumerate(hs):
        if m.group(2).strip() == name:
            level = len(m.group(1))
            end = len(text)
            for nxt in hs[i + 1:]:
                if len(nxt.group(1)) <= level:
                    end = nxt.start()
                    break
            return text[m.end():end].strip()
    return None


def main():
    if len(sys.argv) != 2:
        print("用法: python3 validate.py <文档.md>")
        sys.exit(2)

    text = open(sys.argv[1], encoding="utf-8").read()
    errors, warnings = [], []

    hs = headings(text)
    if not any(lvl == 1 for lvl, _ in hs):
        errors.append("缺少一级标题（标题）")

    names = [n for _, n in hs]
    for req in REQUIRED:
        if req not in names:
            errors.append(f"缺少必备章节: {req}")

    if "大纲" in names and "正文" in names:
        if names.index("大纲") > names.index("正文"):
            errors.append("章节顺序错误: 大纲应在正文之前")

    body = section_body(text, "正文")
    if body is not None and len(body) < 50:
        warnings.append("正文内容过短（< 50 字）")

    cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", body or "")})
    sources = section_body(text, "参考来源") or ""
    listed = {int(n) for n in re.findall(r"^\[(\d+)\]", sources, re.MULTILINE)}
    for n in cited:
        if n not in listed:
            errors.append(f"正文引用了 [{n}]，但参考来源中缺少对应条目")

    for w in warnings:
        print(f"[警告] {w}")
    for e in errors:
        print(f"[错误] {e}")

    if errors:
        print(f"\n校验未通过: {len(errors)} 个错误")
        sys.exit(1)
    print("\n校验通过" + (f"（{len(warnings)} 个警告）" if warnings else ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
