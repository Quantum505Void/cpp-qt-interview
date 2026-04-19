# 42. 嵌入式与上位机通信协议


↑ 回到目录


graph TD
    A[上位机发送升级请求] --> B[MCU 回复 ACK]
    B --> C[发送固件分片 N]
    C --> D{MCU 校验 CRC}
    D -->|通过| E{是否最后分片?}
    D -->|失败| F[请求重传分片 N]
    F --> C
    E -->|否| G[发送分片 N+1]
    G --> C
    E -->|是| H[MCU 完整性校验]
    H --> I[MCU 重启应用新固件]

### Q1: ⭐⭐🟡 Modbus RTU 与 Modbus TCP 帧格式有何区别？如何用 Qt 实现？


**结论**：Modbus RTU 基于串口（带 CRC），Modbus TCP 基于以太网（带 MBAP 头），Qt 通过 `QtSerialBus` 模块统一封装。


**详解**：


**Modbus RTU 帧格式**：


```
| 设备地址(1B) | 功能码(1B) | 数据(nB) | CRC16(2B) |
```


**Modbus TCP 帧格式（MBAP Header）**：


```
| 事务标识(2B) | 协议标识(2B,固定0) | 长度(2B) | 单元标识(1B) | 功能码(1B) | 数据(nB) |
```


**Qt 实现 Modbus RTU 读保持寄存器（FC03）**：


```cpp
#include <QModbusRtuSerialClient>

QModbusRtuSerialClient *modbus = new QModbusRtuSerialClient(this);
modbus->setConnectionParameter(QModbusDevice::SerialPortNameParameter, "COM3");
modbus->setConnectionParameter(QModbusDevice::SerialBaudRateParameter, QSerialPort::Baud9600);
modbus->connectDevice();

QModbusDataUnit readUnit(QModbusDataUnit::HoldingRegisters, 0, 10);  // 从地址0读10个
if (auto *reply = modbus->sendReadRequest(readUnit, 1)) {  // 设备地址1
    connect(reply, &QModbusReply::finished, this, [reply]() {
        const auto units = reply->result();
        for (int i = 0; i < units.valueCount(); i++)
            qDebug() << "Reg" << i << ":" << units.value(i);
        reply->deleteLater();
    });
}
```


**常见追问**：


- Modbus RTU CRC 如何计算？CRC-16/IBM 算法，多项式 0x8005
- Modbus TCP 为何不需要 CRC？TCP 本身有校验，MBAP 头的长度字段替代了 RTU 的 CRC


---


### Q2: ⭐⭐🟡 CANbus 帧格式是什么？Qt SerialBus 模块如何操作 CAN 总线？


**结论**：CAN 帧由仲裁场（ID）、控制场（DLC）、数据场（0-8B）组成，Qt 通过 `QCanBusDevice` 提供统一接口。


**详解**：


**CAN 标准帧格式**：


```
| SOF(1bit) | ID(11bit) | RTR(1bit) | IDE(1bit) | DLC(4bit) | Data(0-8B) | CRC(15bit) | ACK(2bit) | EOF(7bit) |
```


CAN 扩展帧（CAN 2.0B）：ID 扩展为 29bit


**Qt 操作 CAN 总线**：


```cpp
#include <QCanBus>
#include <QCanBusFrame>

QCanBusDevice *device = QCanBus::instance()->createDevice("socketcan", "can0");
device->connectDevice();

// 发送帧
QCanBusFrame frame;
frame.setFrameId(0x123);
frame.setPayload(QByteArray::fromHex("0102030405060708"));
device->writeFrame(frame);

// 接收帧
connect(device, &QCanBusDevice::framesReceived, this, [device]() {
    while (device->framesAvailable()) {
        QCanBusFrame f = device->readFrame();
        qDebug() << Qt::hex << f.frameId() << f.payload().toHex();
    }
});
```


**常见追问**：


- CAN FD 与 CAN 2.0 区别？CAN FD 数据场最大 64B，速率可达 8Mbps（数据段），向下兼容
- socketcan 是什么？Linux 内核 CAN 驱动框架，将设备抽象为网络接口，`ip link set can0 up type can bitrate 500000`


---


### Q3: ⭐⭐🟡 自定义串口协议帧格式如何设计？关键要素有哪些？


**结论**：自定义协议帧至少包含帧头、长度、命令码、数据和校验五个字段，设计时需考虑同步、定界和错误检测。


**详解**：


**典型帧格式**：


```
| 帧头(2B) | 长度(2B) | 命令码(1B) | 序列号(1B) | 数据(nB) | CRC16(2B) | 帧尾(2B) |
  0xAA55   数据段长度   功能标识    防重放       payload   校验数据段   0x55AA
```


**设计要点**：


1. **帧头**：选择在业务数据中出现概率低的字节序列，如 `0xAA55`
2. **长度字段**：明确是否包含头/尾/校验，通常只计算数据区长度
3. **校验算法**：简单场景用 XOR/累加和；可靠传输用 CRC16/CRC32
4. **帧尾**：可选，有利于快速同步，但增加协议开销


**Qt 封包示例**：


```cpp
QByteArray buildFrame(quint8 cmd, const QByteArray &data) {
    QByteArray frame;
    frame.append("ªU", 2);     // 帧头
    quint16 len = data.size();
    frame.append((len >> 8) & 0xFF);
    frame.append(len & 0xFF);
    frame.append(cmd);
    frame.append(data);
    quint16 crc = crc16(frame.mid(4));
    frame.append((crc >> 8) & 0xFF);
    frame.append(crc & 0xFF);
    frame.append("Uª", 2);     // 帧尾
    return frame;
}
```


**常见追问**：


- 为何需要序列号字段？防止重发导致命令重复执行，上位机通过序列号匹配响应
- 帧头在数据中出现怎么办？字节填充（转义）：将数据中的帧头字节替换为转义序列


---


### Q4: ⭐⭐🔴 串口通信粘包/拆包问题如何处理？Qt 中的实现策略是什么？


**结论**：粘包/拆包是字节流传输的本质问题，解决方案是在接收缓冲区中用帧状态机解析。


**详解**：


**问题原因**：串口/TCP 是字节流，不保留消息边界；每次 `readyRead` 收到的数据量不确定（可能是半帧、一帧或多帧）。


**状态机解析方案**：


```cpp
void FrameParser::parseFrames() {
    while (true) {
        // 1. 查找帧头
        int pos = m_buffer.indexOf(QByteArray("ªU", 2));
        if (pos < 0) { m_buffer.clear(); return; }
        if (pos > 0) m_buffer.remove(0, pos);  // 丢弃帧头前的垃圾

        // 2. 等待长度字段
        if (m_buffer.size() < 4) return;
        quint16 dataLen = ((quint8)m_buffer[2] << 8) | (quint8)m_buffer[3];
        int frameLen = 2 + 2 + 1 + dataLen + 2 + 2;  // 头+长度+命令+数据+CRC+尾

        // 3. 等待完整帧到来
        if (m_buffer.size() < frameLen) return;

        // 4. 校验并提取帧
        QByteArray frame = m_buffer.left(frameLen);
        if (validateCRC(frame))
            emit frameReceived(frame);
        m_buffer.remove(0, frameLen);
    }
}
```


**常见追问**：


- 帧头恰好出现在数据中怎么办？CRC 校验失败后跳过，从下一个疑似帧头重新尝试
- 缓冲区无限增长怎么防止？设置最大大小上限，超出则清空并重新同步


---


### Q5: ⭐⭐🔴 OTA 固件升级流程如何设计？分片传输、CRC 校验、断点续传如何实现？


**结论**：OTA 升级分为握手、分片传输、整包校验、激活四阶段，断点续传依赖设备端记录已接收分片索引。


**详解**：


**OTA 通信流程**：


```
上位机                              MCU
  │── OTA_START（版本/大小/分片数）──►│
  │◄── ACK（就绪）─────────────────│
  │── FRAME(index=0, 256B) ────────►│ 写 Flash
  │◄── ACK(index=0) ───────────────│
  │    ...（断线后从 index=N 续传）   │
  │── OTA_END（整包 CRC32）──────────►│
  │◄── ACK(OK) / NACK(CRC 失败) ───│
  │── REBOOT ──────────────────────►│ 跳转新固件
```


**Qt 上位机关键代码**：


```cpp
void OtaManager::sendFirmware(const QString &filePath) {
    QByteArray firmware = QFile(filePath).readAll();
    const int CHUNK = 256;
    int total = (firmware.size() + CHUNK - 1) / CHUNK;
    quint32 crc = crc32(firmware);

    sendCommand(OTA_START, {firmware.size(), total, crc});

    for (int i = m_resumeIndex; i < total; i++) {
        sendFrame(OTA_FRAME, i, firmware.mid(i * CHUNK, CHUNK));
        if (!waitAck(i, 3000)) {
            m_resumeIndex = i;  // 记录断点，下次续传
            emit otaFailed("Timeout at chunk " + QString::number(i));
            return;
        }
        emit progressChanged(i * 100 / total);
    }
    sendCommand(OTA_END, {crc});
}
```


**常见追问**：


- 为何要分片？MCU RAM 有限，无法缓存整个固件，分片逐步写入 Flash
- CRC 校验失败怎么办？重传全部固件，或设备端记录错误分片索引仅重传缺失部分


---


### Q6: ⭐⭐🟡 HID 协议 Report Descriptor 是什么？如何读写 HID 设备？


**结论**：Report Descriptor 描述 HID 报告的字段布局（位域含义），通过 `hidapi` 库可跨平台读写 HID 设备数据。


**详解**：


**HID 报告描述符示例**（简化鼠标）：


```
Usage Page (Generic Desktop)   // 设备类别
Usage (Mouse)
Collection (Application)
  Usage (Pointer)
  Collection (Physical)
    Usage (X), Usage (Y)       // 相对坐标轴
    Logical Min (-127), Max (127)
    Report Size (8), Count (2)
    Input (Data, Variable, Relative)  // 两个 8bit 相对值
  End Collection
End Collection
```


**使用 hidapi 读写 HID 设备（Qt 集成）**：


```cpp
#include <hidapi.h>

hid_device *handle = hid_open(0x1234, 0x5678, nullptr);  // VID, PID

// 读输入报告（鼠标/HID 设备数据）
unsigned char buf[65] = {0};
int res = hid_read_timeout(handle, buf, sizeof(buf), 1000);
if (res > 0) {
    int x = (int8_t)buf[1];
    int y = (int8_t)buf[2];
}

// 发输出报告（如控制 LED）
unsigned char out[65] = {0x00, 0x01};
hid_write(handle, out, 65);
hid_close(handle);
```


**常见追问**：


- HID 为何不需要驱动？USB HID 是 USB 规范标准类，OS 内置 HID 驱动
- Report ID 的作用？一个设备可有多种报告，Report ID 区分类型（如键盘/触摸板在同一设备）


---


### Q7: ⭐⭐🔴 上位机与 MCU 通信时序与超时重传机制如何设计？


**结论**：通过请求-响应模型 + 定时器超时 + 重试计数器实现可靠通信，关键是处理好超时、重发、去重三个问题。


**详解**：


**通信状态机**：


```
IDLE ──发送命令──► WAITING_ACK
                      │
              ┌───────┴───────┐
           收到ACK         超时（500ms）
              │               │
           SUCCESS    重试次数 < 3？
                        ├─ 是 → 重发 → WAITING_ACK
                        └─ 否 → FAILED
```


**Qt 实现**：


```cpp
class ReliableComm : public QObject {
    QTimer *m_timer;
    int m_retryCount = 0;
    QByteArray m_pendingFrame;
    quint8 m_pendingSeq;

    void sendRequest(quint8 cmd, const QByteArray &data) {
        m_pendingSeq = nextSeq();
        m_pendingFrame = buildFrame(cmd, m_pendingSeq, data);
        m_retryCount = 0;
        doSend();
    }

    void doSend() {
        m_serialPort->write(m_pendingFrame);
        m_timer->start(500);
    }

    void onTimeout() {
        if (++m_retryCount < 3) doSend();
        else { m_timer->stop(); emit commFailed("Max retries"); }
    }

    void onFrameReceived(const QByteArray &frame) {
        if (parseSeq(frame) == m_pendingSeq) {  // 序列号匹配才处理
            m_timer->stop();
            emit responseReceived(frame);
        }
        // 序列号不匹配：丢弃旧响应（去重）
    }
};
```


**常见追问**：


- 为什么需要序列号？防止超时重发后，旧响应被误认为新请求的响应
- 超时时间如何选择？通常为往返时延的 3-5 倍，串口通信一般 200-1000ms
- 全双工通信如何处理？MCU 主动上报与应答通过命令码区分，不能混用同一条流


---


### Q8: ⭐⭐🟡 Qt SerialBus 模块支持哪些协议？工业通信方案如何选型？


**结论**：Qt SerialBus 原生支持 Modbus 和 CAN 两大工业协议，选型依据是总线拓扑、节点数和实时性要求。


**详解**：


**Qt SerialBus 模块结构**：


```
QtSerialBus
├── QCanBus（CAN 总线）
│   ├── socketcan（Linux SocketCAN）
│   ├── peakcan（PEAK USB-to-CAN）
│   └── vectorcan（Vector CANalyzer）
└── QModbusMaster / QModbusSlave
    ├── QModbusRtuSerialClient（RTU/串口）
    └── QModbusTcpClient（TCP/以太网）
```


**工业通信选型对比**：


| 协议 | 速率 | 距离 | 节点数 | 典型应用 |
| --- | --- | --- | --- | --- |
| RS-232 | 115.2kbps | 15m | 2 | 简单设备调试 |
| RS-485/Modbus RTU | 10Mbps | 1200m | 32 | PLC、仪表 |
| CAN 2.0 | 1Mbps | 40m | 110 | 汽车 ECU、工业控制器 |
| CAN FD | 8Mbps | 40m | 110 | 高速控制系统 |
| Modbus TCP | 100Mbps | 不限 | 不限 | 工厂以太网 |
| EtherCAT | 100Mbps | 不限 | 65535 | 高实时性运动控制 |


**常见追问**：


- Qt 是否支持 EtherCAT？Qt 原生不支持，需要第三方库（如 SOEM）
- Modbus 轮询延迟高怎么优化？合并地址连续的寄存器为一次请求，减少轮询次数，提高波特率


---


## 📊 统计


- 总章节数：42
- 总题目数：391
- 难度分布：🟢 基础 67 题 | 🟡 中级 233 题 | 🔴 高级 59 题
- 高频题（⭐）：237 题


*文档版本：2026年4月 v4.1*


*定位：C++/Qt 桌面开发工程师（3年经验）面试备考*
