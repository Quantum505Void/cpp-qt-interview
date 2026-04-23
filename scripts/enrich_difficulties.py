#!/usr/bin/env python3
"""
为各章节增加 ⬤ 入门题和 ⬤ 难题。
- 每章补入门题(🟢)和高难题(🔴)
- 调整章节末尾统计表
"""
import random
import os

target_chapters = {
    "07-concurrency.md": {"green": 2, "red": 2},
    "06-qt-core.md": {"green": 2, "red": 2},
    "41-electron.md": {"green": 2, "red": 2},
    "38-kalman.md": {"green": 2, "red": 2},
    "04-polymorphism.md": {"green": 2, "red": 2},
}

# 动态题库生成
new_questions = {
    "green": [
        "讲一下上下文切换的原理？",
        "什么是双向链表和常用场景？",
        "map和unordered_map有什么区别？",
    ],
    "red": [
        "Cache Line False Sharing 怎么解决？",
        "如何实现无锁队列？有哪些适用的场景？",
        "多线程环境中如何检测死锁？",
    ],
}

def enrich_difficulty(content, num_green, num_red):
    """增加入门题和高难题，按章节 Q编号偏置"""
    lines = content.splitlines(keepends=True)
    existing = [ln for ln in lines if '### Q' in ln]
    base_num = len(existing)

    added_lines = []
    for i in range(num_green):
        qtext = random.choice(new_questions['green'])
        added_lines.append(f"\n### Q{base_num + i}: ⭐🟢 {qtext}\\nA: ...\\n")
    for red in range(num_red):
        rtext = random.choice(new_questions['red'])
        added_lines.append(f"\n### Q{red}: ⭐🔴 {rtext}\nAnswer pending..!!")
