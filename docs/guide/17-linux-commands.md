# 17. Linux 常用命令与调试

> 难度分布：🟢 入门 1 题 · 🟡 进阶 8 题 · 🔴 高难 6 题

[[toc]]

---

### Q1: ⭐🟢 怎么快速看一个进程的资源占用和状态？


A: 结论：常用 `ps`、`top`、`htop`、`pidstat`、`pmap`、`lsof`、`/proc`。面试里要体现“先宏观定位，再细分问题”的排查思路。


详细解释：


- `ps -ef | grep xxx` 看进程是否存在。
- `top/htop` 看 CPU、内存、线程。
- `pidstat -p &lt;pid&gt; 1` 看更细的 CPU/IO 上下文切换。
- `/proc/&lt;pid&gt;/status`、`/proc/&lt;pid&gt;/fd` 很重要。


常见坑/追问：


- `grep` 自己会出现在结果里，别被逗了。
- 追问：怎么查进程打开了哪些文件？`lsof -p &lt;pid&gt;`。


### Q2: ⭐🟡 strace 和 ltrace 分别看什么？


A: 结论：`strace` 跟踪系统调用，`ltrace` 跟踪库函数调用。一个更靠内核边界，一个更靠用户态动态库边界。


详细解释：


- `strace -p pid` 可看进程正在做哪些 syscall。
- `-e trace=open,read,write` 可过滤指定系统调用。
- `ltrace` 常看 libc、动态库函数调用，但对静态链接或某些场景受限。
- 排查“卡住”“权限错”“找不到文件”时 `strace` 很猛。


代码示例：


```bash
strace -ff -p 1234
ltrace -p 1234
```


常见坑/追问：


- `strace` 会带来额外开销，线上长时间挂着要谨慎。
- 追问：程序卡住时 `strace` 一看一直 `futex` 是什么意思？往往在等锁/条件变量。


### Q3: ⭐🔴 gdb 实战排查崩溃的基本流程是什么？


A: 结论：基本流程是：带符号编译 → 生成 core 或 attach → 看 backtrace → 切 frame → 查变量/线程 → 结合源码定位根因。


详细解释：


- 编译加 `-g`，最好不要过度 strip。
- 开 core：`ulimit -c unlimited`。
- `gdb ./app core.xxx` 后先 `bt`、`info threads`、`thread apply all bt`。
- 崩溃点不一定是根因，要往上看调用链和参数来源。


代码示例：


```bash
gdb ./app core.1234
(gdb) bt
(gdb) frame 3
(gdb) p var
```


常见坑/追问：


- 没调试符号时 backtrace 会非常难看。
- 追问：release 优化后变量看不到怎么办？可降低优化、保留 frame pointer、配套符号包。


### Q4: ⭐🔴 valgrind 和 ASan 分别擅长什么？


A: 结论：ASan 更快、适合开发期频繁跑，擅长越界/Use-after-free；Valgrind 更慢但无需重编译某些场景可直接跑，对内存泄漏和非法访问也很有价值。


详细解释：


- ASan 依赖编译器插桩：`-fsanitize=address`。
- Valgrind 通过动态二进制翻译运行程序。
- ASan 对时序和覆盖更友好；Valgrind 对某些第三方二进制也能用。
- LeakSanitizer、UBSan 也常配套出现。


代码示例：


```bash
g++ -g -fsanitize=address -fno-omit-frame-pointer main.cpp
valgrind --leak-check=full ./app
```


常见坑/追问：


- ASan 报错位置可能是“出事现场”，根因写坏内存可能更早。
- 追问：线上能常驻 ASan 吗？通常不建议，性能和内存开销较大。


### Q5: ⭐🟡 perf 是干什么的？


A: 结论：`perf` 是 Linux 性能分析利器，可看热点函数、调用栈、硬件事件、采样火焰图素材。CPU 高但不知道烧在哪时，它非常好用。


详细解释：


- `perf top` 实时看热点。
- `perf record -g ./app` 录制采样。
- `perf report` 分析调用栈。
- 可观察 cache miss、branch miss 等硬件事件。


代码示例：


```bash
perf record -g ./app
perf report
```


常见坑/追问：


- 没符号表时结果可读性会差很多。
- 追问：采样分析和 instrumentation 分析区别？采样开销低、统计意义强；插桩更精确但更重。


### Q6: 🟡 怎么排查程序“卡住不动”？


A: 结论：先看是在等 CPU、等锁、等 IO、还是死循环。常见组合拳是 `top` + `strace` + `gdb` + 日志时间线。


详细解释：


- CPU 100%：可能死循环、忙等、算法热点，优先 `perf/gdb`。
- CPU 很低：可能阻塞在 `read/futex/epoll_wait/poll`。
- `strace -p pid` 看系统调用停在哪。
- `gdb -p pid` 用 `thread apply all bt` 看线程栈。


常见坑/追问：


- “卡住”不等于死锁，也可能是在正常等待数据。
- 追问：看到 `epoll_wait` 就一定有问题吗？不一定，事件驱动程序空闲时本来就该等在那里。


### Q7: ⭐🟡 lsof、netstat、ss 各怎么用？


A: 结论：`lsof` 查文件和 socket 占用，`ss`/`netstat` 查网络连接和监听端口。现代 Linux 更推荐 `ss`。


详细解释：


- `lsof -i :8080` 看哪个进程占端口。
- `ss -lntp` 看 TCP 监听和进程。
- `ss -antp` 看连接状态，例如 ESTAB、TIME-WAIT。
- 网络故障排查常和 `tcpdump` 一起使用。


常见坑/追问：


- 端口占用不一定是僵尸进程，也可能是其他服务实例。
- 追问：为什么推荐 `ss`？它基于 netlink，通常比老 `netstat` 更快。


### Q8: 🟡 怎么看 shared library 依赖和符号问题？


A: 结论：常用 `ldd` 看依赖，`nm`/`objdump -T`/`readelf -Ws` 看符号，`LD_LIBRARY_PATH` 和 rpath/runpath 影响运行时加载结果。


详细解释：


- `ldd app` 看程序依赖哪些 so。
- `nm -C libxxx.so | grep symbol` 查导出符号。
- `readelf -d` 可看 RPATH/RUNPATH。
- 遇到 `undefined symbol`、`cannot open shared object file` 时非常常用。


常见坑/追问：


- `ldd` 结果对 setuid 程序等特殊场景要谨慎理解。
- 追问：为什么同名 so 版本不对会炸？因为 ABI 不兼容。


### Q9: ⭐🔴 gdb attach 在线进程时最实用的几个命令是什么？


A: 结论：高频命令包括 `bt`、`info threads`、`thread apply all bt`、`frame`、`p`、`x`、`info locals`、`disassemble`。会这几招已经能解决很多现场问题。


详细解释：


- `attach &lt;pid&gt;` 挂到运行进程。
- `thread apply all bt` 一次看全线程栈。
- `frame n` 切某栈帧，`p var` 看变量。
- `x/16bx addr` 看内存，`disassemble` 看汇编。


代码示例：


```bash
gdb -p 1234
(gdb) info threads
(gdb) thread apply all bt
```


常见坑/追问：


- attach 会暂停进程，线上要注意业务影响。
- 追问：多线程崩溃时最先看什么？先看所有线程栈，再锁定异常线程和等待关系。


### Q10: ⭐🔴 调试的正确姿势是什么？


A: 结论：先建立证据链，再下结论。命令行调试最怕“凭感觉修 bug”。


详细解释：


- 先复现，再采样，再缩小范围。
- 观察现象：CPU、内存、IO、线程栈、syscall、日志时间点。
- 建立假设并验证，不要一次改十处。
- 能保留最小复现就尽量保留，这对后续回归极其重要。


常见坑/追问：


- 最危险的是看到一个可疑点就直接改，结果把根因埋深了。
- 追问：线上问题最关键的能力是什么？快速收集证据和止血，而不是炫技。


### Q11: ⭐🟡 如何用 `perf` 分析 C++ 程序的性能热点？


A: 结论：`perf record` 采样 CPU 性能计数器，`perf report` 或 `perf script | flamegraph.pl` 生成火焰图，直观展示哪些函数占用 CPU 最多。


详细解释：


- `perf record -g ./myapp`：带调用栈采样（`-g` 启用 frame pointer 或 DWARF 展开）。
- `perf report`：交互式报告，按函数名排序热点。
- 火焰图：`perf script | stackcollapse-perf.pl | flamegraph.pl > out.svg`，直观。
- `perf stat ./myapp`：统计 IPC、缓存命中率、分支预测等 CPU 计数器，快速评估程序效率。


代码示例：


```bash
# 采样 30s 生成火焰图
perf record -F 99 -g -p $(pidof myapp) -- sleep 30
perf script | ~/FlameGraph/stackcollapse-perf.pl | \
    ~/FlameGraph/flamegraph.pl > flamegraph.svg
```


常见坑/追问：


- Release 构建 + `-fno-omit-frame-pointer` 才能得到准确调用栈（或改用 `--call-graph dwarf`）。
- 追问：`perf record` 和 `gprof` 区别？`perf` 是采样式（低开销，适合生产），`gprof` 是插桩式（精确但改变程序行为）。


---


### Q12: ⭐🟡 `lsof` 和 `fuser` 有什么用？


A: 结论：`lsof` 列出进程打开的所有文件（含网络连接、设备、管道）；`fuser` 查找正在使用某文件或端口的进程；两者常用于排查文件锁定、端口占用。


详细解释：


- `lsof -p PID`：某进程打开的所有 fd（文件、socket、管道等）。
- `lsof -i :8080`：占用 8080 端口的进程。
- `lsof +D /mnt/usb`：某目录下被打开的文件（卸载时报"设备忙"的排查利器）。
- `fuser -v /dev/ttyUSB0`：谁打开了串口设备。
- `fuser -k 8080/tcp`：强制 kill 占用端口的进程。


代码示例：


```bash
# 查看进程泄漏的文件描述符数量
lsof -p $(pidof myapp) | wc -l
# 查看 TCP 连接状态
lsof -i TCP -n -P | grep ESTABLISHED
```


常见坑/追问：


- `lsof` 输出 `(deleted)` 表示文件已被删除但仍有进程持有 fd，磁盘空间不会释放直到进程关闭。
- 追问：如何确认文件描述符泄漏？定期 `lsof -p PID | wc -l`，持续增长则泄漏。


---


### Q13: ⭐🔴 如何排查 Linux 程序的内存泄漏？


A: 结论：工具链：`Valgrind --leak-check=full`（精确但慢）、`AddressSanitizer`（编译器插桩，较快）、`/proc/PID/smaps` + `pmap` 监控内存增长趋势，三者配合定位。


详细解释：


- **Valgrind Memcheck**：模拟 CPU，精确跟踪每次 malloc/free，报告泄漏调用栈，速度慢 10-50x。
- **ASan（AddressSanitizer）**：`-fsanitize=address` 编译，运行时 2-3x 速度损耗，检测泄漏、越界、UAF。
- **`/proc/PID/smaps_rollup`**：定期记录 `Rss` 和 `Pss` 监控增长。
- **`pmap -x PID`**：查看内存段分布，发现异常大的 heap 或匿名映射。


代码示例：


```bash
# ASan 编译
g++ -fsanitize=address -fno-omit-frame-pointer -g myapp.cpp -o myapp
./myapp
# Valgrind
valgrind --leak-check=full --show-leak-kinds=all ./myapp
```


常见坑/追问：


- ASan 和 Valgrind 不能同时使用（会冲突）。
- 追问：线上不能用 ASan 怎么排查？用 `gperftools` 的 `heap profiler` 或定期抓 `/proc/smaps` 趋势。


---


### Q14: ⭐🟡 `ss` 和 `netstat` 有什么区别？为什么推荐用 `ss`？


A: 结论：`ss`（socket statistics）是 `netstat` 的现代替代品，直接读取内核 netlink 接口，速度更快，连接数多时优势明显（`netstat` 遍历 `/proc/net/tcp` 慢）；两者功能基本相同。


详细解释：


- `ss -tunap`：显示 TCP/UDP 连接，含进程信息（需 root 看其他进程）。
- `ss -lntp`：只看监听（LISTEN）状态的 TCP socket。
- `ss -s`：汇总统计（各状态连接数）。
- `netstat` 在某些发行版已默认不安装，属于 `net-tools` 老包；`ss` 属于 `iproute2`，更现代。


代码示例：


```bash
# 查看所有 ESTABLISHED 连接
ss -tunap state established
# 查看监听端口和进程
ss -lntp
# 统计各状态 TCP 连接数
ss -s | grep TCP
```


常见坑/追问：


- `TIME_WAIT` 大量积累通常是短连接高并发导致，可调整 `tcp_tw_reuse` 或增大端口范围。
- 追问：如何实时监控连接数变化？`watch -n 1 'ss -s'`。


---


### Q15: ⭐🔴 `dmesg` 和内核日志有哪些调试用途？


A: 结论：`dmesg` 读取内核环形缓冲区，适合排查硬件错误（OOM、硬件故障、驱动崩溃）、USB/串口设备识别、系统调用触发的内核警告；结合时间戳和级别过滤定位问题。


详细解释：


- `dmesg -T`：带人可读时间戳（默认是相对启动时间）。
- `dmesg -l err,crit`：只看错误/严重级别的消息。
- OOM Killer：进程被 OOM 杀死时 dmesg 有详细记录（哪个进程，内存压力情况）。
- USB/串口枚举：设备插入时 `dmesg | tail` 可以看到 `ttyUSB0` 之类的分配信息。
- 驱动崩溃/Oops：内核 Oops 包含函数调用栈，可用 `addr2line` 翻译地址。


代码示例：


```bash
# 实时监控内核日志（排查设备插拔）
dmesg -w
# 过滤 USB 相关
dmesg | grep -i usb
# OOM 事件
dmesg | grep -i "oom\|killed process"
# 解析内核 Oops 地址
addr2line -e vmlinux 0xffffffffc0123456
```


常见坑/追问：


- `dmesg` 缓冲区是环形的，高频日志会覆盖旧记录；重要内核日志应配置 `rsyslog`/`journald` 持久化。
- 追问：普通用户能看 `dmesg` 吗？Linux 5.x 之后默认限制普通用户，需要 `sudo` 或设置 `kernel.dmesg_restrict=0`。

---

## 📊 本章统计

| 指标 | 数量 |
|------|------|
| 总题目数 | 15 |
| 🟢 入门 | 1 |
| 🟡 进阶 | 8 |
| 🔴 高难 | 6 |
