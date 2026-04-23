# 31. 软件工程与设计原则

> 难度分布：🟢 入门 2 题 · 🟡 进阶 9 题 · 🔴 高难 4 题

[[toc]]

---

### Q1: ⭐🟢 什么是 SOLID？


A: 结论：SOLID 是五个面向对象设计原则：单一职责、开闭、里氏替换、接口隔离、依赖倒置，用来降低耦合、提升可维护性。


详细解释：


- 它不是教条，而是帮助判断“设计是否在朝着更易变更的方向走”。
- 面试时最好结合项目例子回答，而不是背名词。


常见坑/追问：


- 过度设计也会变成“为了 SOLID 而 SOLID”。


### Q2: ⭐🟢 单一职责原则在工程里怎么落地？


A: 结论：一个模块应只有一个主要变化原因。比如协议解析、数据库落盘、UI 展示不要搅在一个类里。


详细解释：


- 职责分离后更容易测试、复用和替换。
- 上位机项目很容易把“设备通信 + 状态机 + 界面刷新”写成巨类，这是典型反例。


常见坑/追问：


- 单一职责不是类越小越好，而是变化原因要清晰。


### Q3: ⭐🟡 开闭原则怎么理解才不空泛？


A: 结论：对扩展开放、对修改关闭，意思是新增行为尽量通过扩展而非频繁改稳定核心。


详细解释：


- 例如新增协议类型时，通过策略/注册表扩展，而不是在巨型 `switch` 里到处改。
- 插件化、命令模式、工厂模式都常服务于这个目标。


常见坑/追问：


- 不是“永远不能改旧代码”，而是尽量减少对稳定内核的扰动。


### Q4: ⭐🟡 依赖倒置原则为什么重要？


A: 结论：高层模块不应依赖底层细节，而应依赖抽象，这能降低替换成本和测试成本。


详细解释：


- 比如业务层依赖 `ILogger`，而不是直接绑死文件日志实现。
- 这样未来可替换为异步日志、网络日志、测试 mock。


常见坑/追问：


- 不是所有地方都要上接口，变化点明显的地方才值得抽象。


### Q5: 🟡 设计模式在实际项目中应该怎么用？


A: 结论：设计模式是经验工具箱，不是面试表演。应在确有变化点和复杂度时使用，而非预先堆满模式。


详细解释：


- Qt 里信号槽本身就带有观察者风格。
- 协议处理常见策略/工厂。
- 状态机适合设备流程控制。


常见坑/追问：


- 最怕“每个类都抽象一层”，代码还没复杂，架构先复杂了。


### Q6: 🟡 如何看待重构？


A: 结论：重构是“在不改变外部行为前提下改善内部结构”，它不是大手术，也不应脱离测试和业务节奏独立存在。


详细解释：


- 常见时机：重复逻辑过多、命名混乱、模块边界不清、修改成本持续升高。
- 小步重构 + 回归测试最稳。


常见坑/追问：


- 别把“顺手重写半个系统”叫重构，那通常叫冒险。


### Q7: 🔴 如何设计一个可维护的 Qt 大型桌面应用架构？


A: 结论：建议分成 UI 展示层、应用服务层、领域/业务层、基础设施层，并通过信号槽/事件总线/接口抽象做解耦。


详细解释：


- UI 层只关心展示与交互。
- 服务层编排用例、线程切换、状态同步。
- 基础设施层负责串口、网络、数据库、日志。
- 可结合 MVVM/MVP，但别生搬硬套。


常见坑/追问：


- 反模式是 MainWindow 什么都干，最终变成上帝类。


### Q8: 🔴 如何平衡“先做出来”和“长期可维护”？


A: 结论：先保证正确可交付，再在高频变化路径保留扩展点；不要一开始过度架构，也不要一直堆临时代码不还债。


详细解释：


- 用业务压力指导抽象深度。
- 对短生命周期需求可适度务实，对核心基础设施要更谨慎。


常见坑/追问：


- 面试里说出“我会在第二次重复时开始抽象，第一次先观测变化方向”会显得成熟。


### Q9: ⭐🟡 什么是依赖注入？在 C++/Qt 项目里怎么落地？


A: 结论：依赖注入是将类的依赖通过外部传入而非内部创建，核心是"不要自己 new 你依赖的东西"，从而降低耦合、提升可测试性。


详细解释：


- 三种注入方式：构造函数注入（最推荐）、setter 注入、接口注入。
- Qt 项目中，可以把 `ISerialPort*`、`IDatabase*` 等抽象接口通过构造函数传入，而不在类内部 `new` 具体实现。
- 这样测试时可传入 Mock 实现，实际运行传入真实实现。


代码示例：


```cpp
class DeviceManager {
public:
    // 注入接口而非具体实现
    explicit DeviceManager(ICommPort* port, IDatabase* db)
        : m_port(port), m_db(db) {}
private:
    ICommPort* m_port;
    IDatabase* m_db;
};

// 测试时
DeviceManager mgr(new MockPort(), new MockDatabase());
// 生产时
DeviceManager mgr(new SerialPort("/dev/ttyUSB0"), new SQLiteDatabase());
```


常见坑/追问：


- 追问：DI 和 Service Locator 的区别？DI 是显式传入，Service Locator 是隐式查找，前者更易追踪依赖关系。


### Q10: ⭐🟡 什么是观察者模式？和 Qt 信号槽有什么关系？


A: 结论：观察者模式让多个对象订阅某个主题的变化，主题状态改变时自动通知所有订阅者；Qt 的信号槽本质上是观察者模式的语言级实现，更安全、更解耦。


详细解释：


- 传统观察者：Subject 维护 Observer 列表，手动管理注册/注销，易内存泄漏。
- Qt 信号槽：自动管理生命周期（对象销毁自动断开连接），支持跨线程（QueuedConnection），类型安全。
- 信号槽可以 1:N（一个信号连多个槽）、N:1（多个信号连同一个槽）。


代码示例：


```cpp
// 经典观察者
class IObserver { public: virtual void update(int val) = 0; };
class Subject {
    std::vector<IObserver*> obs;
public:
    void notify(int val) { for (auto* o : obs) o->update(val); }
};

// Qt 方式
connect(device, &Device::dataArrived, ui, &MainWindow::updateChart);
// 线程安全投递
connect(worker, &Worker::result, this, &MainWindow::onResult, Qt::QueuedConnection);
```


常见坑/追问：


- 追问：Qt 信号槽的性能比直接函数调用慢多少？大约 5-10 倍，但大多数场景可接受，热路径才需要考虑直接回调。


### Q11: ⭐🟡 如何理解"面向接口编程"而不是"面向实现编程"？


A: 结论：代码依赖抽象（接口/纯虚类）而非具体类，使得实现可以自由替换（通信方式、存储后端、算法策略），这是开闭原则和依赖倒置的核心体现。


详细解释：


- 定义 `ICommPort` 接口，串口/TCP/HID 各自实现；上层业务只知道 `ICommPort`，不关心底层。
- 同理，`ILogger`、`IAlarmHandler`、`IConfig` 都可以有多个实现。
- 好处：单元测试容易（Mock 替换）、新需求只需新增实现（不改旧代码）。


代码示例：


```cpp
class ICommPort {
public:
    virtual ~ICommPort() = default;
    virtual bool open() = 0;
    virtual QByteArray read(int maxBytes) = 0;
    virtual bool write(const QByteArray& data) = 0;
};

class SerialPort : public ICommPort { /* ... */ };
class TcpPort   : public ICommPort { /* ... */ };
```


常见坑/追问：


- 追问：接口太细粒度会导致接口爆炸，SOLID 的 ISP 原则提醒我们接口要内聚。


### Q12: 🟡 什么是状态机？在上位机项目里为什么重要？


A: 结论：状态机用明确的状态集合和迁移条件描述系统行为，避免布满 if-else 的"状态乱跳"，上位机通信、OTA 升级、设备控制流程都是状态机的天然应用场景。


详细解释：


- 核心要素：状态（State）、事件（Event）、迁移（Transition）、动作（Action）。
- 枚举 + switch 是最简单实现，但规模大时不易维护。
- 表驱动状态机：用二维表 `transitions[state][event] = {next_state, action}` 集中管理所有迁移。
- 可用 Qt 的 `QStateMachine`（基于状态图，适合复杂嵌套状态）。


代码示例：


```cpp
enum class OtaState { Idle, Downloading, Verifying, Flashing, Done, Error };
enum class OtaEvent { StartDownload, DownloadDone, VerifyOk, VerifyFail, FlashDone };

// 简单状态机
void OtaStateMachine::handleEvent(OtaEvent ev) {
    switch (m_state) {
    case OtaState::Idle:
        if (ev == OtaEvent::StartDownload) { m_state = OtaState::Downloading; startDownload(); }
        break;
    case OtaState::Downloading:
        if (ev == OtaEvent::DownloadDone) { m_state = OtaState::Verifying; verify(); }
        break;
    // ...
    }
}
```


常见坑/追问：


- 最常见问题：不用状态机，用一堆 bool flag 手动拼状态，状态组合爆炸难维护。
- 追问：如何处理状态机的并发触发？需要加事件队列，避免在状态迁移处理中途收到新事件。


### Q13: 🟡 什么是命令模式？在 Qt 桌面应用里有哪些实际用途？


A: 结论：命令模式把操作封装成对象，支持参数化、队列化、撤销/重做和日志记录，Qt 应用中常用于实现 Undo/Redo 和批量操作。


详细解释：


- `QUndoCommand` 是 Qt 内置命令模式实现，支持 `undo()`/`redo()` 接口和 `QUndoStack` 管理。
- 除了 Undo/Redo，命令模式还可用于：操作日志（把命令序列化保存）、远程控制（命令序列化发送）、宏命令（批量执行）。


代码示例：


```cpp
class RenameDeviceCmd : public QUndoCommand {
public:
    RenameDeviceCmd(Device* d, const QString& newName)
        : m_dev(d), m_newName(newName), m_oldName(d->name()) {}
    void redo() override { m_dev->setName(m_newName); }
    void undo() override { m_dev->setName(m_oldName); }
private:
    Device* m_dev;
    QString m_newName, m_oldName;
};

// 使用
undoStack->push(new RenameDeviceCmd(dev, "新设备名"));
```


常见坑/追问：


- 追问：命令模式和函数指针/std::function 的区别？命令对象携带状态、支持撤销，function 只是可调用对象。


### Q14: ⭐🔴 代码评审（Code Review）的核心价值是什么？评审时你关注哪些维度？


A: 结论：代码评审不只是找 bug，更重要的是知识传播、统一规范、提前暴露设计问题，以及防止技术债沉积。


详细解释：


- **正确性**：逻辑对不对，边界情况有没有处理。
- **可读性**：命名、注释、函数长度，能否让新人理解。
- **安全性**：缓冲区越界、资源泄漏、线程安全。
- **性能**：热路径是否有不必要的锁/复制/分配。
- **设计**：职责是否清晰，是否引入了不必要的耦合。
- **测试覆盖**：新功能是否有对应测试。


常见坑/追问：


- 追问：你在评审中发现过哪些有价值的问题？准备一个真实案例，比"我会看逻辑"更有说服力。
- 评审不是批判，措辞要客观具体：说"这里 delete 后未置 nullptr，析构时可能 double free"好过"这里有 bug"。


### Q15: ⭐🔴 如何理解技术债？什么时候还债是合适的？


A: 结论：技术债是为了短期交付故意选择了不够优良的方案，后续需要额外工作来修复；关键是有意识地管理，而不是让它无声积累。


详细解释：


- 有意技术债：有意识地做了折中，记录在案，计划偿还（如临时用 sqlite 硬存，后续换时序数据库）。
- 无意技术债：不知道有更好做法，后来才发现；通过学习和 review 减少。
- 还债时机：新功能开发前、性能瓶颈明显时、维护成本超过业务收益时。
- 量化债：用"每次新功能开发要多花多少时间"来说服管理者排期还债。


常见坑/追问：


- 追问：如果 PM 不给时间还债怎么办？把技术债成本折算成需求延迟风险，用业务语言沟通；同时在日常迭代里持续"小还"，不等大重构。
- 追问：童子军规则是什么？"离开营地时比进入时更干净"——每次改动顺手改善一点周边代码。

---

## 📊 本章统计

| 指标 | 数量 |
|------|------|
| 总题目数 | 15 |
| 🟢 入门 | 2 |
| 🟡 进阶 | 9 |
| 🔴 高难 | 4 |
