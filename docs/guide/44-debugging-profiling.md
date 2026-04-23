# 44. 调试与性能分析

> 难度分布：🟢 入门 2 题 · 🟡 进阶 11 题 · 🔴 高难 2 题

[[toc]]

---


## 一、调试工具

### Q1: ⭐🟢 C++ 程序 Segmentation Fault 怎么快速定位？


A: 结论：优先用 `gdb`（事后分析 core dump 或附加调试），辅以 `AddressSanitizer`（ASAN）在编译阶段开启，能精确报告越界/野指针位置。


详细解释：


```bash
# 1. 编译时加调试符号 + ASAN
g++ -g -fsanitize=address -o myapp main.cpp

# 2. 运行，ASAN 直接打印出问题位置和调用栈

# 3. 事后 core dump 分析（需先 ulimit -c unlimited）
gdb ./myapp core
(gdb) bt   # 打印调用栈
(gdb) frame 3  # 切换到第 3 帧
(gdb) info locals  # 查看局部变量
```


常见坑/追问：


- Release 编译关掉了符号表，`bt` 看不到函数名，调试要用 Debug build 或单独保留 `.debug` 文件。
- ASAN 和 `-O2` 同时开没问题，但 ASAN 本身有 ~2x 运行时开销，不适合生产。


---

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q2: ⭐🟢 Valgrind 是什么？和 ASAN 的区别？


A: 结论：Valgrind（memcheck）是动态分析工具，不需要重新编译，但速度极慢（~10-50x）；ASAN 是编译器插桩，速度快（~2x），但需要重新编译。


详细解释：


| 工具 | 是否需重编译 | 速度开销 | 检测能力 |
|------|------------|---------|---------|
| Valgrind memcheck | 否 | ~20-50x | 内存泄漏、野指针、未初始化读 |
| AddressSanitizer (ASAN) | 是 | ~2x | 越界、野指针、use-after-free |
| LeakSanitizer (LSAN) | 是 | ~1.1x | 内存泄漏（ASAN 附带） |
| ThreadSanitizer (TSAN) | 是 | ~5-15x | 数据竞争 |


```bash
# Valgrind 用法
valgrind --leak-check=full --show-leak-kinds=all ./myapp

# ASAN（编译时加参数）
g++ -fsanitize=address,undefined -g -o myapp main.cpp
```


常见坑/追问：


- Valgrind 在 Qt 程序上误报较多（Qt 内部有刻意的 "泄漏"），需要 `--suppressions` 过滤。
- TSAN 和 ASAN 不能同时开，需要分别运行。


---

> 💡 **面试追问**：内存泄漏如何定位？Valgrind 和 AddressSanitizer 各自适合什么场景？



### Q3: ⭐🟡 GDB 常用命令有哪些？


A: 结论：掌握 `break`/`run`/`next`/`step`/`continue`/`bt`/`watch`/`print` 这 8 个核心命令，能覆盖 90% 调试场景。


详细解释：


| 命令 | 简写 | 作用 |
|------|------|------|
| `break main.cpp:42` | `b` | 在第 42 行设断点 |
| `break MyClass::method` | `b` | 在函数入口设断点 |
| `run [args]` | `r` | 启动程序 |
| `next` | `n` | 单步执行（不进函数） |
| `step` | `s` | 单步执行（进入函数） |
| `continue` | `c` | 继续运行到下一个断点 |
| `backtrace` | `bt` | 打印调用栈 |
| `print expr` | `p` | 打印变量/表达式 |
| `watch var` | | 变量改变时暂停 |
| `info threads` | | 查看所有线程 |
| `thread N` | | 切换到线程 N |
| `finish` | | 运行到当前函数返回 |


常见坑/追问：


- `print` 打印 Qt 容器（QList、QString）显示不友好，可以用 GDB pretty-printer for Qt。
- Qt Creator 内置 GDB 图形界面，调试体验更好。


---

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q4: ⭐🟡 如何用 perf 分析 C++ 程序的 CPU 热点？


A: 结论：用 `perf record` 采样，`perf report` 分析调用树，找到 CPU 时间占比最高的函数。需要有调试符号。


详细解释：


```bash
# 1. 编译时保留符号（-g），但允许优化（-O2）
g++ -g -O2 -o myapp main.cpp

# 2. perf 采样（采样 30 秒，100Hz）
perf record -g -F 100 ./myapp

# 3. 交互式查看
perf report

# 4. 火焰图（需要 FlameGraph 工具）
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg
```


常见坑/追问：


- 内核符号需要 root 或 `kernel.perf_event_paranoid=1` 才能采集。
- Qt 应用的信号槽调用在 perf 上显示为 `QMetaObject::activate`，需要进一步展开。
- 火焰图纵轴是调用栈深度，横轴是时间占比，宽的框就是热点。


---

> 💡 **面试追问**：信号槽与回调函数相比有何优劣？跨线程信号槽如何工作？




## 二、内存问题

### Q5: ⭐🟡 Qt Creator 内置了哪些性能分析工具？


A: 结论：Qt Creator 集成 QML Profiler（QML 渲染分析）、Callgrind/Heaptrack（C++ CPU/内存分析）、Memcheck（内存错误）、Chrome Trace（Qt 6.5+）。


详细解释：


| 工具 | 用途 | 快捷入口 |
|------|------|---------|
| QML Profiler | QML 绑定/JS 执行时间，Scene Graph 渲染分析 | Analyze → QML Profiler |
| Callgrind | CPU 指令级分析，查函数调用次数和开销 | Analyze → Valgrind Function Profiler |
| Memcheck | 内存泄漏和越界检测（Valgrind） | Analyze → Valgrind Memory Analyzer |
| Heaptrack | 堆内存分配热点，找谁在疯狂 new | Analyze → Heaptrack |
| CTF/Chrome Trace | Qt 6.5+ 基于 LTTng/ETW 的系统级追踪 | 需手动配置 |


常见坑/追问：


- QML Profiler 和程序同时运行时有一定开销，大型应用要控制采样时间。
- Callgrind 模拟执行，速度非常慢（~50x），只在需要精确指令计数时用。


---

> 💡 **面试追问**：内存泄漏如何定位？Valgrind 和 AddressSanitizer 各自适合什么场景？



### Q6: ⭐🟡 如何检测多线程数据竞争（Data Race）？


A: 结论：用 ThreadSanitizer（TSAN）编译运行，它能在运行时检测并发访问的数据竞争，精确到代码行和线程 ID。


详细解释：


```bash
# 编译时加 TSAN
g++ -fsanitize=thread -g -o myapp main.cpp

# 运行，TSAN 在检测到竞争时打印详细报告：
# WARNING: ThreadSanitizer: data race
#   Write of size 4 at 0x...
#     #0 Thread1::run() main.cpp:15
#   Previous read of size 4 at 0x...
#     #1 Thread2::run() main.cpp:25
```


常见坑/追问：


- TSAN 只能检测运行时实际触发的竞争，不能静态覆盖所有路径。
- TSAN 和 ASAN、MSAN 不能同时开。
- Qt 内部有些刻意的"竞争"（经过原子保护），TSAN 可能误报，需要加 `suppressions`。


---

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q7: ⭐🟡 C++ 程序内存泄漏如何系统地排查？


A: 结论：组合使用 ASAN（开发阶段）+ Valgrind/Heaptrack（测试阶段），配合代码 review 检查裸指针、异常路径，消除漏洞。


详细解释：


**排查步骤：**

1. **ASAN**：编译加 `-fsanitize=address,leak`，程序退出时打印所有未释放内存的分配调用栈。
2. **Heaptrack**：记录所有堆分配，可以找出分配峰值和高频分配者。
3. **代码 Review 检查点**：
   - 异常抛出时是否会跳过 `delete`（用 RAII/智能指针避免）
   - 循环引用（shared_ptr 互指）
   - 容器存裸指针，容器清空时没有 delete
   - Qt parent 机制：只有有 parent 的 QObject 才自动释放

常见坑/追问：


- Qt 应用中，`QObject` 设置了 parent 就不需要手动 delete，但没有 parent 的必须手动管理。
- `QThread` 对象本身不自动释放，`thread->deleteLater()` 配合 `finished()` 信号是标准模式。


---

> 💡 **面试追问**：与 GC 相比 RAII 的优势是什么？异常抛出时 RAII 为何仍然可靠？



### Q8: ⭐🟡 `strace` 和 `ltrace` 分别用来做什么？


A: 结论：`strace` 追踪系统调用（open/read/write/ioctl 等），`ltrace` 追踪动态库函数调用。调试文件操作、IPC、权限问题很有用。


详细解释：


```bash
# strace：看程序在做什么系统调用
strace -f -e trace=open,read,write ./myapp
# -f：跟踪子进程
# -e trace=xxx：只看指定类型的调用
# -o output.txt：输出到文件

# ltrace：看调用了哪些动态库函数
ltrace ./myapp 2>&1 | head -50

# 实际场景：调试串口/HID 权限问题
strace -e trace=open,ioctl ./myapp 2>&1 | grep -E "tty|hid|usb"
```


常见坑/追问：


- `strace` 对多线程程序要加 `-f`，否则只追踪主线程。
- Qt 信号槽不是系统调用，`strace` 看不到，但 socket/epoll 等 I/O 操作可以看到。


---

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？




## 三、性能分析

### Q9: ⭐🟡 如何分析 Qt 应用的启动时间？


A: 结论：用 `QElapsedTimer` 手动打点，配合 `perf stat` 或 Qt Creator Profiler 找启动瓶颈，常见瓶颈是动态库加载和 QML 编译。


详细解释：


```cpp
// 在 main() 最开始加计时
#include <QElapsedTimer>
int main(int argc, char *argv[]) {
    QElapsedTimer timer;
    timer.start();

    QApplication app(argc, argv);
    qDebug() << "QApplication 构建:" << timer.elapsed() << "ms";

    MainWindow w;
    qDebug() << "MainWindow 构建:" << timer.elapsed() << "ms";

    w.show();
    qDebug() << "show():" << timer.elapsed() << "ms";

    return app.exec();
}
```


**常见启动瓶颈：**
- 动态库加载（减少依赖，用静态链接关键库）
- QML 文件解析/编译（Qt 6 支持 AOT 编译 `.qmlc`）
- 数据库连接/大量同步 I/O（改为异步或延迟加载）
- 大量单例初始化（改为懒初始化）


常见坑/追问：


- Qt 6 的 QML 缓存（`.qmlc`）在文件没变化时可以跳过解析，明显提升启动速度。


---

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q10: ⭐🟡 如何用 `QLoggingCategory` 做分级日志？


A: 结论：`QLoggingCategory` 允许按模块/类别分级控制日志输出，避免发布版日志塞满终端，又能在需要时精确打开特定模块的调试日志。


详细解释：


```cpp
// 定义分类
Q_LOGGING_CATEGORY(lcNetwork, "myapp.network")
Q_LOGGING_CATEGORY(lcUI,      "myapp.ui")

// 使用
qCDebug(lcNetwork) << "连接到" << host;
qCWarning(lcUI)    << "布局计算超时";

// 运行时通过环境变量控制
// QT_LOGGING_RULES="myapp.network=true;myapp.ui=false" ./myapp

// 或通过配置文件 /path/to/qtlogging.ini
// [Rules]
// myapp.*=false
// myapp.network=true
```


常见坑/追问：


- `qCDebug` 在 Release 编译中会被优化掉（零开销），比 `qDebug` 更适合生产代码。
- 多线程程序中 `qCDebug` 是线程安全的。


---

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q11: ⭐🔴 如何分析和解决 Qt 程序的死锁？


A: 结论：死锁时用 GDB `info threads` + `bt` 分析每个线程的调用栈，找到互相等待的锁；用 TSAN 可以在运行时提前发现潜在死锁。


详细解释：


**定位步骤：**

```bash
# 1. 程序卡死，用 gdb attach
gdb -p <pid>

# 2. 查看所有线程
(gdb) info threads

# 3. 切换到每个线程查看调用栈
(gdb) thread apply all bt

# 4. 找到都在等锁的线程：调用栈里有 pthread_mutex_lock / std::mutex::lock 的
```


**死锁常见模式：**
- **ABBA 锁**：线程 1 持有 A 等 B，线程 2 持有 B 等 A
- **Qt 主线程阻塞 + 信号槽**：主线程持锁，Worker 通过信号槽在主线程执行，又等主线程的锁
- **recursive_mutex 未用 recursive 版**：同一线程重复加锁（std::mutex 不支持递归）

**预防：**
- 统一加锁顺序（锁的层级化）
- 用 `std::lock(a, b)` 同时获取多个锁，避免 ABBA
- Qt 信号槽跨线程时注意 `Qt::BlockingQueuedConnection` 容易死锁


---

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q12: ⭐🟡 `core dump` 是什么？怎么配置和使用？


A: 结论：`core dump` 是进程崩溃时的内存快照，可以用 `gdb` 事后复盘，还原崩溃现场的调用栈和变量值。


详细解释：


```bash
# 1. 开启 core dump（默认关闭）
ulimit -c unlimited

# 2. 设置 core 文件路径（Linux）
echo "/tmp/core-%e-%p" | sudo tee /proc/sys/kernel/core_pattern

# 3. 程序崩溃后生成 core 文件
# 4. 用 gdb 分析
gdb ./myapp /tmp/core-myapp-12345

(gdb) bt          # 查看崩溃时的调用栈
(gdb) info regs   # 查看寄存器
(gdb) list        # 查看源码上下文
```


常见坑/追问：


- systemd 系统默认 core dump 由 `systemd-coredump` 处理，路径在 `/var/lib/systemd/coredump/`，用 `coredumpctl` 查看。
- Docker 容器内 `ulimit -c unlimited` 需要 `--ulimit core=-1` 启动参数。


---

> 💡 **面试追问**：内存泄漏如何定位？Valgrind 和 AddressSanitizer 各自适合什么场景？




## 四、生产环境诊断

### Q13: ⭐🟡 C++ 程序如何做基准测试（Benchmark）？


A: 结论：Google Benchmark（`gbench`）是标准选择，自动控制循环次数、预热、统计变异，结果可靠；简单场景用 `QElapsedTimer` 或 `std::chrono`。


详细解释：


```cpp
#include <benchmark/benchmark.h>

static void BM_StringCopy(benchmark::State& state) {
    std::string src(state.range(0), 'x');
    for (auto _ : state) {
        std::string copy = src;
        benchmark::DoNotOptimize(copy);  // 防止编译器优化掉
    }
    state.SetBytesProcessed(state.iterations() * state.range(0));
}
BENCHMARK(BM_StringCopy)->Range(8, 1024);

BENCHMARK_MAIN();
```


```bash
# 编译并运行
g++ -O2 -lbenchmark -lpthread -o bench bench.cpp
./bench --benchmark_filter=BM_StringCopy
```


常见坑/追问：


- 不要用 `clock()` 或 `gettimeofday()`，精度不够，受系统负载影响大。
- 基准测试要在 Release 模式（`-O2`）下运行，Debug 下完全没参考价值。
- 用 `DoNotOptimize` 和 `ClobberMemory` 防止编译器把测试代码优化掉。


---

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q14: ⭐🟡 如何查找 Qt 程序的内存使用峰值？


A: 结论：用 `Heaptrack` 记录所有堆分配，可以精确找到内存分配峰值时的调用栈；`/proc/<pid>/status` 的 `VmRSS`/`VmPeak` 提供整体粗粒度视图。


详细解释：


```bash
# 1. Heaptrack（推荐）
heaptrack ./myapp
heaptrack --analyze heaptrack.myapp.*.gz  # 或用 heaptrack_gui

# 2. 实时查看进程内存
watch -n 1 "cat /proc/$(pidof myapp)/status | grep -E 'VmRSS|VmPeak|VmSize'"

# 3. Qt 内置（粗粒度）
# 只能看 QObject 数量，不能定位分配点
```


常见坑/追问：


- `VmRSS` 是当前实际物理内存；`VmPeak` 是历史峰值；`VmSize` 是虚拟地址空间（包含 mmap）。
- Qt 有内存池（`QObject` 内部的 `d_ptr` 复用等），heaptrack 的数据会比 `VmRSS` 看起来多。


---

> 💡 **面试追问**：内存泄漏如何定位？Valgrind 和 AddressSanitizer 各自适合什么场景？



### Q15: ⭐🔴 线上环境崩溃如何在没有 core dump 的情况下调试？


A: 结论：用 `signal` 捕获 `SIGSEGV`/`SIGABRT`，在处理函数中通过 `backtrace()` 打印调用栈到日志；或集成 `Breakpad`/`Crashpad` 崩溃上报框架。


详细解释：


```cpp
#include <execinfo.h>
#include <csignal>

void crashHandler(int sig) {
    void *array[20];
    int size = backtrace(array, 20);
    fprintf(stderr, "Error: signal %d\n", sig);
    backtrace_symbols_fd(array, size, STDERR_FILENO);
    signal(sig, SIG_DFL);
    raise(sig);  // 重新触发，产生 core dump（如果已配置）
}

int main() {
    signal(SIGSEGV, crashHandler);
    signal(SIGABRT, crashHandler);
    // ...
}
```


**生产环境方案：**
- **Breakpad/Crashpad**（Google 出品）：崩溃时写入 minidump，上报到服务器，`minidump_stackwalk` 分析
- **Sentry**：SaaS 崩溃收集平台，有 C++ SDK
- **符号服务器**：保存每个版本的 `.debug` 文件，上报的 minidump 能还原符号


常见坑/追问：


- `backtrace` 在 Signal Handler 中调用不是 async-signal-safe，有一定风险，但实践中基本可用。
- 线上 binary 应当是 stripped（无符号），但要保留 `.debug` 文件用于事后分析。

---

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？

---

## 📊 本章统计

| 指标 | 数量 |
|------|------|
| 总题目数 | 15 |
| 🟢 入门 | 2 |
| 🟡 进阶 | 11 |
| 🔴 高难 | 2 |
