# 🗺️ C++/Qt 桌面开发工程师面试学习路线

> 本路线图基于 [huihut/interview](https://github.com/huihut/interview) 和 [0voice/qt_interview_reference](https://github.com/0voice/qt_interview_reference) 的知识体系，结合实际面试经验整理而成。

---

## 📐 学习路线总览

```
基础夯实 → 进阶突破 → 工程化实践 → 系统设计 → 面试冲刺
```

---

## 阶段一：基础夯实（1~2 周）

**目标**：掌握 C++ 现代特性和 Qt 框架核心机制

| 章节 | 重点 |
|------|------|
| [Qt 框架基础](/guide/01-qt-basics) | 信号槽、元对象系统、事件循环 |
| [C++11/14/17 新特性](/guide/02-cpp11-14-17) | auto、lambda、右值引用、nullptr |
| [C++ 核心基础](/guide/03-cpp-core) | 内存布局、虚函数表、继承 |
| [多态与虚函数](/guide/04-polymorphism) | 多态原理、虚函数表结构 |
| [virtual 关键字](/guide/05-virtual) | 纯虚函数、析构函数虚化 |

---

## 阶段二：进阶突破（2~3 周）

**目标**：深入理解 Qt 核心机制，掌握并发编程

| 章节 | 重点 |
|------|------|
| [Qt 核心机制](/guide/06-qt-core) | QObject 内存管理、父子关系、线程亲和性 |
| [并发与并行](/guide/07-concurrency) | mutex、condition_variable、atomic |
| [消息队列](/guide/08-message-queue) | 线程间通信、队列设计 |
| [线程池](/guide/10-thread-pool) | 线程池实现、任务调度 |
| [智能指针深入](/guide/15-smart-pointers) | shared_ptr 原理、循环引用、weak_ptr |
| [移动语义](/guide/23-move-semantics) | 右值引用、完美转发、RVO |
| [内存模型与原子操作](/guide/25-memory-model) | memory_order、happens-before |

---

## 阶段三：工程化实践（1~2 周）

**目标**：掌握工程开发必备技能，覆盖通信/Linux/构建系统

| 章节 | 重点 |
|------|------|
| [C++ 消息与通信](/guide/12-messaging) | 协议设计、序列化 |
| [串口与 USB/HID](/guide/18-serial-usb-hid) | 串口通信、HID 设备 |
| [Linux 系统编程](/guide/16-linux-programming) | 进程/线程、文件 I/O、信号 |
| [Linux 命令与调试](/guide/17-linux-commands) | gdb、valgrind、strace |
| [CMake 构建系统](/guide/19-cmake) | 现代 CMake、target_xxx 用法 |
| [Qt5 与 Qt6 区别](/guide/09-qt5-qt6) | API 差异、迁移要点 |
| [模板与泛型](/guide/20-templates) | SFINAE、类型萃取、concept |
| [编译链接与 ABI](/guide/26-compile-link-abi) | 符号修饰、动态库 |

---

## 阶段四：系统设计（1 周）

**目标**：能够设计中等规模系统，理解架构权衡

| 章节 | 重点 |
|------|------|
| [设计模式](/guide/14-design-patterns) | 23 种 GoF 模式，重点：单例/工厂/观察者/策略 |
| [软件工程与设计原则](/guide/31-software-engineering) | SOLID 原则、重构技巧 |
| [场景设计题](/guide/32-scenario-design) | 日志系统、配置管理、插件框架 |
| [性能优化](/guide/27-performance) | 缓存优化、锁竞争、内存池 |
| [网络编程](/guide/28-networking) | TCP/UDP、epoll、异步 I/O |
| [STL 深入](/guide/22-stl) | 容器选型、迭代器失效、算法复杂度 |

---

## 阶段五：面试冲刺（3~5 天）

**目标**：查漏补缺，练习表达，熟悉高频题

| 章节 | 重点 |
|------|------|
| [高频综合题](/guide/35-comprehensive) | 综合性问题，快速过一遍 |
| [项目经验问答](/guide/33-project-experience) | STAR 法则，准备 2~3 个项目亮点 |
| [面试实战技巧](/guide/34-interview-skills) | 白板编程、系统设计面技巧 |
| [C++20 新特性](/guide/21-cpp20) | Concept、协程、ranges |
| [异常处理](/guide/24-exceptions) | noexcept、异常安全保证 |

---

## 🔥 高频考点 TOP 10

以下是 C++/Qt 桌面开发面试中出现频率最高的 10 个考点：

| # | 考点 | 所在章节 | 出现频率 |
|---|------|---------|---------|
| 1 | 虚函数表结构与多态实现原理 | [多态与虚函数](/guide/04-polymorphism) | ⭐⭐⭐⭐⭐ |
| 2 | shared_ptr 实现原理与循环引用 | [智能指针深入](/guide/15-smart-pointers) | ⭐⭐⭐⭐⭐ |
| 3 | Qt 信号槽底层机制 | [Qt 核心机制](/guide/06-qt-core) | ⭐⭐⭐⭐⭐ |
| 4 | C++ 内存管理（new/delete/malloc 区别） | [C++ 核心基础](/guide/03-cpp-core) | ⭐⭐⭐⭐⭐ |
| 5 | 右值引用与移动语义 | [移动语义](/guide/23-move-semantics) | ⭐⭐⭐⭐ |
| 6 | mutex/lock 的正确用法与死锁 | [并发与并行](/guide/07-concurrency) | ⭐⭐⭐⭐ |
| 7 | Qt 线程安全与跨线程信号槽 | [Qt 核心机制](/guide/06-qt-core) | ⭐⭐⭐⭐ |
| 8 | 设计模式（单例/工厂/观察者） | [设计模式](/guide/14-design-patterns) | ⭐⭐⭐⭐ |
| 9 | STL 容器选型与迭代器失效 | [STL 深入](/guide/22-stl) | ⭐⭐⭐ |
| 10 | Lambda 表达式与捕获列表 | [C++11/14/17 新特性](/guide/02-cpp11-14-17) | ⭐⭐⭐ |

---

## 📋 刷题策略

### 按难度刷

```
入门（直接给答案类）→ 中等（需要分析/推导）→ 困难（系统设计/手写代码）
```

- **入门**：Qt 基础、Linux 命令、CMake 语法
- **中等**：虚函数表、智能指针实现、线程池设计
- **困难**：设计模式综合应用、场景设计题、内存模型

### 按模块刷（推荐）

适合有时间规划的候选人，按模块深度掌握：

1. 先把 **C++ 核心** 的 12 个章节过一遍
2. 再攻 **Qt 框架** + **并发/线程**（核心竞争力）
3. **通信/协议** 和 **Linux/工程化** 做补充
4. 最后冲刺 **项目/面试** 三章

### 按时间刷

| 时间 | 建议 |
|------|------|
| 1 周 | 重点刷 TOP 10 高频考点 |
| 2 周 | 完整过 C++ 核心 + Qt 框架 |
| 1 个月 | 全部 42 章系统覆盖 |

---

## 📚 参考资料

- **[huihut/interview](https://github.com/huihut/interview)** — C/C++ 技术面试基础知识总结，Star 30k+，是最全面的 C++ 面试知识体系
- **[0voice/qt_interview_reference](https://github.com/0voice/qt_interview_reference)** — Qt 面试题参考，覆盖 Qt 核心机制
- **《Effective Modern C++》** — Scott Meyers 著，C++ 现代特性最权威的参考书
- **《Qt 5/6 官方文档》** — https://doc.qt.io
- **cppreference.com** — C++ 标准库最权威的在线参考

---

> 💡 **建议**：面试准备不只是背题目，更重要的是理解原理、能够举一反三。遇到不会的题先想思路，再查资料，最后用自己的话复述一遍。
