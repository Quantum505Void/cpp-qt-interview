# 6. Qt 核心机制

> 难度分布：🟢 入门 2 题 · 🟡 进阶 13 题 · 🔴 高难 0 题

[[toc]]

---

### Q1: ⭐🟢 Qt 的信号槽机制本质上解决了什么问题？


A: 结论：信号槽解决的是对象之间低耦合通信问题，特别适合 GUI 事件驱动、模块解耦和跨线程通知。发送者不关心谁接收，也不关心接收者怎么处理。


详细解释：


- 支持一对一、一对多连接。
- 支持直接调用和排队调用。
- 把“发生了什么”和“怎么响应”拆开。


代码示例：


```cpp
connect(button, &QPushButton::clicked,
        this, &MainWindow::onClicked);
```


常见坑/追问：


- 信号槽不是简单回调语法糖，它背后依赖元对象系统和连接类型。


### Q2: ⭐🟡 新连接语法为什么优于旧字符串语法？


A: 结论：新语法类型安全、编译期可检查、重构友好，基本应该默认使用。旧字符串语法更多是历史兼容产物。


详细解释：


- 新语法使用函数指针或 lambda。
- 编译器能检查参数签名。
- IDE 重命名时也更可靠。


代码示例：


```cpp
connect(sender, &Sender::valueChanged,
        receiver, &Receiver::onValueChanged);
```


常见坑/追问：


- 重载信号/槽时要配合 `QOverload` 或显式类型转换。


### Q3: 🟢 emit 是关键字吗？


A: 结论：不是，`emit` 本质上只是一个空宏，主要用于增强代码可读性，让人一眼看出这里在发信号。它没有额外语义魔法。


详细解释：


- 写不写 `emit` 对编译结果通常无本质区别。
- 但从团队风格看，保留 `emit` 更清晰。


常见坑/追问：


- 不要把 `emit` 理解成“特别的语法结构”。


### Q4: ⭐🟡 MOC 是什么？Qt 为什么需要它？


A: 结论：MOC 是 Qt 的元对象编译器，用来扫描带 `Q_OBJECT` 的类并生成额外 C++ 代码，从而支持信号槽、反射、动态属性等能力。因为标准 C++ 长期没有完整反射，所以 Qt 需要这套机制补位。


详细解释：


- MOC 会生成元对象描述和调用分发代码。
- 构建系统必须正确处理 MOC 步骤。
- 这也是 Qt 框架与纯标准库开发的重要区别之一。


常见坑/追问：


- 漏写 `Q_OBJECT` 或构建脚本没跑 MOC，都会导致奇怪错误。


### Q5: ⭐🟡 Qt 事件循环是怎么工作的？


A: 结论：程序进入 `exec()` 后，事件循环不断从队列中取事件并分发给目标对象，这构成了 Qt 应用的运行心跳。UI 响应、定时器、网络回调、跨线程 queued signal 都建立在它之上。


详细解释：


- 事件来源包括用户输入、系统消息、定时器、socket、posted event。
- 事件循环保证主线程 GUI 程序持续响应。
- 没有事件循环，很多 Qt 异步机制都不会正常工作。


常见坑/追问：


- 阻塞主线程会让事件循环卡住，表现就是界面假死。


### Q6: ⭐🟡 sendEvent 和 postEvent 的区别是什么？


A: 结论：`sendEvent` 是同步立即发送，当前线程直接处理；`postEvent` 是异步投递到事件队列，等事件循环调度。一般业务代码更常用 `postEvent` 这种事件驱动方式。


详细解释：


- `sendEvent` 更直接，但调用栈耦合更强。
- `postEvent` 更符合异步系统设计。
- queued signal 本质上也接近“封装成事件再投递”。


代码示例：


```cpp
QCoreApplication::postEvent(obj, new QEvent(QEvent::User));
```


常见坑/追问：


- `postEvent` 依赖接收线程有事件循环。


### Q7: ⭐🟡 QVariant 的设计哲学是什么？


A: 结论：`QVariant` 的设计目标是提供一个统一、可反射、可在 Qt 元对象系统中流转的动态值容器。它不是为了替代静态类型，而是为了在“框架边界”和“通用接口”处提升灵活性。


详细解释：


- 常用于 model/view、属性系统、动态配置、信号槽通用参数。
- 它强调与 Qt 类型系统协同，而不只是“能装任何东西”。
- 在 Qt6 中它仍然是框架胶水层的重要角色。


代码示例：


```cpp
QVariant v = 42;
int x = v.toInt();
```


常见坑/追问：


- 不要在性能关键、类型明确的核心逻辑里滥用 `QVariant`。


### Q8: ⭐🟡 什么是 Qt 的隐式共享（COW）？


A: 结论：隐式共享是 Qt 很多值类型采用的 copy-on-write 机制：拷贝时先共享底层数据，只有写入时才真正分离。它提高了值语义使用体验，但也要求理解“读共享、写分离”的成本模型。


详细解释：


- 常见于 `QString`、`QByteArray`、`QImage` 等类型。
- 拷贝通常很便宜，修改时可能触发 detach。
- 这让 API 可以按值传递而不一定成本高昂。


代码示例：


```cpp
QString a = "hello";
QString b = a;  // 先共享
b[0] = 'H';     // 写时分离
```


常见坑/追问：


- 不要以为“拷贝永远零成本”，写操作仍可能发生真实复制。


### Q9: ⭐🟡 QSharedPointer 和 std::shared_ptr 怎么比较？


A: 结论：两者都是共享所有权智能指针，但 `QSharedPointer` 与 Qt 生态、对象删除策略、部分工具链整合更自然，而 `std::shared_ptr` 是标准方案、通用性更强。新项目如果不依赖特定 Qt 语义，通常优先标准库版本。


详细解释：


- `QSharedPointer` 在老 Qt 代码中较常见。
- `std::shared_ptr` 更利于跨库、跨框架统一。
- 二者不要混着接管同一个裸指针。


常见坑/追问：


- `QObject` 有 parent 时，再拿共享指针接管生命周期要极度小心。


### Q10: ⭐🟡 为什么 GUI 只能在主线程操作？


A: 结论：因为大多数 GUI 框架都要求界面对象在其所属线程访问，Qt Widgets 通常要求在主线程操作 UI。后台线程应该负责计算或 I/O，再通过信号槽或事件回到主线程更新界面。


详细解释：


- GUI 库往往依赖单线程消息泵模型。
- 跨线程直接改 UI 容易造成竞态和不可预测行为。
- Qt 用 queued connection 提供了线程间安全通知路径。


常见坑/追问：


- “偶尔能跑”不代表线程安全，很多 UI 跨线程问题是概率性炸弹。


### Q11: ⭐🟡 moveToThread 和继承 QThread 怎么选？


A: 结论：业务对象通常推荐 `QObject + moveToThread` 的 worker 模式，只有在线程对象本身需要定制执行逻辑时才考虑继承 `QThread`。因为 `QThread` 更像线程控制器，而不是业务工作对象本体。


详细解释：


- Worker 模式利于槽函数在目标线程执行。
- 继承 `QThread` 容易把“线程管理”和“业务逻辑”耦在一起。
- 官方长期更推荐 worker 方案。


代码示例：


```cpp
Worker* worker = new Worker;
QThread* thread = new QThread;
worker->moveToThread(thread);
connect(thread, &QThread::started, worker, &Worker::doWork);
thread->start();
```


常见坑/追问：


- `moveToThread` 改的是对象归属线程，不是“让当前代码瞬移过去”。


### Q12: ⭐🟡 QTimer 的精度和使用边界是什么？


A: 结论：`QTimer` 适合常规 UI 定时、轮询和超时控制，但它不是高精度实时定时器。其精度受操作系统调度、事件循环阻塞和定时器类型影响。


详细解释：


- 事件循环忙时，超时触发会延后。
- `Qt::PreciseTimer` 能提高精度，但不是硬实时保证。
- 非常高精度场景通常要考虑系统级定时设施或专用方案。


代码示例：


```cpp
QTimer* timer = new QTimer(this);
connect(timer, &QTimer::timeout, this, &MainWindow::onTimeout);
timer->start(1000);
```


常见坑/追问：


- 在槽里执行耗时任务会导致下一次 timeout 漂移。


### Q13: 🟡 Q_INVOKABLE 是干什么的？


A: 结论：`Q_INVOKABLE` 用来把普通成员函数暴露到 Qt 元对象系统，使其可以被反射调用，也更容易被 QML 等框架侧访问。它本质上是在说：这个函数值得被 Qt 运行时看见。


详细解释：


- 可与 `QMetaObject::invokeMethod` 配合使用。
- 常用于 QML 暴露接口、动态调用。
- 与槽函数不同，它不表示一定参与信号槽语义。


代码示例：


```cpp
class Api : public QObject {
    Q_OBJECT
public:
    Q_INVOKABLE int add(int a, int b) { return a + b; }
};
```


常见坑/追问：


- `Q_INVOKABLE` 不是性能优化标记，是元对象可见性标记。


### Q14: ⭐🟡 QProcess 有什么用？使用时要注意什么？


A: 结论：`QProcess` 用于在 Qt 程序中启动外部进程、收集输出、控制生命周期，是桌面工具和工程辅助程序里非常常见的能力。它比直接 `system()` 更可控，也更适合事件驱动模型。


详细解释：


- 可异步读取标准输出/错误。
- 可等待启动、等待结束，也可纯异步。
- 常用于调用脚本、外部命令、设备工具链。


代码示例：


```cpp
QProcess p;
p.start("ls", {"-l"});
p.waitForFinished();
qDebug() << p.readAllStandardOutput();
```


常见坑/追问：


- 不要忽略命令注入风险。
- 大输出场景下，如果不及时读取管道，子进程可能阻塞。


### Q15: ⭐🟡 Qt 的属性系统（Q_PROPERTY）是什么？有什么用？


A: 结论：`Q_PROPERTY` 宏在 Qt 元对象系统中注册属性，使属性可以被 QML 绑定、被 `QObject::property()` 反射读写、被属性动画（`QPropertyAnimation`）驱动、被序列化工具自动枚举。它是 Qt 数据绑定和动态访问的核心机制。


详细解释：


- 属性需要声明 `READ`/`WRITE` 函数，可选 `NOTIFY` 信号（QML 绑定必须有 NOTIFY）。
- `QPropertyAnimation` 通过属性名字符串驱动，不需要直接持有对象方法指针。
- `QObject::property("name")` 和 `setProperty("name", val)` 支持运行期动态访问。
- C++20 风格的 `Q_PROPERTY` 在 Qt 6 中也可与绑定引擎（`QBindable`）配合，实现响应式数据流。


代码示例（如有）：


```cpp
class Circle : public QObject {
    Q_OBJECT
    Q_PROPERTY(double radius READ radius WRITE setRadius NOTIFY radiusChanged)
public:
    explicit Circle(QObject* parent = nullptr) : QObject(parent), radius_(1.0) {}

    double radius() const { return radius_; }
    void setRadius(double r) {
        if (qFuzzyCompare(r, radius_)) return;
        radius_ = r;
        emit radiusChanged(r);
    }

signals:
    void radiusChanged(double newRadius);

private:
    double radius_;
};

// 使用：属性动画
auto* anim = new QPropertyAnimation(circle, "radius");
anim->setStartValue(1.0);
anim->setEndValue(100.0);
anim->setDuration(2000);
anim->start();

// 反射访问
circle->setProperty("radius", 50.0);
qDebug() << circle->property("radius").toDouble();
```


常见坑/追问：


- `NOTIFY` 信号里传新值是惯例但不是强制；QML 绑定依赖 NOTIFY 信号来刷新。
- 属性类型必须是 `QMetaType` 已知的类型，自定义类型需要 `Q_DECLARE_METATYPE` + `qRegisterMetaType`。
- 追问：`Q_PROPERTY` 和直接公开成员变量的区别？属性提供封装、变更通知、元对象系统集成，公开成员变量都没有。

---

## 📊 本章统计

| 指标 | 数量 |
|------|------|
| 总题目数 | 15 |
| 🟢 入门 | 2 |
| 🟡 进阶 | 13 |
| 🔴 高难 | 0 |
