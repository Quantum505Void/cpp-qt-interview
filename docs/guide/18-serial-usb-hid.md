# 18. 串口与 USB/HID 通信


↑ 回到目录


sequenceDiagram
    participant H as Host
    participant D as Device
    H->>D: USB Reset
    D->>H: Device Descriptor
    H->>D: Set Address
    H->>D: Get Configuration Descriptor
    H->>D: Set Configuration
    Note over H,D: 枚举完成，可正常通信

### Q1: ⭐🟢 串口通信最核心的参数有哪些？


A: 结论：串口最核心的是波特率、数据位、停止位、校验位、流控。两端这些参数不一致，通信要么乱码要么根本不通。


详细解释：


- 常见配置：115200, 8N1。
- 流控分软件流控（XON/XOFF）和硬件流控（RTS/CTS）。
- 工业场景里还要区分 RS-232、RS-485 的电气层。


代码示例：


```cpp
QSerialPort port;
port.setBaudRate(QSerialPort::Baud115200);
port.setDataBits(QSerialPort::Data8);
port.setParity(QSerialPort::NoParity);
port.setStopBits(QSerialPort::OneStop);
```


常见坑/追问：


- 波特率对了不代表就通，校验和流控也要一致。
- 追问：8N1 是什么意思？8 数据位、No parity、1 停止位。


### Q2: ⭐🟡 串口为什么会出现粘包、拆包、半包？


A: 结论：因为串口本质是连续字节流，没有天然消息边界。应用层必须自己定义帧格式来切分数据。


详细解释：


- 一次 `readyRead` 不代表收到完整一帧。
- 一帧数据可能被拆成多次到达，也可能多帧挤在一起。
- 常见做法是用固定头 + 长度 + 校验，或结束符协议。


常见坑/追问：


- 不要拿 `readAll()` 直接当一整帧处理。
- 追问：串口和 TCP 在这一点像吗？很像，都是字节流语义。


### Q3: ⭐🟡 termios 在 Linux 串口编程里负责什么？


A: 结论：`termios` 用来配置串口设备的波特率、数据格式、超时、阻塞行为等。Linux 下做原生串口编程几乎绕不开它。


详细解释：


- 打开设备通常是 `/dev/ttyS`、`/dev/ttyUSB`、`/dev/ttyACM*`。
- `tcgetattr/tcsetattr` 获取和设置属性。
- raw mode 可关闭行缓冲和特殊字符处理。


代码示例：


```cpp
int fd = open("/dev/ttyUSB0", O_RDWR | O_NOCTTY);
struct termios tio{};
tcgetattr(fd, &tio);
cfsetispeed(&tio, B115200);
cfsetospeed(&tio, B115200);
tio.c_cflag |= (CLOCAL | CREAD);
tcsetattr(fd, TCSANOW, &tio);
```


常见坑/追问：


- 忘了设置 raw mode，`


`、回显、特殊字符会把数据流搞乱。


- 追问：`O_NOCTTY` 有什么用？避免设备成为控制终端。


### Q4: ⭐🟡 RS-232、RS-485、TTL 串口有什么区别？


A: 结论：它们主要区别在电平标准、传输距离、抗干扰能力和拓扑。面试时别把“串口协议”和“电气层”混了。


详细解释：


- TTL：MCU 板级常见，不能直接长距离传输。
- RS-232：点对点，电平与 TTL 不同。
- RS-485：差分传输、抗干扰强、适合总线多节点、远距离工业场景。
- 上位机常通过 USB 转串口芯片接入这些接口。


常见坑/追问：


- TTL 不能直接怼 RS-232/485，电平不兼容可能直接烧。
- 追问：485 为什么适合工业现场？差分、距离远、抗干扰强。


### Q5: ⭐🟡 USB CDC、USB HID 分别是什么？


A: 结论：USB CDC 常把设备抽象成虚拟串口；USB HID 是人机接口类，免驱特性强、报文小、轮询式常见。二者在上位机访问方式上差异很大。


详细解释：


- CDC 设备在 Linux 上常表现为 `/dev/ttyACM*`。
- HID 设备常通过 `/dev/hidraw*` 或 libhidapi 访问。
- HID 不需要自定义驱动的门槛低，但 payload 和报文组织有其限制。


常见坑/追问：


- “USB 设备就是串口”是错的，USB 类别很多。
- 追问：为什么一些设备选 HID？免驱、跨平台、部署方便。


### Q6: ⭐🔴 HID 报告（Report）是什么？


A: 结论：HID 通过 report descriptor 描述数据格式，主机和设备按 report 结构收发数据。你看到的每次读写通常都是一个 report。


详细解释：


- report descriptor 描述字段含义、长度、usage。
- 可能有 input report、output report、feature report。
- 有些设备第一个字节是 report ID。
- 上位机读写时必须严格按报告格式组织字节。


代码示例：


```cpp
// hidapi 伪代码
unsigned char buf[65] = {0}; // buf[0] 常为 report ID
hid_write(handle, buf, sizeof(buf));
```


常见坑/追问：


- 忽略 report ID 会导致长度和协议全部错位。
- 追问：为什么 HID 报文常是固定长度？因为报告描述和端点规格决定了传输格式。


### Q7: 🟡 Qt 中怎么做串口通信？


A: 结论：Qt 里通常用 `QSerialPort`，配合信号槽异步收发，界面程序里非常方便。它封装了跨平台差异。


详细解释：


- 打开前设置端口名和参数。
- 用 `readyRead` 收包。
- 注意拆包缓存和线程模型。
- 可以通过 `QSerialPortInfo` 枚举设备。


代码示例：


```cpp
connect(&port, &QSerialPort::readyRead, this, [this] {
    buffer_ += port.readAll();
    parseFrames();
});
```


常见坑/追问：


- `waitForReadyRead` 在 GUI 线程里乱用可能卡界面。
- 追问：设备插拔怎么处理？监听枚举变化或定时扫描重连。


### Q8: ⭐🟡 串口/USB 通信排障一般怎么做？


A: 结论：按“物理层 → 驱动枚举 → 参数配置 → 原始字节流 → 协议解析”逐层排。不要一上来就怀疑代码。


详细解释：


- 先确认设备枚举是否存在：`dmesg`、`lsusb`、`/dev/tty*`。
- 再确认权限和占用。
- 用串口工具/抓包工具先看原始数据。
- 最后才看应用层组帧、CRC、状态机。


常见坑/追问：


- 上位机收不到数据，可能只是波特率/校验位错了，不一定是程序 bug。
- 追问：USB HID 怎么抓包？Linux 下可看 `usbmon`、Wireshark，Windows 可用 USBPcap。


### Q9: 🟡 非阻塞串口读写要注意什么？


A: 结论：非阻塞模式下 `read/write` 可能立刻返回 EAGAIN，需要配合 `select/poll/epoll` 或事件通知机制使用。不能按阻塞思维写循环。


详细解释：


- 非阻塞适合集成进事件循环。
- 写串口也可能短写，尤其底层缓冲满时。
- 工业程序要考虑超时和重发策略。


常见坑/追问：


- while 死循环重试会把 CPU 烧高。
- 追问：GUI 程序为什么偏爱异步信号槽模式？因为不会阻塞主线程。


### Q10: ⭐🔴 串口和 USB/HID 项目中最容易踩的坑是什么？


A: 结论：最容易踩的坑是把“链路通了”和“协议通了”混为一谈。物理连接、驱动识别、字节流、帧解析、业务状态机，这五层可能分别出错。


详细解释：


- 串口能打开不代表参数对。
- 有原始数据不代表拆包和 CRC 对。
- CRC 对了不代表命令时序和设备状态满足要求。
- USB 枚举成功也不代表 report 格式写对。


常见坑/追问：


- 现场排障时一定保留十六进制原始日志，这是救命绳。
- 追问：为什么调设备经常“换个工具就好了”？因为工具默认参数/时序/流控可能和你程序不同。
