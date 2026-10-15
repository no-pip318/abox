---
name: "doc-writer"
description: "根据主题和素材生成结构化 Markdown 文档（标题/摘要/大纲/正文/参考来源）。当用户要写文章、报告、说明文档，或要从大纲生成文档时调用。"
---

# Skill: 文档生成器

## 用途
根据用户提供的主题和素材，生成结构化 Markdown 文档。

## 输入
- 主题（必填）
- 受众（可选，默认：普通读者）
- 目标字数（可选，默认：800–1200 字）
- 参考材料（可选）

## 输出
按以下顺序，一次性输出完整文档：
1. 标题
2. 摘要
3. 大纲
4. 正文
5. 参考来源

## 规则
- 必须先输出大纲，再生成正文
- 不得编造未提供的数据
- 引用材料需标注来源
- 输出必须符合 `references/outline_templates.md` 中的结构

## 工作流程
1. 解析输入，确定主题、受众、目标字数
2. 从 `references/outline_templates.md` 选择最贴近的模板
3. 生成大纲，交由用户确认（用户已明确「直接生成」时可跳过）
4. 按 `references/writing_rules.md` 展开正文
5. 按 `references/citation_rules.md` 标注来源
6. 运行 `scripts/validate.py` 做结构自检，修正后输出

## 参考文件
- `references/outline_templates.md`：大纲模板库
- `references/writing_rules.md`：写作规范
- `references/citation_rules.md`：引用规范
- `examples/input.md`、`examples/output.md`：输入输出示例
- `scripts/validate.py`：结构校验脚本
