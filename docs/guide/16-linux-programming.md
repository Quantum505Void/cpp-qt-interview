# 16. Linux 系统编程


↑ 回到目录


### Q1: ⭐🟢 用户态和内核态的区别是什么？


A: 结论：用户态运行普通应用，权限受限；内核态运行操作系统核心代码，权限最高。系统调用是用户态进入内核态的主要通道。


详细解释：


- 用户态不能直接操作硬件或任意内存。
- 进程要读文件、发网络包、创线程，通常都要通过 syscall。
- 切换到内核态有开销，所以高频 syscall 会影响性能。


常见坑/追问：


- 不要把“线程切换”和“用户态/内核态切换”混为一谈。
- 追问：为什么 `read` 比直接访问用户内存慢？因为要陷入内核并做权限检查/拷贝。


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


### Q8: 🟡 fork 在多线程程序里为什么要格外小心？


A: 结论：因为 `fork` 后只有调用它的那个线程会出现在子进程里，但锁状态、库内部状态可能来自父进程的全局现场，容易死锁或状态不一致。


详细解释：


- 多线程进程里其他线程突然“消失”，但 mutex 可能仍处于锁住状态。
- 因此 `fork` 后子进程通常应尽快 `exec`，不要做复杂逻辑。
- 这也是很多系统编程面试爱问的坑点。


常见坑/追问：


- fork 后在子进程里调用复杂日志/内存分配接口都不稳。
- 追问：有没有钩子？有 `pthread_atfork`，但也不是万能药。


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
