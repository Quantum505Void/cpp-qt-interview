#!/usr/bin/env python3
"""Full-site refactor for cpp-qt-interview VitePress project."""

import os
import re
import json
from pathlib import Path

GUIDE_DIR = Path('/home/void/文档/project/cpp-qt-interview/docs/guide')
CONFIG_PATH = Path('/home/void/文档/project/cpp-qt-interview/docs/.vitepress/config.mts')
INDEX_PATH = Path('/home/void/文档/project/cpp-qt-interview/docs/index.md')

# ── helpers ──────────────────────────────────────────────────────────────────

def count_difficulty(text):
    lines = text.splitlines()
    g = y = r = 0
    for line in lines:
        if re.match(r'###\s+Q\d+', line):
            g += line.count('🟢')
            y += line.count('🟡')
            r += line.count('🔴')
    return g, y, r

def count_questions(text):
    return len(re.findall(r'^###\s+Q\d+', text, re.MULTILINE))

def get_title(text):
    """Return the first # heading text."""
    m = re.search(r'^#\s+(.+)', text, re.MULTILINE)
    return m.group(1).strip() if m else ''

# ── process chapter files ────────────────────────────────────────────────────

stats_by_file = {}  # filename -> (total, g, y, r)

files = sorted(GUIDE_DIR.glob('*.md'))
chapter_files = [f for f in files if not f.name.startswith('00-')]

for fpath in chapter_files:
    text = fpath.read_text(encoding='utf-8')
    g, y, r = count_difficulty(text)
    total = count_questions(text)
    stats_by_file[fpath.name] = (total, g, y, r)

    # ── 1. Fix header ──
    # Remove "↑ 回到目录" lines (with surrounding blank lines)
    text = re.sub(r'\n*\n↑ 回到目录\n*', '\n', text)

    # After the first # heading, insert difficulty block + [[toc]] + ---
    # Pattern: "# N. Title\n" possibly followed by blank lines
    def replace_header(m):
        heading = m.group(1).rstrip()
        block = f"{heading}\n\n> 难度分布：🟢 入门 {g} 题 · 🟡 进阶 {y} 题 · 🔴 高难 {r} 题\n\n[[toc]]\n\n---\n"
        return block

    # Replace existing header section (heading + optional blank lines + optional old toc/hr)
    # Be conservative: just replace heading line + remove old diff block if present
    # First strip any existing difficulty line
    text = re.sub(r'\n> 难度分布：.*\n', '\n', text)
    # Strip existing [[toc]] line
    text = re.sub(r'\n\[\[toc\]\]\n', '\n', text)
    # Strip leading --- after heading (if already there from prior run)
    # We'll re-insert everything cleanly after the heading

    # Now find first heading and rewrite header block
    text = re.sub(
        r'^(#[^\n]+)\n+',
        lambda m: f"{m.group(1)}\n\n> 难度分布：🟢 入门 {g} 题 · 🟡 进阶 {y} 题 · 🔴 高难 {r} 题\n\n[[toc]]\n\n---\n\n",
        text,
        count=1,
        flags=re.MULTILINE
    )

    # ── 2. Fix footer ──
    # Remove existing stats block if present
    text = re.sub(
        r'\n---\n\n## 📊 本章统计\n[\s\S]*?(?=\n---\n|$)',
        '',
        text
    )
    # Trim trailing whitespace/newlines
    text = text.rstrip()

    footer = f"""

---

## 📊 本章统计

| 指标 | 数量 |
|------|------|
| 总题目数 | {total} |
| 🟢 入门 | {g} |
| 🟡 进阶 | {y} |
| 🔴 高难 | {r} |
"""
    text = text + footer

    fpath.write_text(text, encoding='utf-8')
    print(f"  ✓ {fpath.name}  total={total} 🟢{g} 🟡{y} 🔴{r}")

print(f"\nProcessed {len(chapter_files)} chapter files.\n")

# ── rebuild sidebar config ───────────────────────────────────────────────────

# Map file prefix -> sidebar group
GROUPS = [
    ('🗺️ 学习路线',      ['00']),
    ('🧩 C++ 核心',       ['02','03','04','05','15','20','21','22','23','24','25','26']),
    ('🎨 Qt 框架',        ['01','06','09','43']),
    ('🧵 并发与线程',     ['07','08','10']),
    ('📡 通信与协议',     ['12','13','18','42']),
    ('🐧 Linux 与工程化', ['16','17','19','30']),
    ('🧮 数据结构与算法', ['49','50']),
    ('🏗️ 系统设计',       ['14','31','32']),
    ('🎯 项目与面试',     ['33','34','35']),
    ('🔧 扩展领域',       ['11','27','28','29','36','37','38','39','40','41','44','45']),
    ('🤖 AI / 大模型',    ['46','47','48']),
]

# Build prefix -> filepath map
prefix_map = {}
for fpath in files:
    m = re.match(r'^(\d+)-', fpath.name)
    if m:
        prefix_map[m.group(1).zfill(2)] = fpath
    elif fpath.name.startswith('00-'):
        prefix_map['00'] = fpath

def make_sidebar_item(fpath):
    text = fpath.read_text(encoding='utf-8')
    title = get_title(text)
    # Extract number prefix from filename
    m = re.match(r'^(\d+)-', fpath.name)
    num = int(m.group(1)) if m else 0
    stem = fpath.stem  # e.g. 01-qt-basics
    link = f'/guide/{stem}'
    item_text = f'{num}. {re.sub(r"^\d+\.\s*", "", title)}' if num else title
    return f"          {{ text: '{item_text}', link: '{link}' }}"

sidebar_groups = []
for group_name, prefixes in GROUPS:
    items = []
    for p in prefixes:
        key = p.zfill(2)
        if key in prefix_map:
            items.append(make_sidebar_item(prefix_map[key]))
    if not items:
        continue
    collapsed = 'false'
    items_str = ',\n'.join(items)
    group = f"""      {{
        text: '{group_name}',
        collapsed: {collapsed},
        items: [
{items_str}
        ]
      }}"""
    sidebar_groups.append(group)

sidebar_str = ',\n'.join(sidebar_groups)

# Read current config and replace sidebar section
config = CONFIG_PATH.read_text(encoding='utf-8')

new_sidebar = f"""    sidebar: [
{sidebar_str}
    ],"""

config = re.sub(
    r'    sidebar: \[[\s\S]*?\],(\s*\n\s*search:)',
    new_sidebar + r'\1',
    config
)

CONFIG_PATH.write_text(config, encoding='utf-8')
print("✓ Rebuilt sidebar in config.mts\n")

# ── update index.md ──────────────────────────────────────────────────────────

total_chapters = len(chapter_files)
total_questions = sum(v[0] for v in stats_by_file.values())

# Count per group for features (using actual group assignments)
def count_group(prefixes):
    chaps = sum(1 for p in prefixes if p.zfill(2) in prefix_map and prefix_map[p.zfill(2)].name != '00-roadmap.md')
    qs = sum(stats_by_file.get(prefix_map[p.zfill(2)].name, (0,0,0,0))[0]
             for p in prefixes if p.zfill(2) in prefix_map and prefix_map[p.zfill(2)].name != '00-roadmap.md')
    return chaps, qs

cpp_c, cpp_q = count_group(['02','03','04','05','15','20','21','22','23','24','25','26'])
qt_c, qt_q = count_group(['01','06','09','43'])
concur_c, concur_q = count_group(['07','08','10'])
comm_c, comm_q = count_group(['12','13','18','42'])
linux_c, linux_q = count_group(['16','17','19','30'])
design_c, design_q = count_group(['14','31','32'])
interview_c, interview_q = count_group(['33','34','35'])
ext_c, ext_q = count_group(['11','27','28','29','36','37','38','39','40','41','44','45'])
ai_c, ai_q = count_group(['46','47','48'])
ds_c, ds_q = count_group(['49','50'])

index = INDEX_PATH.read_text(encoding='utf-8')

# Update tagline
index = re.sub(
    r'tagline:.*',
    f'tagline: 从面试小白到 offer 收割机 — {total_chapters}章 · {total_questions}+ 题目 · 系统覆盖 C++/Qt/Linux/AI/工程化',
    index
)

# Update features
index = re.sub(
    r'(title: C\+\+ 现代特性 ·).*',
    f'\\1 {cpp_c}章',
    index
)
index = re.sub(
    r'(details: C\+\+11~20 新特性、模板、智能指针、移动语义、内存模型完整覆盖，)\d+\+ 题目',
    f'\\g<1>{cpp_q}+ 题目',
    index
)
index = re.sub(
    r'(title: Qt 框架深入 ·).*',
    f'\\1 {qt_c}章',
    index
)
index = re.sub(
    r'(details: Qt5/Qt6 核心机制、信号槽、事件系统、Qt Quick/QML 现代 UI 开发，)\d+\+ 题目',
    f'\\g<1>{qt_q}+ 题目',
    index
)
index = re.sub(
    r'(title: AI 大模型 ·).*',
    f'\\1 {ai_c}章',
    index
)
index = re.sub(
    r'(details: LLM 应用开发、RAG、Fine-tuning、量化部署、AI 工程化，)\d+ 题目',
    f'\\g<1>{ai_q} 题目',
    index
)

# Rebuild coverage table
ds_row = f'| 数据结构与算法 | {ds_c} | 数据结构、算法 |\n' if ds_c > 0 else ''
new_table = f"""## 📊 覆盖范围

| 模块 | 章节数 | 代表章节 |
|------|--------|----------|
| C++ 核心 | {cpp_c} | C++11~20、模板、STL、移动语义、内存模型 |
| Qt 框架 | {qt_c} | Qt 基础、核心机制、Qt5/6 区别、Qt Quick/QML |
| 并发/线程 | {concur_c} | 并发原理、消息队列、线程池 |
| 通信/协议 | {comm_c} | 消息通信、CRC、串口/USB/HID、嵌入式协议 |
| Linux/工程化 | {linux_c} | 系统编程、命令调试、CMake、Git |
| 系统设计 | {design_c} | 设计模式、软件工程原则、场景设计 |
| 项目/面试 | {interview_c} | 项目经验、面试技巧、高频综合题 |
| 扩展领域 | {ext_c} | 加密、性能优化、网络、数据库、GIS、Redis、跨平台、调试分析 |
| AI 大模型 | {ai_c} | LLM 应用开发、模型优化、AI 工程化部署 |
{ds_row}| **合计** | **{total_chapters}** | **{total_questions}+ 题目** |"""

index = re.sub(r'## 📊 覆盖范围[\s\S]*$', new_table, index)
INDEX_PATH.write_text(index, encoding='utf-8')
print("✓ Updated index.md\n")
print(f"Summary: {total_chapters} chapters, {total_questions}+ questions total.")
