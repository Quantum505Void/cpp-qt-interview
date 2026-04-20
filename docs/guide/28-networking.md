# 28. 网络编程


↑ 回到目录


### Q1: ⭐🟢 TCP 和 UDP 的核心区别是什么？


A: 结论：TCP 面向连接、可靠有序、字节流；UDP 无连接、尽力而为、保留报文边界。


详细解释：


- TCP 适合可靠传输，如文件、业务协议、数据库连接。
- UDP 适合实时性优先，如语音、视频、广播发现。


常见坑/追问：


- TCP 没有消息边界，这是后面“粘包拆包”高频题基础。


### Q2: ⭐🟢 什么是 TCP 粘包/拆包？怎么解决？


A: 结论：TCP 是字节流，不保证一次 `send` 对应一次 `recv`，应用层必须自己设计消息边界。


详细解释：


- 接收端可能一次收到半包、整包、多个包拼一起。
- 常见方案：固定长度、分隔符、长度字段 + payload。
- 工业协议、上位机通信里最常见的是“包头 + 长度 + 数据 + CRC”。


代码示例：


```cpp
struct PacketHeader {
    uint16_t magic;
    uint16_t len;
};
```


常见坑/追问：


- 不要把“粘包”理解成 TCP 出错，它是协议设计者要处理的正常现象。


### Q3: ⭐🟡 select、poll、epoll 有什么区别？


A: 结论：`select/poll` 是遍历式就绪模型，`epoll` 是事件驱动式就绪通知，适合高并发大量连接场景。


详细解释：


- `select` 有 fd 数量限制，还要反复拷贝集合。
- `poll` 去掉了固定上限，但仍是线性扫描。
- `epoll` 通过内核维护关注集合，减少无效遍历。


常见坑/追问：


- 回答别停在“epoll 更快”，要说清楚快在哪。


### Q4: ⭐🟡 Reactor 模式是什么？


A: 结论：Reactor 是“事件到达后分发给对应处理器”的架构模式，`epoll + event loop + callback` 就是典型实现。


详细解释：


- 一个线程/线程池等待 IO 事件。
- 事件就绪后分发到 read/write/accept handler。
- Qt 的事件循环、本地 socket notifier 都能类比理解。


代码示例：


```cpp
// 伪代码：reactor loop
while (true) {
    auto events = epoll_wait(...);
    for (auto& e : events) dispatch(e);
}
```


常见坑/追问：


- 容易和 Proactor 混淆：前者“就绪通知”，后者“完成通知”。


### Q5: 🟡 上位机协议解析模块怎么设计更稳？


A: 结论：建议做成“字节流接收层 → 帧同步层 → 协议解码层 → 业务分发层”的分层架构，并显式处理半包、错包、超时、重发、校验失败。


详细解释：


- 接收层只负责收字节。
- 帧层识别包头、长度、CRC，解决粘包拆包。
- 解码层负责大小端、字段解析、版本兼容。
- 分发层再路由到业务命令处理。


常见坑/追问：


- 工程里最怕“socket 回调里直接写业务解析”，后期几乎必炸。


### Q6: 🟡 心跳、重连、超时机制通常怎么设计？


A: 结论：通信系统必须把“连接还在”“对端还活着”“请求是否超时”分开设计，不能只靠 TCP 连接状态判断业务可用性。


详细解释：


- 心跳用于活性检测。
- 请求超时用于请求级 SLA。
- 重连要带退避和状态机，避免雪崩重试。


常见坑/追问：


- TCP 已连接不代表业务健康，可能对端应用早就卡死了。


### Q7: 🔴 epoll ET 和 LT 有什么区别？


A: 结论：LT（水平触发）只要缓冲区还有数据就会持续通知；ET（边沿触发）只在状态变化时通知一次，要求你一次尽量读空/写空。


详细解释：


- LT 更容易写对。
- ET 减少重复通知，性能潜力更高，但实现更容易漏读。
- ET 模式一般要配合非阻塞 fd 和循环读写。


常见坑/追问：


- 面试官常追问：为什么 ET 下必须 while 读到 `EAGAIN`？


### Q8: 🔴 高并发网络程序为什么不能让业务处理阻塞事件循环？


A: 结论：因为事件循环线程的职责是快速收发和分发，一旦在里面做重计算/阻塞 IO，会拖慢所有连接，形成队头阻塞。


详细解释：


- 正确做法通常是 IO 线程轻量收包，业务任务投递到 worker 池。
- 这也是“网络线程只做 IO、业务线程做计算”的分层思想。


常见坑/追问：


- Qt 里也一样：不要在 readyRead/槽函数里做大计算把主线程卡死。


### Q9: ⭐🟡 select/poll/epoll 三者的区别和演进逻辑是什么？


A: 结论：select 受文件描述符数量限制，poll 去掉限制但仍需全量遍历，epoll 用事件驱动只返回就绪集合，是大并发场景的主流选择。


详细解释：


- `select`：fd_set 位图，默认上限 1024，每次调用要把 fd 集合从用户空间复制到内核，返回后要遍历全集。
- `poll`：用 pollfd 数组，无数量限制，但同样是 O(n) 轮询，线性扫描随连接数增大变慢。
- `epoll`：内核维护红黑树（注册）+ 就绪链表（激活），`epoll_wait` 只返回真正就绪的 fd，复杂度接近 O(就绪数)。


代码示例：


```cpp
int epfd = epoll_create1(0);
epoll_event ev;
ev.events = EPOLLIN | EPOLLET;
ev.data.fd = sockfd;
epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev);

epoll_event events[MAX_EVENTS];
int n = epoll_wait(epfd, events, MAX_EVENTS, -1);
for (int i = 0; i < n; ++i) {
    // 只处理就绪 fd
}
```


常见坑/追问：


- 追问：epoll 适合连接数多但活跃连接少的场景，若全都活跃，优势会收窄。
- 追问：epoll 与 select 的内存模型差异在哪？


### Q10: ⭐🟡 非阻塞 Socket 和阻塞 Socket 有什么本质区别？什么时候用哪种？


A: 结论：阻塞 socket 调用会挂起线程直到操作完成；非阻塞 socket 立即返回（可能是 EAGAIN），调用者需自行重试或配合事件通知机制。


详细解释：


- 阻塞模式简单直观，适合"一线程处理一连接"模型（如简单工具、测试程序）。
- 非阻塞模式必须配合 select/poll/epoll 或 io_uring，用于高并发事件驱动服务器。
- 设置非阻塞：`fcntl(fd, F_SETFL, O_NONBLOCK)` 或 `SOCK_NONBLOCK` 标志。


代码示例：


```cpp
int flags = fcntl(fd, F_GETFL, 0);
fcntl(fd, F_SETFL, flags | O_NONBLOCK);

// 非阻塞读
ssize_t n = read(fd, buf, sizeof(buf));
if (n < 0 && errno == EAGAIN) {
    // 数据暂未到达，稍后再试
}
```


常见坑/追问：


- 非阻塞写时若缓冲区满，write 返回 EAGAIN，必须把剩余数据放回发送队列等待可写事件，否则会丢数据。


### Q11: ⭐🟡 Qt 网络编程中 QTcpSocket 信号槽的正确使用方式是什么？


A: 结论：用 `readyRead` 信号驱动接收、`bytesWritten` 信号处理写完通知，并配合粘包处理逻辑，避免在槽函数中做阻塞操作。


详细解释：


- `readyRead`：有数据到达，读到缓冲区后交给帧解析器处理。
- `disconnected`：对端断开，触发重连或清理逻辑。
- `errorOccurred`：网络错误，要区分是超时、连接拒绝还是中途断开。
- 不要在槽函数里 `waitForReadyRead`，会阻塞事件循环。


代码示例：


```cpp
connect(socket, &QTcpSocket::readyRead, this, [this]() {
    rxBuf.append(socket->readAll());
    parseFrames(rxBuf); // 帧解析，处理粘包
});
connect(socket, &QTcpSocket::disconnected, this, &MyClient::onDisconnected);
```


常见坑/追问：


- `readAll()` 每次取走所有数据，但不保证是完整帧，必须有缓冲 + 解析逻辑。


### Q12: ⭐🟡 心跳机制的作用是什么？有哪些实现方式？


A: 结论：心跳用于检测对端存活和链路健康，避免"半开连接"（连接看似存在但实际已死）。


详细解释：


- TCP keepalive：系统层，可通过 `setsockopt(SO_KEEPALIVE)` 开启，可配置探测间隔和次数，但间隔一般较长（默认 2 小时）。
- 应用层心跳：在协议内定义心跳帧，周期性发送，超时无响应则主动断开重连，实时性更好。
- 常见上位机场景优先用应用层心跳，方便控制超时粒度。


代码示例：


```cpp
// 设置 TCP keepalive
int on = 1, idle = 10, interval = 3, count = 3;
setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &on, sizeof(on));
setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle, sizeof(idle));
setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &interval, sizeof(interval));
setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &count, sizeof(count));
```


常见坑/追问：


- 追问：为什么 TCP keepalive 不够用？因为默认间隔太长、且检测的是 IP 层可达，不检测应用层是否还在响应。


### Q13: 🟡 UDP 广播和组播有什么区别？什么场景用哪种？


A: 结论：广播发送到子网所有主机，组播只发给订阅了特定组地址的主机，效率更高，适合跨网段和大规模设备发现。


详细解释：


- 广播：目标地址为 `255.255.255.255` 或子网广播地址，同网段所有机器都会收到，不可跨路由。
- 组播：目标地址为 `224.0.0.0~239.255.255.255`，加入组 (`IP_ADD_MEMBERSHIP`) 才接收，可跨路由（需要路由器支持 IGMP）。
- 上位机设备发现常用局域网广播，大型工业系统可用组播减少无关主机的报文处理开销。


代码示例：


```cpp
// 加入组播组
ip_mreq mreq;
mreq.imr_multiaddr.s_addr = inet_addr("239.1.1.1");
mreq.imr_interface.s_addr = INADDR_ANY;
setsockopt(sockfd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq));
```


常见坑/追问：


- 广播在大型 VLAN 环境中会造成广播风暴，组播更可控。


### Q14: ⭐🔴 Reactor 模型和 Proactor 模型的区别是什么？


A: 结论：Reactor 是"事件就绪后由我来读写"，Proactor 是"异步 IO 完成后通知我"；前者常见于 Linux epoll 架构，后者对应 Windows IOCP 或 Linux io_uring。


详细解释：


- Reactor：epoll_wait 通知 fd 可读，应用自己调用 read；适合 Linux 高并发服务器。
- Proactor：内核帮你完成 IO，完成后回调通知，应用只处理结果；延迟更低，代码更复杂。
- 常见实现：Reactor → libevent、libuv、Netty；Proactor → IOCP、io_uring 封装。


常见坑/追问：


- 追问：epoll 严格来说是 Reactor，不是 Proactor，io_uring 才更接近 Proactor 模型。
- 追问：Qt 的 QAbstractSocket 内部封装了事件循环，对用户暴露的是信号槽，本质接近 Reactor 封装。


### Q15: ⭐🔴 如何排查上位机 TCP 连接中的丢包或数据不一致问题？


A: 结论：按"物理链路 → 系统缓冲 → 应用层收发逻辑 → 协议解析 → 业务逻辑"逐层排查，并借助 tcpdump/Wireshark 抓包辅助定位。


详细解释：


- 先确认是否真的丢包：抓包看 TCP 序号和重传，区分"网络丢"和"应用没读完"。
- 检查接收缓冲：`SO_RCVBUF` 是否太小，数据是否因读取太慢被覆盖（UDP）。
- 检查应用层粘包处理：是否有 off-by-one、数组越界、解析状态机未重置。
- 若 UDP，检查内核 `netstat -su` 中的 receive buffer errors 和 InErrors。


代码示例：


```bash
# 抓取指定端口的 TCP 包
tcpdump -i eth0 -w cap.pcap tcp port 8888
# 查看 socket 缓冲使用情况
ss -nt sport = :8888
```


常见坑/追问：


- 面试时能说出"先抓包确认是否真丢，再查应用层处理逻辑"会显得有实战经验。
- 追问：TCP 不丢包但数据错乱？通常是应用层帧解析 bug，不是网络问题。
