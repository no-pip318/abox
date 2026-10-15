#!/usr/bin/env python3
"""文档结构自检脚本（demo 版，模板感知）。

用法:
    python3 validate.py <文档.md>

按内容自动识别模板（周报 / PRD / 通用），校验:
    1. 有且仅有一个一级标题
    2. 所选模板要求的章节齐全
    3. 无前言/寒暄（首个非空行必须是标题）
    4. 正文 [n] 引用需在「参考来源」中有对应条目
"""
import re
import sys

# 模板 -> 必备章节
TEMPLATES = {
    "周报": ["本周概览", "关键进展", "下周计划"],
    "PRD": ["背景与目标", "用户与场景", "功能需求", "交互与流程", "验收标准"],
    "通用": ["摘要", "大纲", "正文", "参考来源"],
}
PREAMBLE = ("好的", "以下是", "这是您的", "希望对您", "如下：", "为您生成", "这是您")


def _norm(name):
    """去掉标题前的编号，如「1. 背景与目标」→「背景与目标」。"""
    return re.sub(r"^[0-9]+[.、]\s*", "", name).strip()


def headings(text):
    return [(len(m.group(1)), _norm(m.group(2)))
            for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)]


def section_body(text, name):
    """返回该章节正文（含子章节），直到出现同级或更高级标题为止。"""
    hs = list(re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, re.MULTILINE))
    for i, m in enumerate(hs):
        if _norm(m.group(2)) == name:
            level = len(m.group(1))
            end = len(text)
            for nxt in hs[i + 1:]:
                if len(nxt.group(1)) <= level:
                    end = nxt.start()
                    break
            return text[m.end():end].strip()
    return None


def detect(hs):
    names = [n for _, n in hs]
    h1 = next((n for lvl, n in hs if lvl == 1), "")
    if "周报" in h1 or "本周概览" in names:
        return "周报"
    if "PRD" in h1 or "产品需求文档" in h1 or "功能需求" in names:
        return "PRD"
    return "通用"


def main():
    if len(sys.argv) != 2:
        print("用法: python3 validate.py <文档.md>")
        sys.exit(2)

    text = open(sys.argv[1], encoding="utf-8").read()
    errors = []

    hs = headings(text)
    names = [n for _, n in hs]

    h1 = [n for lvl, n in hs if lvl == 1]
    if len(h1) != 1:
        errors.append(f"一级标题数量应为 1，实际为 {len(h1)}")

    # 前言/寒暄检查：首个非空行必须是标题
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    if not first.startswith("#"):
        errors.append("首行不是标题，存在前言/寒暄内容")
    elif any(w in first for w in PREAMBLE):
        errors.append("标题行疑似包含寒暄用语")

    tmpl = detect(hs)
    for req in TEMPLATES[tmpl]:
        if req not in names:
            errors.append(f"[{tmpl}] 缺少必备章节: {req}")

    if tmpl == "通用" and "大纲" in names and "正文" in names:
        if names.index("大纲") > names.index("正文"):
            errors.append("章节顺序错误: 大纲应在正文之前")

    # 引用完整性
    sources = section_body(text, "参考来源")
    body_text = "\n".join(
        section_body(text, n) or "" for n in
        ("正文", "关键进展", "功能需求", "背景与目标"))
    cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", body_text)})
    if cited:
        if sources is None:
            errors.append("存在 [n] 引用但缺少「参考来源」章节")
        else:
            listed = {int(n) for n in re.findall(r"^\[(\d+)\]", sources, re.MULTILINE)}
            for n in cited:
                if n not in listed:
                    errors.append(f"正文引用了 [{n}]，但参考来源中缺少对应条目")

    for e in errors:
        print(f"[错误] {e}")

    if errors:
        print(f"\n校验未通过（模板: {tmpl}）: {len(errors)} 个错误")
        sys.exit(1)
    print(f"\n校验通过（模板: {tmpl}）")
    sys.exit(0)


if __name__ == "__main__":
    main()
