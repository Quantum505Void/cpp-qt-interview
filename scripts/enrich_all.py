#!/usr/bin/env python3
"""
全局丰富脚本：给所有章节文件添加
1. 章节内主题分组（## 二级标题）
2. 每道题标准化追问（> 💡 面试追问）
3. 每个大节开头 > 📌 本节重点
4. 更新尾部统计
"""
import re, os, sys

GUIDE_DIR = "docs/guide"

# 每个文件的分组配置：{文件名: [(分组标题, [Q编号列表])]}
# Q编号从1开始
GROUPINGS = {
    "01-qt-basics.md": [
        ("一、Qt 概览与架构", list(range(1, 5))),
        ("二、信号与槽", list(range(5, 9))),
        ("三、事件系统", list(range(9, 12))),
        ("四、Qt 对象模型", list(range(12, 16))),
    ],
    "02-cpp11-14-17.md": [
        ("一、类型推导与语言改进", list(range(1, 5))),
        ("二、移动语义与右值引用", list(range(5, 8))),
        ("三、Lambda 与函数对象", list(range(8, 11))),
        ("四、并发支持", list(range(11, 13))),
        ("五、其他重要特性", list(range(13, 16))),
    ],
    "03-cpp-core.md": [
        ("一、面向对象基础", list(range(1, 6))),
        ("二、关键字与类型系统", list(range(6, 11))),
        ("三、函数与运算符", list(range(11, 16))),
    ],
    "04-polymorphism.md": [
        ("一、多态基础", list(range(1, 6))),
        ("二、虚函数机制", list(range(6, 11))),
        ("三、高级多态场景", list(range(11, 16))),
    ],
    "05-virtual.md": [
        ("一、virtual 基础", list(range(1, 6))),
        ("二、虚函数表与内存布局", list(range(6, 11))),
        ("三、特殊场景与陷阱", list(range(11, 16))),
    ],
    "06-qt-core.md": [
        ("一、元对象系统", list(range(1, 5))),
        ("二、内存管理", list(range(5, 9))),
        ("三、线程与事件循环", list(range(9, 13))),
        ("四、核心容器与工具", list(range(13, 16))),
    ],
    "07-concurrency.md": [
        ("一、线程基础", list(range(1, 6))),
        ("二、同步原语", list(range(6, 11))),
        ("三、高级并发模式", list(range(11, 16))),
    ],
    "08-message-queue.md": [
        ("一、消息队列基础", list(range(1, 6))),
        ("二、实现与原理", list(range(6, 11))),
        ("三、应用场景与优化", list(range(11, 16))),
    ],
    "09-qt5-qt6.md": [
        ("一、核心变化", list(range(1, 6))),
        ("二、模块与 API 迁移", list(range(6, 11))),
        ("三、性能与兼容性", list(range(11, 16))),
    ],
    "10-thread-pool.md": [
        ("一、线程池基础", list(range(1, 6))),
        ("二、设计与实现", list(range(6, 11))),
        ("三、调优与实践", list(range(11, 16))),
    ],
    "11-crypto.md": [
        ("一、加密基础", list(range(1, 6))),
        ("二、对称与非对称加密", list(range(6, 11))),
        ("三、哈希与证书", list(range(11, 16))),
    ],
    "12-messaging.md": [
        ("一、通信模型", list(range(1, 6))),
        ("二、协议设计", list(range(6, 11))),
        ("三、可靠性与优化", list(range(11, 16))),
    ],
    "13-crc.md": [
        ("一、校验基础", list(range(1, 6))),
        ("二、CRC 原理", list(range(6, 11))),
        ("三、实现与应用", list(range(11, 16))),
    ],
    "14-design-patterns.md": [
        ("一、创建型模式", list(range(1, 5))),
        ("二、结构型模式", list(range(5, 9))),
        ("三、行为型模式", list(range(9, 13))),
        ("四、模式选择与实践", list(range(13, 16))),
    ],
    "15-smart-pointers.md": [
        ("一、智能指针基础", list(range(1, 5))),
        ("二、unique_ptr 与 shared_ptr", list(range(5, 10))),
        ("三、weak_ptr 与循环引用", list(range(10, 13))),
        ("四、自定义与陷阱", list(range(13, 16))),
    ],
    "16-linux-programming.md": [
        ("一、进程与文件", list(range(1, 6))),
        ("二、线程与同步", list(range(6, 11))),
        ("三、网络与 IPC", list(range(11, 16))),
    ],
    "17-linux-commands.md": [
        ("一、文件与目录", list(range(1, 5))),
        ("二、进程与系统监控", list(range(5, 9))),
        ("三、网络与调试工具", list(range(9, 13))),
        ("四、Shell 与脚本", list(range(13, 16))),
    ],
    "18-serial-usb-hid.md": [
        ("一、串口通信", list(range(1, 6))),
        ("二、USB 协议", list(range(6, 11))),
        ("三、HID 设备", list(range(11, 16))),
    ],
    "19-cmake.md": [
        ("一、CMake 基础", list(range(1, 5))),
        ("二、目标与依赖管理", list(range(5, 10))),
        ("三、跨平台与高级特性", list(range(10, 13))),
        ("四、实战技巧", list(range(13, 16))),
    ],
    "20-templates.md": [
        ("一、模板基础", list(range(1, 6))),
        ("二、模板特化与偏特化", list(range(6, 11))),
        ("三、模板元编程", list(range(11, 16))),
    ],
    "21-cpp20.md": [
        ("一、Concepts 与约束", list(range(1, 5))),
        ("二、Ranges 与视图", list(range(5, 8))),
        ("三、协程", list(range(8, 11))),
        ("四、其他新特性", list(range(11, 16))),
    ],
    "22-stl.md": [
        ("一、容器", list(range(1, 6))),
        ("二、迭代器与算法", list(range(6, 11))),
        ("三、函数对象与适配器", list(range(11, 16))),
    ],
    "23-move-semantics.md": [
        ("一、右值引用基础", list(range(1, 5))),
        ("二、移动构造与赋值", list(range(5, 9))),
        ("三、完美转发", list(range(9, 12))),
        ("四、实践场景", list(range(12, 16))),
    ],
    "24-exceptions.md": [
        ("一、异常基础", list(range(1, 6))),
        ("二、异常安全", list(range(6, 11))),
        ("三、最佳实践", list(range(11, 16))),
    ],
    "25-memory-model.md": [
        ("一、内存序基础", list(range(1, 5))),
        ("二、原子操作", list(range(5, 9))),
        ("三、内存屏障与 happens-before", list(range(9, 13))),
        ("四、无锁编程", list(range(13, 16))),
    ],
    "26-compile-link-abi.md": [
        ("一、编译过程", list(range(1, 5))),
        ("二、链接与符号", list(range(5, 10))),
        ("三、ABI 与二进制兼容", list(range(10, 13))),
        ("四、工程实践", list(range(13, 16))),
    ],
    "27-performance.md": [
        ("一、性能分析方法", list(range(1, 5))),
        ("二、CPU 与缓存优化", list(range(5, 9))),
        ("三、内存与算法优化", list(range(9, 13))),
        ("四、工具与实践", list(range(13, 16))),
    ],
    "28-networking.md": [
        ("一、网络基础", list(range(1, 5))),
        ("二、TCP/UDP", list(range(5, 9))),
        ("三、Socket 编程", list(range(9, 13))),
        ("四、高性能网络", list(range(13, 16))),
    ],
    "29-database.md": [
        ("一、SQL 基础", list(range(1, 5))),
        ("二、索引与查询优化", list(range(5, 9))),
        ("三、事务与并发", list(range(9, 13))),
        ("四、C++ 数据库实践", list(range(13, 16))),
    ],
    "30-git.md": [
        ("一、基础操作", list(range(1, 5))),
        ("二、分支与合并", list(range(5, 9))),
        ("三、协作与工作流", list(range(9, 13))),
        ("四、高级操作", list(range(13, 16))),
    ],
    "31-software-engineering.md": [
        ("一、设计原则", list(range(1, 5))),
        ("二、架构与重构", list(range(5, 9))),
        ("三、测试与质量", list(range(9, 13))),
        ("四、工程文化", list(range(13, 16))),
    ],
    "32-scenario-design.md": [
        ("一、系统设计基础", list(range(1, 5))),
        ("二、常见系统设计题", list(range(5, 10))),
        ("三、扩展与容灾", list(range(10, 13))),
        ("四、实战思路", list(range(13, 16))),
    ],
    "33-project-experience.md": [
        ("一、项目描述技巧", list(range(1, 5))),
        ("二、技术难点问答", list(range(5, 10))),
        ("三、团队协作与复盘", list(range(10, 13))),
        ("四、成长与反思", list(range(13, 16))),
    ],
    "34-interview-skills.md": [
        ("一、面试准备", list(range(1, 5))),
        ("二、现场应对", list(range(5, 9))),
        ("三、技术答题技巧", list(range(9, 13))),
        ("四、offer 谈判", list(range(13, 16))),
    ],
    "35-comprehensive.md": [
        ("一、C++ 高频综合", list(range(1, 5))),
        ("二、Qt 高频综合", list(range(5, 9))),
        ("三、系统设计综合", list(range(9, 13))),
        ("四、工程实战综合", list(range(13, 16))),
    ],
    "36-gis.md": [
        ("一、GIS 基础", list(range(1, 6))),
        ("二、地图渲染与投影", list(range(6, 11))),
        ("三、空间数据与算法", list(range(11, 16))),
    ],
    "37-redis.md": [
        ("一、数据结构", list(range(1, 5))),
        ("二、持久化与高可用", list(range(5, 10))),
        ("三、缓存设计", list(range(10, 14))),
        ("四、集群与性能", list(range(14, 18))),
    ],
    "38-kalman.md": [
        ("一、滤波基础", list(range(1, 6))),
        ("二、卡尔曼滤波原理", list(range(6, 11))),
        ("三、扩展应用", list(range(11, 16))),
    ],
    "39-pid.md": [
        ("一、控制基础", list(range(1, 5))),
        ("二、PID 原理与调参", list(range(5, 10))),
        ("三、工程实现", list(range(10, 13))),
        ("四、高级变种", list(range(13, 16))),
    ],
    "40-cpp-csharp.md": [
        ("一、语言对比", list(range(1, 5))),
        ("二、内存与资源管理", list(range(5, 9))),
        ("三、并发模型", list(range(9, 13))),
        ("四、生态与选型", list(range(13, 16))),
    ],
    "41-electron.md": [
        ("一、架构与原理", list(range(1, 5))),
        ("二、进程通信", list(range(5, 9))),
        ("三、安全与性能", list(range(9, 13))),
        ("四、跨平台实践", list(range(13, 16))),
    ],
    "42-embedded-protocol.md": [
        ("一、通信协议基础", list(range(1, 5))),
        ("二、主流嵌入式协议", list(range(5, 10))),
        ("三、协议栈实现", list(range(10, 13))),
        ("四、调试与可靠性", list(range(13, 16))),
    ],
    "43-qt-qml.md": [
        ("一、QML 基础", list(range(1, 5))),
        ("二、Qt Quick 组件", list(range(5, 9))),
        ("三、C++ 与 QML 交互", list(range(9, 13))),
        ("四、性能与实践", list(range(13, 16))),
    ],
    "44-debugging-profiling.md": [
        ("一、调试工具", list(range(1, 5))),
        ("二、内存问题", list(range(5, 9))),
        ("三、性能分析", list(range(9, 13))),
        ("四、生产环境诊断", list(range(13, 16))),
    ],
    "45-cross-platform.md": [
        ("一、跨平台基础", list(range(1, 5))),
        ("二、平台差异处理", list(range(5, 9))),
        ("三、构建与打包", list(range(9, 13))),
        ("四、实战经验", list(range(13, 16))),
    ],
    "46-llm-basics.md": [
        ("一、LLM 基础", list(range(1, 5))),
        ("二、RAG 与向量检索", list(range(5, 9))),
        ("三、Prompt 工程", list(range(9, 13))),
        ("四、应用开发实践", list(range(13, 16))),
    ],
    "47-ml-optimization.md": [
        ("一、模型压缩基础", list(range(1, 5))),
        ("二、量化与剪枝", list(range(5, 9))),
        ("三、推理优化", list(range(9, 13))),
        ("四、部署实践", list(range(13, 16))),
    ],
    "48-ai-engineering.md": [
        ("一、AI 系统架构", list(range(1, 5))),
        ("二、训练与评估", list(range(5, 9))),
        ("三、生产部署", list(range(9, 13))),
        ("四、工程化最佳实践", list(range(13, 16))),
    ],
    "49-data-structures.md": [
        ("一、线性结构", list(range(1, 9))),
        ("二、树结构", list(range(9, 18))),
        ("三、堆", list(range(18, 21))),
        ("四、哈希表", list(range(21, 26))),
        ("五、图", list(range(26, 32))),
        ("六、高频综合题", list(range(32, 38))),
    ],
    "50-algorithms.md": [
        ("一、复杂度分析", list(range(1, 3))),
        ("二、排序算法", list(range(3, 12))),
        ("三、查找算法", list(range(12, 16))),
        ("四、动态规划", list(range(16, 25))),
        ("五、图算法", list(range(25, 31))),
        ("六、贪心算法", list(range(31, 33))),
        ("七、字符串算法", list(range(33, 38))),
        ("八、递归与分治", list(range(38, 40))),
        ("九、高频面试题", list(range(40, 45))),
    ],
}

# 每章节大节的概述文字
SECTION_NOTES = {
    "一、线性结构": "数组、链表、栈、队列的底层实现与 STL 容器对应关系，是面试必考基础",
    "二、树结构": "二叉树四种遍历、BST、AVL、红黑树、B/B+ 树，重点掌握时间复杂度与实现原理",
    "三、堆": "堆的性质、priority_queue 用法、Top-K 问题，堆排序是考察重点",
    "四、哈希表": "哈希冲突处理、unordered_map vs map、负载因子，工程中使用频率极高",
    "五、图": "图的存储方式、BFS/DFS、最短路径、最小生成树，系统设计中常用",
    "六、高频综合题": "LRU/LFU Cache、Top-K、布隆过滤器等经典面试综合题",
    "一、复杂度分析": "时间/空间复杂度分析是算法题的基础，主定理和摊销分析是难点",
    "二、排序算法": "快排、归并、堆排三种 O(nlogn) 排序及线性排序，必须能手写快排和归并",
    "三、查找算法": "二分查找变体是高频考点，BST/红黑树/B+树查找场景对比",
    "四、动态规划": "DP 的核心是状态定义和转移方程，背包/LCS/LIS/编辑距离是经典题型",
    "五、图算法": "BFS/DFS/Dijkstra/拓扑排序/最小生成树，掌握复杂度和适用场景",
    "六、贪心算法": "局部最优推全局最优，证明贪心正确性是难点",
    "七、字符串算法": "KMP/Rabin-Karp/滑动窗口/双指针，字符串题是算法面试高频",
    "八、递归与分治": "分治思想贯穿排序/查找/DP，尾递归优化和栈溢出是工程关注点",
    "九、高频面试题": "接雨水、三数之和、N皇后等经典综合题，考察多种算法融合应用",
}

# 每道题追问（按文件名+Q编号）— 这里放通用追问，特殊题用关键词匹配
FOLLOWUP_BY_KEYWORD = {
    "vector": "vector 扩容时迭代器为何失效？如何用 `reserve` 优化？`std::deque` 和 `vector` 底层有何不同？",
    "链表": "链表反转怎么实现？如何检测环？为什么实际性能不如 vector？",
    "红黑树": "红黑树和 AVL 树各自适合什么场景？STL 为何选红黑树而不是 AVL？",
    "快速排序": "快排最坏情况是什么？三路快排如何解决重复元素问题？",
    "动态规划": "如何识别 DP 问题？状态压缩空间优化的原则是什么？",
    "RAII": "与 GC 相比 RAII 的优势是什么？异常抛出时 RAII 为何仍然可靠？",
    "虚函数": "虚函数表是什么时候创建的？多继承时 vptr 有几个？",
    "智能指针": "shared_ptr 的引用计数是线程安全的吗？weak_ptr 如何打破循环引用？",
    "线程": "线程池的核心参数如何调优？线程数设多少合适？",
    "信号槽": "信号槽与回调函数相比有何优劣？跨线程信号槽如何工作？",
    "移动语义": "什么情况下移动构造函数会被隐式调用？`std::move` 后原对象的状态？",
    "模板": "模板编译期展开有什么代价？如何减少模板实例化导致的代码膨胀？",
    "内存": "内存泄漏如何定位？Valgrind 和 AddressSanitizer 各自适合什么场景？",
    "锁": "互斥锁和自旋锁各自适合什么场景？如何避免死锁？",
    "哈希": "哈希表扩容时为什么要 rehash？哈希冲突严重时会退化到什么复杂度？",
    "排序": "std::sort 使用什么算法？为什么不用归并排序？什么时候用 stable_sort？",
}

DEFAULT_FOLLOWUP = "这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？"

def get_followup(title, content):
    """根据题目标题和内容选择追问"""
    combined = title + content
    for kw, fup in FOLLOWUP_BY_KEYWORD.items():
        if kw in combined:
            return fup
    return DEFAULT_FOLLOWUP

def count_difficulties(lines):
    green = sum(1 for l in lines if '🟢' in l and l.startswith('### Q'))
    yellow = sum(1 for l in lines if '🟡' in l and l.startswith('### Q'))
    red = sum(1 for l in lines if '🔴' in l and l.startswith('### Q'))
    return green, yellow, red

def parse_questions(lines):
    """解析出所有题目的位置和内容，返回 [(q_num, start_line, end_line, title)]"""
    questions = []
    q_pattern = re.compile(r'^### Q(\d+):')
    for i, line in enumerate(lines):
        m = q_pattern.match(line)
        if m:
            questions.append((int(m.group(1)), i))
    # 计算每题结束位置
    result = []
    for idx, (qnum, start) in enumerate(questions):
        end = questions[idx+1][1] if idx+1 < len(questions) else len(lines)
        title = lines[start].strip()
        result.append((qnum, start, end, title))
    return result

def already_has_followup(block_lines):
    return any('💡' in l and '面试追问' in l for l in block_lines)

def add_followup_to_block(block_lines, followup_text):
    """在题目块末尾（统计表之前）加追问"""
    # 找最后一个非空行
    last_non_empty = len(block_lines) - 1
    while last_non_empty >= 0 and not block_lines[last_non_empty].strip():
        last_non_empty -= 1
    # 在最后非空行后插入
    insert_pos = last_non_empty + 1
    followup = [
        "\n",
        f"> 💡 **面试追问**：{followup_text}\n",
        "\n",
    ]
    return block_lines[:insert_pos] + followup + block_lines[insert_pos:]

def build_grouping_map(groupings):
    """返回 {q_num: 分组标题}"""
    mapping = {}
    for group_title, q_nums in groupings:
        for q in q_nums:
            mapping[q] = group_title
    return mapping

def process_file(filepath, groupings):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.splitlines(keepends=True)

    # 找到头部结束位置（--- 分隔符后）
    header_end = 0
    dash_count = 0
    for i, line in enumerate(lines):
        if line.strip() == '---':
            dash_count += 1
            if dash_count == 1:
                header_end = i + 1
                break

    # 找到尾部统计开始位置
    stats_start = len(lines)
    for i, line in enumerate(lines):
        if line.strip() == '## 📊 本章统计':
            stats_start = i
            break

    body_lines = lines[header_end:stats_start]
    stats_lines = lines[stats_start:]

    # 解析题目
    questions = parse_questions(body_lines)
    if not questions:
        print(f"  跳过（无题目）: {os.path.basename(filepath)}")
        return

    # 构建分组映射
    group_map = build_grouping_map(groupings) if groupings else {}

    # 重新构建 body：插入分组标题 + 追问
    new_body = []
    current_group = None
    # 找 body 开头的内容（题目之前可能有的内容）
    first_q_start = questions[0][1]
    pre_q_content = body_lines[:first_q_start]
    # 清理 pre_q_content 中已有的分组标题（避免重复）
    pre_q_filtered = [l for l in pre_q_content if not (l.startswith('## ') and not l.startswith('## 📊'))]
    new_body.extend(pre_q_filtered)

    for qnum, start, end, title in questions:
        block = body_lines[start:end]

        # 检查是否需要插入新的分组标题
        desired_group = group_map.get(qnum)
        if desired_group and desired_group != current_group:
            current_group = desired_group
            note = SECTION_NOTES.get(desired_group, "")
            new_body.append('\n')
            new_body.append(f'## {desired_group}\n')
            new_body.append('\n')
            if note:
                new_body.append(f'> 📌 **本节重点**：{note}\n')
                new_body.append('\n')

        # 加追问（如果还没有）
        if not already_has_followup(block):
            block_content = ''.join(block)
            followup = get_followup(title, block_content)
            block = add_followup_to_block(block, followup)

        new_body.extend(block)

    # 更新难度统计
    all_lines = lines[:header_end] + new_body + stats_lines
    green, yellow, red = count_difficulties(all_lines)
    total_q = len(questions)

    # 更新头部难度行
    new_all = []
    for line in all_lines:
        if line.startswith('> 难度分布：'):
            line = f'> 难度分布：🟢 入门 {green} 题 · 🟡 进阶 {yellow} 题 · 🔴 高难 {red} 题\n'
        new_all.append(line)

    # 更新尾部统计
    final_lines = []
    in_stats = False
    for line in new_all:
        if line.strip() == '## 📊 本章统计':
            in_stats = True
            final_lines.append(line)
            continue
        if in_stats:
            # 替换统计表
            pass
        else:
            final_lines.append(line)

    # 重建尾部统计
    final_content = ''.join(final_lines).rstrip()
    # 移除已有统计块
    stats_marker = '## 📊 本章统计'
    if stats_marker in final_content:
        final_content = final_content[:final_content.index(stats_marker)].rstrip()

    final_content += f"""

---

## 📊 本章统计

| 指标 | 数量 |
|------|------|
| 总题目数 | {total_q} |
| 🟢 入门 | {green} |
| 🟡 进阶 | {yellow} |
| 🔴 高难 | {red} |
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"  ✅ {os.path.basename(filepath)}: {total_q} 题, 分 {len(groupings) if groupings else 0} 组, 绿{green}/黄{yellow}/红{red}")

def main():
    guide_dir = GUIDE_DIR
    processed = 0
    for filename, groupings in GROUPINGS.items():
        filepath = os.path.join(guide_dir, filename)
        if not os.path.exists(filepath):
            print(f"  ⚠️  文件不存在: {filename}")
            continue
        try:
            process_file(filepath, groupings)
            processed += 1
        except Exception as e:
            print(f"  ❌ {filename}: {e}")
            import traceback; traceback.print_exc()

    print(f"\n完成: {processed} 个文件")

if __name__ == '__main__':
    main()
