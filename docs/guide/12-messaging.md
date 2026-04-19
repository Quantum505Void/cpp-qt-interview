# 12. C++ 消息与通信工具


↑ 回到目录


### Q1: ⭐🟢 进程间通信（IPC）常见方式有哪些？


A: 结论：常见 IPC 包括 pipe、FIFO、message queue、shared memory、socket、signal、semaphore。面试里最好按“是否跨主机、是否高性能、是否双向”来比较。


详细解释：


- pipe：父子进程常见，半双工。
- FIFO：命名管道，无亲缘关系进程也可用。
- message queue：按消息边界传递。
- shared memory：速度快，但需要自己处理同步。
- socket：本机/跨机都能用，通用性最强。
- signal：适合通知，不适合传大量数据。


代码示例：


```cpp
int fd[2];
pipe(fd);
write(fd[1], "ok", 2);
```


常见坑/追问：


- 共享内存最快不代表最省事，同步错误最容易出诡异 bug。
- 追问：为什么 socket 常被统一采用？因为接口一致，跨机扩展方便。


### Q2: ⭐🟡 文件描述符（fd）到底是什么？


A: 结论：文件描述符是进程级的整数句柄，用来索引内核中的打开文件/设备/socket 等对象。Linux 里“万物皆文件”很多场景最终都落到 fd 上。


详细解释：


- `0/1/2` 分别是 stdin/stdout/stderr。
- `open/socket/pipe/accept` 都会返回 fd。
- fd 指向的是进程文件描述符表中的条目，背后关联内核 open file description。
- `dup/dup2` 可以复制 fd，使多个 fd 指向同一底层打开对象。


代码示例：


```cpp
int fd = open("a.txt", O_RDONLY);
int fd2 = dup(fd);
```


常见坑/追问：


- close 一个 fd 后继续使用会触发 EBADF。
- 追问：fork 后子进程会继承 fd 吗？会，除非设置了 `FD_CLOEXEC` 且后续 `exec`。


### Q3: ⭐🟡 pipe 和 socketpair 有什么区别？


A: 结论：pipe 通常是单向字节流；`socketpair` 提供全双工、本地双端通信，更灵活。需要双向通信时 `socketpair` 往往更顺手。


详细解释：


- `pipe(fd)` 得到读端和写端。
- `socketpair(AF_UNIX, SOCK_STREAM, 0, sv)` 创建一对本地相连 socket。
- `socketpair` 支持 `send/recv`，还能结合更多 socket 语义。


代码示例：


```cpp
int sv[2];
socketpair(AF_UNIX, SOCK_STREAM, 0, sv);
write(sv[0], "hi", 2);
char buf[16]{};
read(sv[1], buf, sizeof(buf));
```


常见坑/追问：


- pipe 如果两边都不关无用端，读写阻塞和 EOF 判断会很难看。
- 追问：为什么有些守护进程更喜欢 `socketpair`？因为可双向、行为更接近 socket。


### Q4: ⭐🔴 fork/exec 的关系是什么？


A: 结论：`fork` 复制当前进程，`exec` 用新程序替换当前进程映像。二者常组合成“父进程 fork，子进程 exec 新程序”。


详细解释：


- `fork()` 后会有父子两个执行流，返回值不同。
- 子进程最初几乎和父进程一样，但地址空间是写时复制（COW）。
- `exec*()` 成功后不会返回，当前进程代码/数据段会被新程序替换。
- shell 执行外部命令的核心机制就是 fork + exec。


代码示例：


```cpp
pid_t pid = fork();
if (pid == 0) {
    execlp("ls", "ls", "-l", nullptr);
    _exit(127);
} else if (pid > 0) {
    waitpid(pid, nullptr, 0);
}
```


常见坑/追问：


- fork 后子进程里不要随便调用非 async-signal-safe 的复杂逻辑，尤其多线程程序。
- 追问：为什么 `exec` 前常配合 `dup2`？为了重定向标准输入输出。


### Q5: ⭐🟡 什么是消息队列？System V 和 POSIX 有什么区别？


A: 结论：消息队列是按“消息边界”而不是纯字节流传输数据的 IPC 方式。System V 和 POSIX 都能做，但接口风格和命名方式不同。


详细解释：


- System V：`msgget/msgsnd/msgrcv`，历史悠久。
- POSIX：`mq_open/mq_send/mq_receive`，接口更现代，支持优先级。
- 消息队列适合离散消息，不适合超大吞吐流数据。


代码示例：


```cpp
// POSIX mq 示例伪代码
mqd_t mq = mq_open("/demo", O_CREAT | O_RDWR, 0644, nullptr);
```


常见坑/追问：


- 队列满/空时会阻塞，注意非阻塞和超时策略。
- 追问：为什么日志系统常不用消息队列承载海量正文？因为复制和上下文切换成本不低。


### Q6: ⭐🟡 共享内存为什么快？缺点是什么？


A: 结论：共享内存快，因为数据不需要在内核和用户态之间反复拷贝；缺点是同步复杂、边界管理困难、很容易出现并发一致性问题。


详细解释：


- 共享内存本质是多个进程映射到同一段物理页。
- 写入方直接写，读取方直接读，减少 memcpy 和系统调用。
- 但它不自带消息边界、锁、版本管理，需要配合 mutex/semaphore/lock-free 方案。


代码示例：


```cpp
int fd = shm_open("/demo", O_CREAT | O_RDWR, 0644);
ftruncate(fd, 4096);
void* p = mmap(nullptr, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
```


常见坑/追问：


- 别忘了 `munmap`、`close`、`shm_unlink` 生命周期管理。
- 追问：共享内存和 `mmap` 是什么关系？POSIX 共享内存通常最后也是 `mmap` 到进程地址空间。


### Q7: 🟡 什么是 Unix Domain Socket？


A: 结论：Unix Domain Socket 是本机进程间通信的 socket 形式，不走 IP 协议栈，通常比 TCP 本地回环更轻量。适合本机服务间通信。


详细解释：


- 地址形式可以是文件路径，也可以是 abstract namespace（Linux）。
- 支持 stream/datagram。
- 除了传数据，还能传递文件描述符（SCM_RIGHTS），这是它很强的一点。


代码示例：


```cpp
int fd = socket(AF_UNIX, SOCK_STREAM, 0);
```


常见坑/追问：


- 路径型 UDS 文件退出后忘记 unlink 会导致下次 bind 失败。
- 追问：为什么 nginx、数据库、本地 daemon 常用它？因为本机通信更高效，权限控制也方便。


### Q8: ⭐🟡 ZeroMQ、MQTT、DBus 这类工具各适合什么场景？


A: 结论：ZeroMQ 适合高性能消息模式封装，MQTT 适合物联网轻量发布订阅，DBus 适合 Linux 桌面/系统组件总线通信。它们不是同一层面的替代关系。


详细解释：


- ZeroMQ 更像“高级 socket 库”，有 pub/sub、req/rep、push/pull 等模式。
- MQTT 是协议，需要 broker，适合弱网设备。
- DBus 是 Linux 系统级消息总线，常见于桌面和系统服务协作。
- Qt 中分别有不同集成方式，如 `QtDBus`、第三方 MQTT/ZeroMQ 库。


常见坑/追问：


- 不要把 ZeroMQ 当成传统意义的 broker。
- 追问：工业设备上报数据为什么常见 MQTT？因为协议轻、生态广、支持 topic。


### Q9: 🟡 Qt 里常见的消息/通信模块有哪些？


A: 结论：Qt 常见通信工具包括 `QTcpSocket`、`QUdpSocket`、`QSerialPort`、`QLocalSocket`、`QDBus` 等，覆盖网络、本地 IPC、串口等常用需求。


详细解释：


- `QTcpSocket/QUdpSocket`：网络通信。
- `QLocalSocket/QLocalServer`：本地进程通信，底层通常对应 UDS/Named Pipe。
- `QSerialPort`：串口。
- `QProcess`：启动子进程并收发标准输出，本质上也是一种进程通信手段。


代码示例：


```cpp
QTcpSocket socket;
socket.connectToHost("127.0.0.1", 8000);
```


常见坑/追问：


- Qt 的 readyRead 是“有数据到了”，不代表应用层消息收完整了，仍要自己做拆包。
- 追问：为什么 `QProcess` 也算通信工具？因为它封装了子进程 stdin/stdout/stderr 管道。


### Q10: ⭐🔴 如何设计可靠的应用层消息协议？


A: 结论：可靠协议设计至少要有边界、长度、类型、版本、校验和错误处理。TCP 只保证字节流，不保证你的“消息”概念。


详细解释：


- 常见包格式：magic + version + type + length + payload + checksum。
- 要考虑粘包拆包、大小端、兼容升级、异常包丢弃、超时重传。
- 文本协议调试方便，二进制协议更省带宽。
- 对高可靠场景还要考虑序号、ACK、幂等。


代码示例：


```cpp
struct Header {
    uint32_t magic;
    uint16_t version;
    uint16_t type;
    uint32_t length;
};
```


常见坑/追问：


- 直接把 C++ struct 裸发网络是高危行为，涉及对齐、字节序、ABI。
- 追问：TCP 为什么会粘包？因为它是字节流，不保留应用层发送边界。
