# 32. 场景设计题

> 难度分布：🟢 入门 1 题 · 🟡 进阶 8 题 · 🔴 高难 6 题

[[toc]]

---


## 一、系统设计基础

### Q1: ⭐🟢 设计一个线程安全日志系统，你会怎么做？


A: 结论：采用多生产者 + 单消费者或分片消费者模型，前台线程轻量写入缓冲，后台线程批量刷盘，并定义背压与丢弃策略。


详细解释：


- 日志接口要尽量非阻塞。
- 数据结构可选有界队列、环形缓冲、双缓冲。
- 落盘策略要支持按大小/时间/级别切分。
- 关键指标包括吞吐、延迟、丢失率、崩溃恢复能力。


常见坑/追问：


- 追问通常会问：磁盘慢怎么办？要么背压，要么丢低优先级日志。

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q2: ⭐🟡 设计一个上位机协议解析系统，你会如何分层？


A: 结论：按“传输层适配 → 字节流缓冲 → 帧解析 → 命令分发 → 业务处理 → 响应编码”分层，保持解析与业务解耦。


详细解释：


- 串口、TCP、USB/HID 可复用统一解析框架。
- 帧层负责包头同步、长度校验、CRC 校验、重组。
- 命令层用注册表/工厂避免巨型 if-else。


常见坑/追问：


- 版本兼容和保留字段一定要前置考虑，不然协议升级很痛苦。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q3: ⭐🟡 设备同时通过串口、TCP、HID 接入时，通信架构怎么统一？


A: 结论：抽象统一的 `IChannel`/`ITransport` 接口，把连接、发送、接收、状态回调标准化，上层只面向消息语义而非具体介质。


详细解释：


- 底层介质差异留在适配层处理。
- 上层协议层关注帧和命令，而不是 `QSerialPort`/`QTcpSocket`/HID API 区别。
- 这样后续切换设备或扩展新介质成本更低。


常见坑/追问：


- 别抽象过头，接口最少包含 open/close/send/receive/state 就够了。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q4: ⭐🟡 Qt 程序启动慢且首屏卡顿，你会怎么设计优化方案？


A: 结论：先埋点定位启动阶段，再把非关键初始化延后/异步化，首屏只加载必要资源，避免主线程阻塞。


详细解释：


- 首屏需要的数据优先。
- 大表格、大图片、数据库连接、日志扫描等可延后。
- 插件探测、主题加载、翻译资源也常是隐藏成本。


常见坑/追问：


- 优化不仅是“变快”，还要防止引入初始化顺序 bug。

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？




## 二、常见系统设计题

### Q5: 🟡 OTA 升级模块如何设计更稳？


A: 结论：要把下载、校验、断点续传、版本比较、升级执行、回滚和状态展示拆开，并把失败恢复当一等公民。


详细解释：


- 升级包必须校验签名/摘要。
- 设备端与上位机端都要有超时和重试策略。
- 状态机设计要清晰，避免卡在半升级态。


常见坑/追问：


- 追问常见：断电怎么办？答案一定要提回滚或双分区/恢复机制。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q6: 🟡 海量设备实时状态展示界面怎么设计不卡？


A: 结论：核心是“分层缓存 + 节流刷新 + 增量更新 + 虚拟化展示”，不要每条状态都直接驱动 UI 重绘。


详细解释：


- 采集线程和 UI 线程隔离。
- 汇总后按固定帧率刷新界面。
- 列表/表格要按可视区域渲染。


常见坑/追问：


- 典型错误是每来一条数据就 `setItem` 或 emit 一次重 UI 信号。

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q7: 🔴 如果让你设计一个插件化桌面应用，你会怎么保证 ABI 和可扩展性？


A: 结论：优先定义稳定 C 接口或纯抽象接口 + 工厂函数，插件边界避免暴露 STL/异常/模板细节，并做版本协商。


详细解释：


- 主程序与插件共享最小接口集。
- 加入接口版本号、能力查询、生命周期函数。
- 数据交换尽量用稳定 POD/序列化结构。


常见坑/追问：


- 追问：为什么不直接导出复杂 C++ 类？因为 ABI 风险太大。

> 💡 **面试追问**：模板编译期展开有什么代价？如何减少模板实例化导致的代码膨胀？



### Q8: 🔴 多线程采集 + 解析 + 存库 + UI 刷新系统怎么做背压？


A: 结论：应在每层设置有界队列和降级策略，区分哪些数据必须保留、哪些可采样/丢弃，并暴露监控指标。


详细解释：


- 采集层可做限速或丢弃旧数据。
- 存库层可批量写入。
- UI 层只关心最新状态，不必消费全部历史消息。


常见坑/追问：


- 没有背压的系统只是在把问题从 CPU 延后到内存。

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q9: ⭐🟡 设计一个上位机设备管理系统，如何处理设备热插拔？


A: 结论：监听系统设备事件（串口枚举变化、USB 插拔通知），触发扫描 → 注册/注销设备流程，通过状态机和信号通知 UI 层，并保证资源安全清理。


详细解释：


- Linux：使用 `udev` 事件或定时扫描 `/dev/ttyUSB*`，Qt 可用 `QFileSystemWatcher` 监控 `/dev`。
- Windows：处理 `WM_DEVICECHANGE` 消息，Qt 重写 `QWidget::nativeEvent` 接收。
- 插拔流程：检测到新设备 → 匹配 VID/PID 或端口名 → 尝试连接 → 注册到 DeviceManager → 通知 UI。
- 拔出流程：检测到移除 → 关闭连接、释放句柄 → 从 DeviceManager 注销 → UI 更新状态。


代码示例：


```cpp
// Qt 串口枚举变化检测（定时轮询简单方案）
connect(&m_scanTimer, &QTimer::timeout, this, [this]() {
    auto ports = QSerialPortInfo::availablePorts();
    // 对比上次列表，检测新增/移除
    detectChanges(ports);
});
m_scanTimer.start(1000);
```


常见坑/追问：


- 追问：资源争用问题——插入时立刻连接可能端口还没稳定，加短暂延迟再尝试连接。
- 追问：多个相同 VID/PID 设备如何区分？用 serial number 或 port path。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？




## 三、扩展与容灾

### Q10: ⭐🟡 如何设计一个支持断线自动重连的通信模块？


A: 结论：用状态机管理连接状态，断线后启动指数退避定时器重连，并向上层通知连接状态变化，保证重连期间的数据缓存和恢复策略。


详细解释：


- 连接状态：Disconnected → Connecting → Connected → Reconnecting。
- 重连策略：首次立即重试，之后指数退避（1s → 2s → 4s → ... 最大 30s）防止雪崩。
- 数据处理：重连期间上行命令缓存到队列，连接恢复后补发，或直接丢弃非关键指令。
- 告警通知：短暂断线可静默，长时间断线（如 30s）触发 UI 警告。


代码示例：


```cpp
void CommModule::onDisconnected() {
    m_state = State::Reconnecting;
    emit connectionChanged(false);
    int delay = std::min(m_retryInterval * 2, MAX_RETRY_INTERVAL_MS);
    m_retryInterval = delay;
    QTimer::singleShot(delay, this, &CommModule::tryConnect);
}
void CommModule::onConnected() {
    m_retryInterval = INITIAL_RETRY_INTERVAL_MS;
    m_state = State::Connected;
    emit connectionChanged(true);
    flushPendingQueue();
}
```


常见坑/追问：


- 追问：不加指数退避，服务器重启瞬间被大量客户端同时疯狂重连，造成"重连风暴"。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q11: ⭐🟡 设计一个上位机配置管理系统，需要考虑哪些方面？


A: 结论：需要考虑配置分层（系统/用户/设备）、格式选择、版本兼容、加密敏感项、运行时热加载和导入导出功能。


详细解释：


- 格式选择：JSON（可读性好，Qt 原生支持）、INI（简单键值）、XML（复杂结构）；推荐 JSON。
- 分层：系统默认 config（只读）、用户覆盖 config、设备个性配置；合并读取。
- 版本兼容：配置文件加 `version` 字段，加载时做迁移。
- 敏感项：密码、token 加密存储（AES + 本地密钥），不能明文放 JSON。
- 热加载：监控配置文件变化，动态重载某些参数（如日志级别）而不重启。


代码示例：


```cpp
class ConfigManager {
public:
    static ConfigManager& instance();
    void load(const QString& path);
    QVariant get(const QString& key, const QVariant& def = {}) const;
    void set(const QString& key, const QVariant& val);
    void save();
    Q_SIGNAL void configChanged(const QString& key);
private:
    QJsonObject m_cfg;
};
```


常见坑/追问：


- 追问：配置文件损坏或被用户手动改坏怎么办？加 schema 校验，加载失败回退到默认配置并备份坏文件。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q12: 🔴 设计一个实时曲线图控件，如何在高刷新率下保持 UI 流畅？


A: 结论：避免每次数据到来都触发全量重绘，用双缓冲/增量绘制、降采样显示、后台线程处理数据、主线程只做最终渲染来保持流畅。


详细解释：


- 数据与显示分离：采集线程写入环形缓冲，UI 定时（如 60ms）从缓冲取最新数据渲染一次。
- 降采样：若数据点远多于像素宽度，按像素列取 min/max 显示，既保留波形特征又减少绘制量。
- 自定义 Widget：重写 `paintEvent`，用 `QPainter` 绘制折线，比 `QChartView` 有更好的性能控制。
- 预分配：提前 `reserve` 点数组，避免动态扩容。


代码示例：


```cpp
void RealtimeChart::paintEvent(QPaintEvent*) {
    QPainter p(this);
    p.setRenderHint(QPainter::Antialiasing);
    const auto& pts = m_ringBuf.snapshot(); // 取当前帧快照
    if (pts.size() < 2) return;
    QPainterPath path;
    path.moveTo(toScreen(pts[0]));
    for (size_t i = 1; i < pts.size(); ++i)
        path.lineTo(toScreen(pts[i]));
    p.drawPath(path);
}
```


常见坑/追问：


- 追问：`QTimer` 间隔 16ms（60fps）刷新，若 paintEvent 本身超过 16ms 就会掉帧，需要 profile 找重绘瓶颈。
- 追问：为什么不直接用 QChartView？在高频数据（>1kHz）下性能不足，需要自绘。

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？




## 四、实战思路

### Q13: 🔴 设计一个多设备固件批量升级系统，如何保证可靠性和进度可见？


A: 结论：用任务队列 + 每设备独立状态机管理升级流程，前端显示实时进度，支持失败重试、跳过和中止，升级过程中保证设备状态可回滚。


详细解释：


- 任务模型：每台设备对应一个 `UpgradeTask`，包含状态机（待升级/传输中/校验中/刷写中/完成/失败）。
- 并发控制：不能所有设备同时升级（带宽/总线竞争），限制同时升级数量（如最多 4 台）。
- 进度汇报：每传完一帧发送进度信号，UI 订阅后更新进度条。
- 失败处理：超时/校验失败自动重试 N 次，超出后标记为失败允许人工干预。
- 结果汇总：全部完成后生成升级报告（设备 ID、升级前后版本、耗时、结果）。


代码示例：


```cpp
class BatchUpgradeManager : public QObject {
    Q_OBJECT
public:
    void start(const QList<DeviceInfo>& devices, const QString& firmwarePath);
signals:
    void deviceProgress(const QString& devId, int percent);
    void deviceDone(const QString& devId, bool success);
    void allDone(int success, int failed);
private:
    QSemaphore m_slots{4}; // 最多 4 台并发
};
```


常见坑/追问：


- 追问：升级中途断电怎么办？设备端需要有 bootloader 双区或 rollback 机制，上位机只能做到"下次检测版本后重新升级"。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q14: ⭐🔴 设计一个报警系统，如何避免报警风暴？


A: 结论：通过去重、分级抑制、报警合并和冷却时间机制，避免短时间内同类报警淹没操作员界面和日志。


详细解释：


- 去重：相同来源、相同类型的报警在恢复前只触发一次，不重复入队。
- 冷却（Dead Band）：状态恢复后，需要保持稳定一段时间才允许再次触发，防止边界值抖动引发反复报警。
- 合并（Rollup）：批量事件聚合为一条（如"5 台设备温度过高"而非 5 条独立报警）。
- 分级抑制：低优先级报警在高优先级事件期间可被暂时压制。
- 确认机制：操作员确认后报警从活跃列表移除，进入历史。


代码示例：


```cpp
class AlarmManager {
    struct AlarmKey { QString source; int code; };
    QMap<AlarmKey, QDateTime> m_active; // 去重表

    void raise(AlarmKey key, AlarmLevel level) {
        if (m_active.contains(key)) return; // 已报警，去重
        m_active[key] = QDateTime::currentDateTime();
        emit alarmTriggered(key, level);
    }
    void clear(AlarmKey key) {
        if (!m_active.contains(key)) return;
        // 冷却期后才真正清除
        QTimer::singleShot(COOLDOWN_MS, this, [this, key]() {
            m_active.remove(key);
            emit alarmCleared(key);
        });
    }
};
```


常见坑/追问：


- 追问：报警风暴的根因通常是传感器抖动或网络抖动，从源头加滤波（如均值滤波、滞后比较）比在报警层抑制更优雅。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q15: ⭐🔴 如何设计一个跨平台（Windows/Linux）的上位机软件自动更新机制？


A: 结论：分为"检测 → 下载 → 校验 → 安装 → 重启"五阶段，关键是安静下载不打断用户、强校验保证安装包完整、安装失败能回滚旧版本。


详细解释：


- 检测：启动时或定时请求版本服务接口，返回最新版本号 + 下载 URL + 哈希。
- 下载：后台线程下载到临时目录，支持断点续传（`Range` 头），进度通知 UI。
- 校验：下载完成后验证 SHA256，不通过则删除重下。
- 安装：Windows 下载 installer 或 zip 解压替换；Linux 下可替换 AppImage 或调用包管理器。
- 重启：提示用户保存工作，关闭主程序，启动安装程序/新版本，或用外部 launcher 完成替换。
- 回滚：安装前备份旧版本，新版本启动失败可还原。


代码示例：


```cpp
class AutoUpdater : public QObject {
    Q_OBJECT
public:
    void checkForUpdate();
signals:
    void updateAvailable(const QString& version, const QString& changelog);
    void downloadProgress(int percent);
    void readyToInstall();
private slots:
    void onVersionResponse(QNetworkReply* reply);
    void downloadUpdate(const QUrl& url);
    bool verifyHash(const QString& filePath, const QByteArray& expected);
};
```


常见坑/追问：


- 追问：Windows 下替换正在运行的 exe 会被锁定，通常用另一个 updater.exe 来完成替换。
- 追问：如何防止用假安装包攻击？服务端签名 + 客户端验签（非对称加密），不仅仅是哈希校验。

---

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？

---

## 📊 本章统计

| 指标 | 数量 |
|------|------|
| 总题目数 | 15 |
| 🟢 入门 | 1 |
| 🟡 进阶 | 8 |
| 🔴 高难 | 6 |
