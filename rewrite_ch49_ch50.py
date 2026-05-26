import os

# Paths to the relevant markdown files
data_structures_path = "docs/guide/49-data-structures.md"
algorithms_path = "docs/guide/50-algorithms.md"

# Template content for the new data structure chapter
data_structures_template = """# 49. 数据结构基础与进阶

> 难度分布：🟢 入门 37 题 · 🟡 进阶 15 题 · 🔴 高难 5 题

[[toc]]

---

## 一、线性结构

> 📌 **本节重点**：数组、链表、栈、队列的底层实现与 STL 容器对应关系

### Q1: ⭐🟢 数组和链表的核心区别？

答案...（这里插入图表和注解）

```mermaid
graph LR
    A[数组] -->|连续内存| B[index 直接访问 O1]
    C[链表] -->|离散内存| D[需要遍历 On]
```

> 💡 **面试追问**：vector 扩容时迭代器为什么会失效？deque 为什么没有这个问题？

---

...（添加其余所有问题和对应的小节）

## 📊 本章统计
|类型|题数|
|----|----|
|线性结构|...|
|树结构|...|
"""

# Template content for the new algorithms chapter
algorithms_template = """# 50. 算法与复杂度分析

> 难度分布：🟢 入门 39 题 · 🟡 进阶 15 题 · 🔴 高难 5 题

[[toc]]

---

## 一、复杂度基础

> 📌 **本节重点**：时间复杂度、空间复杂度的计算方法

### Q1: ⭐🟢 如何分析算法的时间复杂度和空间复杂度？

答案...

```mermaid
graph TD
    A[输入规模] -->B[时间复杂度]
    A --> C[空间复杂度]
```

> 💡 **面试追问**：你能举一个优化空间复杂度的例子吗？

---

...（添加其余所有问题和对应的小节）

## 📊 本章统计
|主题|题数|
|----|---|
|排序算法|...|
|查找算法|...|
"""

def write_file(path, content):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Write the content to the file
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

# Write the new content to the files
write_file(data_structures_path, data_structures_template)
write_file(algorithms_path, algorithms_template)

print("Rewritten content applied.")