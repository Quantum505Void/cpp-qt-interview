#!/usr/bin/env python3
"""
为核心章节注入 Mermaid 图
策略：在每章第一个大节（## 一、...）后插入一张整体结构图
"""
import re, os

GUIDE_DIR = "docs/guide"

# {文件名: [(插入位置关键词, mermaid图内容)]}
MERMAID_INJECTIONS = {
    "49-data-structures.md": [
        ("## 一、线性结构", """
```mermaid
graph LR
    arr["数组 Array\\n连续内存, O(1)访问"] 
    vec["vector\\n动态数组, 2x扩容"]
    lst["list\\n双向链表, O(1)插删"]
    dq["deque\\n分段连续内存"]
    arr --> vec
    arr --> dq
    lst --> |"底层"| dq

    style arr fill:#e8f4f8
    style vec fill:#d4edda
    style lst fill:#d4edda
    style dq fill:#d4edda
```
"""),
        ("## 二、树结构", """
```mermaid
graph TD
    root["根节点 50"]
    l["左子节点 30"]
    r["右子节点 40"]
    ll["20"]
    lr["25"]
    rl["35"]
    rr["45"]
    root --> l
    root --> r
    l --> ll
    l --> lr
    r --> rl
    r --> rr
    style root fill:#ffd700
    style l fill:#98fb98
    style r fill:#98fb98
```

> BST 性质：左子树所有节点 < 根 < 右子树所有节点，中序遍历得到有序序列。
"""),
        ("## 四、哈希表", """
```mermaid
graph LR
    subgraph chaining["链地址法（std::unordered_map）"]
        b0["桶0"] --> a0["key:A"]
        a0 --> a1["key:D（冲突）"]
        b1["桶1"] --> b10["key:B"]
        b2["桶2"] --> c0["key:C"]
    end
    subgraph probe["开放寻址法"]
        p0["idx=0: A"]
        p1["idx=1: D（探测后移）"]
        p2["idx=2: B"]
    end
```
"""),
        ("## 五、图", """
```mermaid
graph LR
    subgraph bfs_order["BFS 层序遍历"]
        b1["1(起点)"] --> b2["2"] & b3["3"]
        b2 --> b4["4"] & b5["5"]
    end
    subgraph dfs_order["DFS 深度优先"]
        d1["1"] --> d2["2"] --> d4["4"] --> d5["5(回溯)"] --> d3["3"]
    end
```
"""),
    ],
    "50-algorithms.md": [
        ("## 二、排序算法", """
| 算法 | 平均 | 最坏 | 空间 | 稳定 | 适用场景 |
|------|------|------|------|------|---------|
| 冒泡 | O(n²) | O(n²) | O(1) | ✅ | 教学 |
| 选择 | O(n²) | O(n²) | O(1) | ❌ | 小数据 |
| 插入 | O(n²) | O(n²) | O(1) | ✅ | 近乎有序 |
| 快排 | O(nlogn) | O(n²) | O(logn) | ❌ | **通用首选** |
| 归并 | O(nlogn) | O(nlogn) | O(n) | ✅ | 链表/外排序 |
| 堆排 | O(nlogn) | O(nlogn) | O(1) | ❌ | Top-K |
| 计数 | O(n+k) | O(n+k) | O(k) | ✅ | 整数/范围小 |
| 基数 | O(nk) | O(nk) | O(n) | ✅ | 多位整数 |

```mermaid
graph TD
    A["归并排序 [5,3,8,1,2]"]
    B["左半 [5,3,8]"]
    C["右半 [1,2]"]
    D["[5,3]"]
    E["[8]"]
    F["[5]"]
    G["[3]"]
    H["合并 [3,5]"]
    I["合并 [3,5,8]"]
    J["合并 [1,2]"]
    K["最终 [1,2,3,5,8]"]
    A --> B & C
    B --> D & E
    D --> F & G
    F & G --> H
    H & E --> I
    C --> J
    I & J --> K
```
"""),
        ("## 三、查找算法", """
| 算法 | 平均复杂度 | 前提条件 | 适用场景 |
|------|-----------|---------|---------|
| 顺序查找 | O(n) | 无 | 无序小数据 |
| 二分查找 | O(logn) | **有序** | 静态有序数组 |
| 插值查找 | O(log logn) | 均匀有序 | 均匀分布数据 |
| 哈希查找 | O(1) | 哈希表 | 精确匹配 |
| BST 查找 | O(logn) | BST | 动态维护有序 |
| B+ 树查找 | O(logn) | B+ 树 | **数据库索引** |
"""),
        ("## 四、动态规划", """
```mermaid
graph LR
    s0["dp[i-1][j]\\n不选第i件"] -->|"max"| s1["dp[i][j]"]
    s2["dp[i-1][j-w[i]] + v[i]\\n选第i件(容量够)"] -->|"max"| s1
    style s1 fill:#ffd700
```

> 0-1背包核心：`dp[i][j] = max(dp[i-1][j], dp[i-1][j-w[i]] + v[i])`，空间可优化为一维。
"""),
        ("## 五、图算法", """
```mermaid
graph LR
    S["S(dist=0)"]
    A["A(dist=∞)"]
    B["B(dist=∞)"]
    T["T(dist=∞)"]
    S -->|"4"| A
    S -->|"2"| B
    B -->|"1"| A
    A -->|"3"| T
    
    S2["S(0)"] -->|松弛| A2["A(3)"]
    S2 -->|松弛| B2["B(2)"]
    A2 -->|松弛| T2["T(6)"]
```

> Dijkstra 核心：每次取 dist 最小的未访问节点，松弛其邻居。贪心正确性依赖**非负权边**。
"""),
    ],
    "07-concurrency.md": [
        ("## 一、线程基础", """
```mermaid
graph LR
    subgraph states["线程状态机"]
        new["新建 New"] -->|"start()"| ready["就绪 Runnable"]
        ready -->|"获得CPU"| run["运行 Running"]
        run -->|"时间片用完"| ready
        run -->|"wait/sleep"| blocked["阻塞 Blocked"]
        blocked -->|"notify/超时"| ready
        run -->|"run()结束"| dead["终止 Terminated"]
    end
```
"""),
        ("## 二、同步原语", """
```mermaid
graph TD
    mutex["mutex 互斥锁\\n同一时刻只有1个线程持有"]
    rw["shared_mutex 读写锁\\n多读单写"]
    sem["semaphore 信号量\\n控制并发数量"]
    cv["condition_variable\\n条件等待+通知"]
    atomic["atomic 原子操作\\n无锁, 最轻量"]
    
    atomic -->|"最快"| mutex -->|"通用"| rw -->|"读多写少"| sem
    cv -->|"配合"| mutex
```
"""),
    ],
    "14-design-patterns.md": [
        ("## 一、创建型模式", """
```mermaid
graph LR
    subgraph creational["创建型"]
        singleton["单例\\nSingleton"]
        factory["工厂\\nFactory"]
        abstract["抽象工厂\\nAbstract Factory"]
        builder["建造者\\nBuilder"]
        prototype["原型\\nPrototype"]
    end
    subgraph structural["结构型"]
        adapter["适配器\\nAdapter"]
        decorator["装饰器\\nDecorator"]
        proxy["代理\\nProxy"]
        facade["外观\\nFacade"]
    end
    subgraph behavioral["行为型"]
        observer["观察者\\nObserver"]
        strategy["策略\\nStrategy"]
        command["命令\\nCommand"]
        state["状态\\nState"]
    end
```
"""),
    ],
    "15-smart-pointers.md": [
        ("## 一、智能指针基础", """
```mermaid
graph TD
    raw["裸指针 T*\\n手动 new/delete\\n容易泄漏"]
    unique["unique_ptr\\n独占所有权\\n不可复制, 可移动"]
    shared["shared_ptr\\n共享所有权\\n引用计数"]
    weak["weak_ptr\\n弱引用\\n不增加计数, 打破循环"]
    
    raw -->|"升级"| unique
    raw -->|"升级"| shared
    shared -->|"配合"| weak
    
    style raw fill:#ffcccc
    style unique fill:#ccffcc
    style shared fill:#ccffcc
    style weak fill:#ffffcc
```
"""),
    ],
    "25-memory-model.md": [
        ("## 一、内存序基础", """
```mermaid
graph LR
    subgraph orders["内存序从强到弱"]
        seq["seq_cst\\n顺序一致(最强)\\n性能最差"]
        acqrel["acquire/release\\n获取释放语义\\n推荐"]
        consume["consume\\n数据依赖顺序"]
        relax["relaxed\\n无顺序约束(最弱)\\n性能最好"]
        seq --> acqrel --> consume --> relax
    end
```

> 选择原则：默认用 `seq_cst`，性能敏感时改为 `acquire/release`，纯计数器用 `relaxed`。
"""),
    ],
    "23-move-semantics.md": [
        ("## 一、右值引用基础", """
```mermaid
graph LR
    lval["左值 lvalue\\n有名字, 有地址\\nint x = 5"]
    rval["右值 rvalue\\n临时, 无持久地址\\nint&&, 5, std::move(x)"]
    move["移动语义\\n转移资源所有权\\n避免深拷贝"]
    fwd["完美转发\\nstd::forward<T>()\\n保持值类别"]
    
    lval -->|"std::move()"| rval
    rval -->|"触发"| move
    fwd -->|"处理"| lval & rval
```
"""),
    ],
    "06-qt-core.md": [
        ("## 一、元对象系统", """
```mermaid
graph TD
    qobject["QObject\\n所有Qt对象基类"]
    moc["moc 元对象编译器\\n处理 Q_OBJECT 宏"]
    meta["元对象 QMetaObject\\n类型信息/方法/属性"]
    signal["信号 signal\\n事件通知机制"]
    slot["槽 slot\\n信号处理函数"]
    prop["属性 Q_PROPERTY\\n运行时反射"]
    
    qobject -->|"需要"| moc
    moc -->|"生成"| meta
    meta --> signal & slot & prop
    signal -->|"connect()"| slot
```
"""),
    ],
    "01-qt-basics.md": [
        ("## 一、Qt 概览与架构", """
```mermaid
graph TD
    qt["Qt 框架"]
    core["QtCore\\n基础类/容器/IO"]
    gui["QtGui\\n2D绘图/图像"]
    widgets["QtWidgets\\n传统桌面控件"]
    qml["QtQml/Quick\\n现代声明式UI"]
    network["QtNetwork\\nHTTP/Socket"]
    sql["QtSql\\n数据库"]
    
    qt --> core & gui & widgets & qml & network & sql
    gui --> widgets
    gui --> qml
```
"""),
    ],
    "22-stl.md": [
        ("## 一、容器", """
| 容器 | 底层结构 | 访问 | 插入/删除 | 有序 | 可重复 |
|------|---------|------|---------|------|-------|
| vector | 动态数组 | O(1) | 末尾O(1)/中间O(n) | ❌ | ✅ |
| deque | 分段数组 | O(1) | 两端O(1) | ❌ | ✅ |
| list | 双向链表 | O(n) | O(1) | ❌ | ✅ |
| map | 红黑树 | O(logn) | O(logn) | ✅ | ❌ |
| unordered_map | 哈希表 | O(1) | O(1)均摊 | ❌ | ❌ |
| set | 红黑树 | O(logn) | O(logn) | ✅ | ❌ |
| priority_queue | 堆 | O(1)top | O(logn) | 按priority | ✅ |
"""),
    ],
    "20-templates.md": [
        ("## 一、模板基础", """
```mermaid
graph LR
    source["源代码\\ntemplate<T>"]
    inst["模板实例化\\n编译期展开"]
    spec["模板特化\\n针对特定类型优化"]
    partial["偏特化\\n部分类型约束"]
    meta["模板元编程\\n编译期计算"]
    
    source -->|"编译"| inst
    inst -->|"优化"| spec
    spec -->|"灵活"| partial
    meta -->|"基于"| inst
```
"""),
    ],
}

def inject_mermaid(filepath, injections):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    for marker, diagram in injections:
        if marker not in content:
            print(f"    ⚠️  找不到标记: {marker}")
            continue
        if '```mermaid' in diagram and '```mermaid' in content[content.index(marker):content.index(marker)+500]:
            print(f"    ⏭️  已有图: {marker}")
            continue
        # 在 marker 行后找到空行，插入图
        idx = content.index(marker)
        # 找 marker 行结束
        line_end = content.index('\n', idx) + 1
        # 找下一个非空行（📌 概述后面）
        insert_after = line_end
        # 找 > 📌 行，在它后面插
        peek = content[line_end:line_end+200]
        if peek.startswith('\n> 📌'):
            note_end = content.index('\n', line_end + 1) + 1
            # 找note行后的空行
            insert_after = note_end
            if content[insert_after] == '\n':
                insert_after += 1

        content = content[:insert_after] + '\n' + diagram + '\n' + content[insert_after:]
        print(f"    ✅ 注入图: {marker[:30]}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    for filename, injections in MERMAID_INJECTIONS.items():
        filepath = os.path.join(GUIDE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"⚠️  {filename} 不存在")
            continue
        print(f"📊 {filename}")
        inject_mermaid(filepath, injections)

if __name__ == '__main__':
    main()
