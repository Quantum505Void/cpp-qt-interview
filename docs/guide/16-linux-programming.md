# 16. Linux 系统编程

> 难度分布：🟢 入门 1 题 · 🟡 进阶 8 题 · 🔴 高难 6 题

[[toc]]

---


## 一、进程与文件

### Q1: ⭐🟢 用户态和内核态的区别是什么？


A: 结论：用户态运行普通应用，权限受限；内核态运行操作系统核心代码，权限最高。系统调用是用户态进入内核态的主要通道。


详细解释：


- 用户态不能直接操作硬件或任意内存。
- 进程要读文件、发网络包、创线程，通常都要通过 syscall。
- 切换到内核态有开销，所以高频 syscall 会影响性能。


常见坑/追问：


- 不要把“线程切换”和“用户态/内核态切换”混为一谈。
- 追问：为什么 `read` 比直接访问用户内存慢？因为要陷入内核并做权限检查/拷贝。

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q2: ⭐🟡 open/read/write/close 这一套 I/O 调用要注意什么？


A: 结论：它们是 Linux 最基础的文件 I/O 接口，核心要点是返回值检查、短读短写处理、EINTR 重试和 fd 生命周期管理。


详细解释：


- `open` 返回 fd，失败返回 -1。
- `read` 可能少于请求字节数，尤其 socket/pipe。
- `write` 也可能短写，不能想当然一次写完。
- `close` 后 fd 不可再用。


代码示例：


```cpp
ssize_t n = write(fd, buf, len);
if (n < 0 && errno == EINTR) {
    // retry
}
```


常见坑/追问：


- 忽略短写是实际项目高频 bug。
- 追问：为什么 regular file 上短读短写少见，但仍要考虑？因为接口语义允许，健壮代码不能赌环境。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q3: ⭐🔴 mmap 是什么？适合哪些场景？


A: 结论：`mmap` 把文件或匿名内存映射到进程地址空间，适合大文件随机访问、共享内存、高性能 I/O 等场景。它不是“更高级的 read”，而是另一套内存映射语义。


详细解释：


- 文件映射：访问像内存，底层按页调入。
- 匿名映射：可用于共享内存或大块分配。
- `MAP_SHARED` 修改可回写到底层对象；`MAP_PRIVATE` 是写时复制。
- 优势：减少用户态拷贝、随机访问方便。


代码示例：


```cpp
int fd = open("data.bin", O_RDONLY);
void* p = mmap(nullptr, size, PROT_READ, MAP_PRIVATE, fd, 0);
// 使用完后
munmap(p, size);
```


常见坑/追问：


- 映射长度、页对齐、文件变短后的 SIGBUS 都要注意。
- 追问：`mmap` 一定比 `read` 快吗？不一定，顺序小文件读未必占优。

> 💡 **面试追问**：内存泄漏如何定位？Valgrind 和 AddressSanitizer 各自适合什么场景？



### Q4: ⭐🔴 signal 的本质是什么？为什么难写对？


A: 结论：signal 是内核向进程/线程递送异步通知的机制，难点在于它会在不可预知时刻打断正常执行，因此处理函数能做的事非常有限。


详细解释：


- 常见信号：SIGINT、SIGTERM、SIGSEGV、SIGCHLD、SIGPIPE。
- 注册处理通常用 `sigaction` 而非老式 `signal`。
- signal handler 里只能调用 async-signal-safe 函数。
- 多线程程序里信号递送和屏蔽规则更复杂。


代码示例：


```cpp
void onSig(int) {
    g_stop = 1; // 只做最小动作
}

struct sigaction sa{};
sa.sa_handler = onSig;
sigaction(SIGTERM, &sa, nullptr);
```


常见坑/追问：


- 在 handler 里 `printf/new/malloc/std::string` 都可能出事。
- 追问：优雅退出怎么做？handler 里只置标志，主循环检测后收尾。

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q5: ⭐🟡 select/poll/epoll 有什么区别？


A: 结论：三者都是 I/O 多路复用。`select` 最老、fd 数量受限；`poll` 去掉位图限制但仍线性扫描；`epoll` 更适合大量连接场景。


详细解释：


- `select` 需要每次重置 fd_set。
- `poll` 用数组描述关注事件。
- `epoll` 把关注集合保存在内核，事件就绪时返回活跃项。
- 高并发服务端最常聊 `epoll`，桌面/工具类程序未必必须上。


常见坑/追问：


- `epoll` 也不是万能，连接少时不一定明显占优。
- 追问：LT 和 ET 区别？电平触发更稳，边沿触发性能潜力更高但更易漏读。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？




## 二、线程与同步

### Q6: ⭐🟡 什么是 daemon？Linux 守护进程一般怎么做？


A: 结论：daemon 是脱离终端、长期在后台运行的服务进程。传统做法包括 fork、setsid、切目录、重定向标准流；现代 Linux 上也常直接交给 systemd 管理。


详细解释：


- 经典 daemonize 步骤：fork 后父进程退出、子进程 `setsid()`、可再次 fork、防止重新获得终端。
- 切到 `/` 防止占用挂载点。
- 重定向 stdin/stdout/stderr 到 `/dev/null` 或日志系统。
- 现在很多程序直接以前台方式运行，由 systemd 托管生命周期。


代码示例：


```cpp
pid_t pid = fork();
if (pid > 0) _exit(0);
setsid();
```


常见坑/追问：


- 守护进程和后台运行不是一回事。
- 追问：为什么现代服务推荐 systemd 管？因为日志、重启、依赖、权限都更规范。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q7: ⭐🔴 dlopen/dlsym 是什么？常见应用是什么？


A: 结论：`dlopen/dlsym` 用于运行时动态加载共享库和解析符号，常见于插件系统、可选模块、热插拔能力。它是 Linux 插件化设计高频考点。


详细解释：


- `dlopen("libxxx.so", RTLD_NOW)` 加载动态库。
- `dlsym(handle, "create_plugin")` 获取函数地址。
- 常配合统一 C 接口导出工厂函数，避免 C++ ABI 问题。
- 卸载时用 `dlclose`。


代码示例：


```cpp
void* h = dlopen("./libplugin.so", RTLD_NOW);
auto create = reinterpret_cast<void*(*)()>(dlsym(h, "create_plugin"));
```


常见坑/追问：


- C++ 类跨 so 边界直接传递容易踩 ABI、编译器版本、STL 实现差异坑。
- 追问：为什么插件接口常用 `extern "C"`？为了稳定符号名和调用约定。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q8: 🟡 fork 在多线程程序里为什么要格外小心？


A: 结论：因为 `fork` 后只有调用它的那个线程会出现在子进程里，但锁状态、库内部状态可能来自父进程的全局现场，容易死锁或状态不一致。


详细解释：


- 多线程进程里其他线程突然“消失”，但 mutex 可能仍处于锁住状态。
- 因此 `fork` 后子进程通常应尽快 `exec`，不要做复杂逻辑。
- 这也是很多系统编程面试爱问的坑点。


常见坑/追问：


- fork 后在子进程里调用复杂日志/内存分配接口都不稳。
- 追问：有没有钩子？有 `pthread_atfork`，但也不是万能药。

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q9: ⭐🟡 什么是文件锁？flock 和 fcntl 有什么区别？


A: 结论：文件锁用于协调多进程访问。`flock` 更简单，通常针对整个文件；`fcntl` 更灵活，支持字节范围锁。二者语义和适用场景不同。


详细解释：


- `flock` 常见于单机脚本/守护进程防重复启动。
- `fcntl` 记录锁更细粒度，可锁文件一部分。
- 锁能否跨 NFS、是否随 fd/进程释放，要看具体机制。


代码示例：


```cpp
int fd = open("app.lock", O_CREAT | O_RDWR, 0644);
flock(fd, LOCK_EX | LOCK_NB);
```


常见坑/追问：


- 锁是协作机制，不会阻止不遵守协议的进程乱写。
- 追问：守护进程为什么常用 lock file？避免多实例抢资源。

> 💡 **面试追问**：互斥锁和自旋锁各自适合什么场景？如何避免死锁？



### Q10: ⭐🔴 系统编程里最重要的习惯是什么？


A: 结论：最重要的是尊重返回值和错误码，永远按失败路径编程。系统调用世界不像业务代码那样“理所当然成功”。


详细解释：


- 每个 syscall 都可能失败。
- 要考虑 EINTR、EAGAIN、部分成功、资源耗尽、权限不足。
- 资源释放要成对：open/close、mmap/munmap、dlopen/dlclose。
- 出问题时保留 errno、日志带上下文。


常见坑/追问：


- 最大低级错误是示例代码写习惯了，生产代码还不查返回值。
- 追问：`perror` 和 `strerror(errno)` 有啥区别？前者简单直接，后者更便于自定义日志格式。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？




## 三、网络与 IPC

### Q11: ⭐🟡 `epoll` 和 `select`/`poll` 有什么本质区别？


A: 结论：`select`/`poll` 每次调用需要传入和扫描全部 fd 集合，O(n) 复杂度；`epoll` 使用内核事件表，只返回就绪的 fd，O(1) 检测，适合大量并发连接场景。


详细解释：


- `select`：fd_set 限制（通常 1024），每次调用拷贝整个集合进内核，轮询所有 fd。
- `poll`：无 fd 数量限制，但每次调用仍传入全部 pollfd 数组，O(n) 扫描。
- `epoll`：`epoll_create` 创建实例，`epoll_ctl` 注册 fd，`epoll_wait` 只返回就绪事件，O(1)。
- `epoll` 的 LT（水平触发）和 ET（边缘触发）：LT 兼容传统，ET 高性能但需一次读完数据。


代码示例：


```cpp
int epfd = epoll_create1(0);
epoll_event ev = {.events = EPOLLIN, .data = {.fd = sockfd}};
epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev);
epoll_event events[64];
int n = epoll_wait(epfd, events, 64, -1); // 阻塞直到有事件
for (int i = 0; i < n; i++) {
    int fd = events[i].data.fd;
    // 处理 events[i].events
}
```


常见坑/追问：


- ET 模式下 `read` 必须循环读到 `EAGAIN`，否则剩余数据永远不会触发事件。
- 追问：`EPOLLONESHOT` 是什么？注册后只触发一次，处理完需重新 arm，适合多线程防竞争。


---

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q12: ⭐🟡 什么是写时复制（Copy-on-Write）？在 Linux fork 中的应用？


A: 结论：COW 是一种延迟复制策略：fork 后父子进程共享物理内存页，页面标记为只读；任何一方写入时内核复制该页给写入方，其余页仍共享，减少不必要的内存复制。


详细解释：


- fork 系统调用仅复制进程描述符和页表，不复制物理内存，几乎是 O(1)。
- 子进程只读访问（如 exec 前）无需复制任何页，效率极高（这是 `fork+exec` 高效的基础）。
- 大量写操作会触发大量页复制，此时 COW 开销反而比直接复制高（页错误 + 内核介入）。
- `vfork`：比 fork 更轻量，子进程直接使用父进程地址空间，必须立即 exec/exit。


常见坑/追问：


- Redis 的 RDB/AOF 持久化利用 COW：fork 子进程做快照，父进程继续写，子进程看到快照时刻的数据。
- 追问：COW 和 `mmap` 的 `MAP_PRIVATE` 有什么关系？`MAP_PRIVATE` 的写操作触发 COW，修改不影响文件或其他进程。


---

> 💡 **面试追问**：内存泄漏如何定位？Valgrind 和 AddressSanitizer 各自适合什么场景？



### Q13: ⭐🔴 Linux 中的内存映射文件（mmap）有哪些应用场景？


A: 结论：mmap 将文件或匿名内存映射到进程地址空间，适合大文件随机访问（零拷贝）、进程间共享内存、实现内存池和高性能 IO。


详细解释：


- **大文件访问**：直接用指针访问文件内容，内核按需加载页面，避免 read/write 用户-内核拷贝。
- **IPC 共享内存**：多进程映射同一文件，直接共享内存，速度远高于管道/消息队列。
- **匿名映射**：`MAP_ANONYMOUS | MAP_PRIVATE`，用于大块临时内存（如内存池后端）。
- **动态库加载**：内核用 mmap 加载 .so 的各段，实现多进程共享代码段（只读 COW）。


代码示例：


```cpp
int fd = open("bigfile.bin", O_RDONLY);
struct stat st; fstat(fd, &st);
void* ptr = mmap(nullptr, st.st_size, PROT_READ, MAP_SHARED, fd, 0);
// 直接用指针访问文件内容
uint32_t val = *reinterpret_cast<uint32_t*>(ptr);
munmap(ptr, st.st_size);
close(fd);
```


常见坑/追问：


- `mmap` 的映射大小必须是页对齐的，文件末尾不足一页的部分用零填充。
- 追问：mmap vs read/write 哪个更快？顺序读写 read/write 可以更快（支持 readahead）；随机访问 mmap 更优（直接寻址，无系统调用开销）。


---

> 💡 **面试追问**：内存泄漏如何定位？Valgrind 和 AddressSanitizer 各自适合什么场景？



### Q14: ⭐🟡 Linux 下如何做进程间共享内存（POSIX shm）？


A: 结论：用 `shm_open` 创建共享内存对象，`ftruncate` 设置大小，`mmap` 映射到各进程，通过信号量（`sem_open`/`pthread_mutex` + `PTHREAD_PROCESS_SHARED`）同步访问。


详细解释：


- `shm_open("/myshm", O_CREAT | O_RDWR, 0666)` → 返回 fd。
- `ftruncate(fd, size)` → 设置共享内存大小。
- `mmap(NULL, size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0)` → 映射。
- 同步：`pthread_mutex_t` 放在共享内存内，初始化时设置 `PTHREAD_MUTEX_PSHARED` 属性。
- 清理：`shm_unlink` 删除共享内存对象（文件持久化直到所有进程 munmap 且 unlink）。


代码示例：


```cpp
int fd = shm_open("/myshm", O_CREAT|O_RDWR, 0666);
ftruncate(fd, sizeof(SharedData));
auto* data = static_cast<SharedData*>(
    mmap(nullptr, sizeof(SharedData), PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0));
// 各进程都这样映射，然后通过 data->mutex 同步
```


常见坑/追问：


- 共享内存里不能放指针（各进程映射地址不同），只能放偏移量或相对地址。
- 追问：`mmap MAP_SHARED` 和 POSIX shm 有何区别？前者基于文件，后者基于 `/dev/shm` 内存文件系统，shm 更干净，文件 mmap 适合持久化。


---

> 💡 **面试追问**：内存泄漏如何定位？Valgrind 和 AddressSanitizer 各自适合什么场景？



### Q15: ⭐🔴 `strace` 和 `ltrace` 的区别是什么？各自的典型使用场景？


A: 结论：`strace` 跟踪系统调用（内核接口），`ltrace` 跟踪动态库函数调用（用户态库函数）；前者适合调试 IO/网络/进程问题，后者适合追踪第三方库调用行为。


详细解释：


- `strace ./app`：打印所有 syscall（`open`、`read`、`write`、`mmap` 等）及参数和返回值，适合排查"打不开文件"、"网络连不上"等问题。
- `strace -p PID -e trace=network`：过滤只看网络相关 syscall。
- `ltrace ./app`：打印动态库调用（`malloc`、`printf`、`fopen` 等），适合追踪 C 标准库和第三方库行为。
- 性能影响：两者都显著拖慢目标程序（ptrace 机制），线上环境谨慎使用。


代码示例：


```bash
# 追踪文件相关系统调用
strace -e trace=file ./myapp 2>&1 | grep "ENOENT"
# 追踪进程的系统调用统计
strace -c ./myapp
# 跟踪库函数调用
ltrace -e malloc+free ./myapp
```


常见坑/追问：


- `strace` 不能看用户态函数调用（如自己写的函数），那是 `gdb` 或 `perf` 的工作范围。
- 追问：如何用 `strace` 排查程序启动慢的问题？看 `openat` 调用序列，找耗时的文件访问（如 DNS 查询或缺失的配置文件导致的慢路径）。

---

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？

---

## 📊 本章统计

| 指标 | 数量 |
|------|------|
| 总题目数 | 15 |
| 🟢 入门 | 1 |
| 🟡 进阶 | 8 |
| 🔴 高难 | 6 |
