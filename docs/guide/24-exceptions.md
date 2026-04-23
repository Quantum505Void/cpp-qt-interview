# 24. 异常处理与异常安全

> 难度分布：🟢 入门 2 题 · 🟡 进阶 9 题 · 🔴 高难 4 题

[[toc]]

---


## 一、异常基础

### Q1: ⭐🟢 C++ 异常机制的价值是什么？


A: 结论：异常适合表达“正常路径之外的错误传播”，能把错误处理从业务主流程中抽离出来，但要控制边界和成本。


详细解释：


- 它尤其适合构造失败、资源获取失败、不可恢复错误。
- 与返回码相比，异常避免层层手工传递错误。
- 但在高频热路径、底层组件边界要谨慎使用。


常见坑/追问：


- 不要把异常当普通分支控制流。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q2: ⭐🟢 什么是异常安全的三个级别？


A: 结论：通常分为基本保证、强保证、不抛异常保证。面试答这题要讲“失败后对象状态还能否维持有效”。


详细解释：


- 基本保证：出错后对象仍有效，但值可能变化。
- 强保证：操作失败就像没发生过一样。
- 不抛异常保证：承诺不会抛异常。


常见坑/追问：


- `noexcept` 与“不抛异常保证”相关，但它是语言层承诺，违背会直接终止。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q3: ⭐🟡 RAII 为什么是异常安全的核心？


A: 结论：RAII 把资源释放绑定到对象析构，从而保证异常传播时也能自动回收资源。


详细解释：


- 栈展开过程中，局部对象会逆序析构。
- 因此锁、文件、内存、事务句柄都应尽量封装为对象。
- 现代 C++ 里，RAII 比“catch 里补救释放”可靠得多。


代码示例：


```cpp
std::lock_guard<std::mutex> lock(m);
// 发生异常也会自动解锁
```


常见坑/追问：


- 析构函数里再抛异常会很危险，尤其栈展开期间会直接 `terminate`。

> 💡 **面试追问**：与 GC 相比 RAII 的优势是什么？异常抛出时 RAII 为何仍然可靠？



### Q4: ⭐🟡 析构函数为什么通常必须 noexcept？


A: 结论：因为析构常发生在异常传播期间，如果析构再抛异常，程序会直接终止。


详细解释：


- 标准库大量依赖析构不抛异常这个前提。
- 资源释放动作若可能失败，通常应记录日志、设置状态、提供显式 `close()` 接口处理。


常见坑/追问：


- “析构里吞异常”不一定优雅，但通常比二次抛出安全。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q5: 🟡 什么时候不建议用异常？


A: 结论：在极致低延迟、异常被禁用、跨语言 ABI 边界、内核/驱动风格接口中，通常更偏向返回码或错误对象。


详细解释：


- 异常的成本不只在运行时，还包括可读性、二进制、工具链策略。
- 很多团队会规定模块边界用 `expected`/error code，内部可用异常。


常见坑/追问：


- 关键不是“异常好/坏”，而是边界风格统一。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？




## 二、异常安全

### Q6: 🟡 如何实现强异常安全保证？


A: 结论：经典方法是 copy-and-swap、先构造临时结果再提交、把失败点放在状态变更之前。


详细解释：


- 先在临时对象中完成所有可能失败的操作。
- 成功后再一次性 swap/commit。
- 数据库事务、配置热更新、容器扩容都能类比这个思路。


代码示例：


```cpp
MyType tmp(new_state);
swap(tmp);
```


常见坑/追问：


- 追求强保证可能带来额外拷贝或内存成本，要看业务是否值得。

> 💡 **面试追问**：内存泄漏如何定位？Valgrind 和 AddressSanitizer 各自适合什么场景？



### Q7: 🔴 noexcept 对标准容器优化有什么影响？


A: 结论：若类型的移动构造是 `noexcept`，如 `vector` 扩容时更愿意走移动而非拷贝，从而降低成本并维持异常安全。


详细解释：


- 容器要在“高效”和“出错后可回滚”之间平衡。
- 如果 move 可能抛异常，容器可能选择拷贝，因为更容易满足强保证。


常见坑/追问：


- 很多人只知道“最好加 noexcept”，但说不清为什么，这题就是拿来区分深度的。

> 💡 **面试追问**：vector 扩容时迭代器为何失效？如何用 `reserve` 优化？`std::deque` 和 `vector` 底层有何不同？



### Q8: 🔴 异常跨线程、跨模块、跨动态库传递要注意什么？


A: 结论：要极度谨慎。跨线程不能直接抛过去，跨 ABI/动态库边界若编译器/运行库不一致也可能出大问题。


详细解释：


- 线程边界通常要捕获异常并转成 `future`、状态码或日志。
- 动态库边界若 ABI 不兼容，异常对象布局、类型识别都可能异常。
- 工程上常要求“模块边界不外抛异常”。


常见坑/追问：


- 这题经常和 ABI、插件系统、C API 封装联动提问。

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？


### Q9: ⭐🟡 `noexcept` 说明符和 `noexcept` 运算符有什么区别？


A: 结论：`noexcept` 说明符用于声明函数不抛异常，是承诺；`noexcept(expr)` 运算符在编译期检测表达式是否不抛异常，返回 `bool`，是查询工具。


详细解释：


- `noexcept` 说明符：`void f() noexcept;` — 承诺 f 不抛异常，违反则 `std::terminate`。
- `noexcept(expr)` 运算符：`noexcept(std::move(x))` — 查询表达式是否不抛，编译期常量，不执行表达式。
- 两者常配合使用：`T(T&& other) noexcept(noexcept(/* member move ops */))` — 条件 noexcept。
- 析构函数默认 noexcept，显式抛异常需要 `noexcept(false)` 声明（但强烈不推荐）。


代码示例：


```cpp
#include <type_traits>

template<typename T>
class Wrapper {
    T val;
public:
    Wrapper(Wrapper&& other) noexcept(std::is_nothrow_move_constructible_v<T>)
        : val(std::move(other.val)) {}
};

// noexcept 运算符查询
static_assert(noexcept(std::declval<int>() + 1)); // true
```


常见坑/追问：


- 违反 `noexcept` 承诺时调用 `std::terminate`，不走 catch。
- 追问：为什么 `std::vector` 扩容要检查 `is_nothrow_move_constructible`？为了满足强异常安全保证。

> 💡 **面试追问**：vector 扩容时迭代器为何失效？如何用 `reserve` 优化？`std::deque` 和 `vector` 底层有何不同？



### Q10: ⭐🟡 如何在构造函数中正确处理异常？


A: 结论：构造函数抛异常时析构函数不会被调用，但已构造完成的成员会被析构；因此应该用 RAII 成员管理资源，避免裸 new，可用 function-try-block 捕获成员初始化异常。


详细解释：


- 构造到一半的对象：已完成的基类和成员会按逆序析构，但对象本身析构函数不调用。
- 裸 new 成员的危险：`A() : p1(new int), p2(new int){}` — p2 抛出时 p1 泄漏（无析构调用）。
- 解决方案：用 `unique_ptr` 成员或 RAII 包装，无论如何都能正确析构。
- `function-try-block`：在成员初始化列表抛出的异常可用此捕获，但必须重新抛出。


代码示例：


```cpp
// 危险做法：裸指针成员
class Bad {
    int* p1; int* p2;
public:
    Bad() : p1(new int(1)), p2(new int(2)) {} // p2 抛出，p1 泄漏
    ~Bad() { delete p1; delete p2; }
};

// 正确做法：RAII 成员
class Good {
    std::unique_ptr<int> p1;
    std::unique_ptr<int> p2;
public:
    Good() : p1(std::make_unique<int>(1)), p2(std::make_unique<int>(2)) {}
    // 任何一步失败，已构造的 unique_ptr 自动释放
};
```


常见坑/追问：


- `function-try-block` 捕获成员初始化异常后必须重新抛出（或让异常继续传播），不能在构造失败后继续使用半构造对象。
- 追问：为什么析构函数不能抛异常？因为 stack unwinding 期间如果析构再抛，会调用 `std::terminate`。

> 💡 **面试追问**：与 GC 相比 RAII 的优势是什么？异常抛出时 RAII 为何仍然可靠？




## 三、最佳实践

### Q11: 🟡 `std::exception_ptr` 是什么？有什么用途？


A: 结论：`std::exception_ptr` 是可以跨线程传递和存储的异常句柄，用于将一个线程捕获的异常"搬运"到另一个线程重新抛出。


详细解释：


- 通过 `std::current_exception()` 在 catch 块中捕获当前异常。
- 通过 `std::rethrow_exception(eptr)` 在另一处重新抛出。
- `std::promise`/`std::future` 内部正是用此机制传递异常。
- 延迟异常处理、错误聚合等场景也很有用。


代码示例：


```cpp
#include <future>
#include <exception>
#include <stdexcept>
#include <iostream>

std::exception_ptr gep;

void worker() {
    try {
        throw std::runtime_error("worker error");
    } catch (...) {
        gep = std::current_exception();
    }
}

int main() {
    std::thread t(worker);
    t.join();
    if (gep) {
        try {
            std::rethrow_exception(gep);
        } catch (const std::exception& e) {
            std::cerr << "Caught: " << e.what() << '\n';
        }
    }
}
```


常见坑/追问：


- `exception_ptr` 是引用计数的，持有它会延长异常对象的生命周期。
- 追问：`std::future::get()` 抛出的异常就是通过 `exception_ptr` 从 worker 线程转移过来的。

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？



### Q12: ⭐🔴 异常处理的性能代价在哪里？为什么嵌入式/游戏引擎常禁用异常？


A: 结论：现代 C++ 异常走"零代价异常"（DWARF/zero-cost EH），无异常路径无运行时开销；但有二进制体积增大、帧展开信息（unwind table）开销，以及抛出时的高延迟（微秒级）。


详细解释：


- 零代价异常（Zero-cost EH）：正常执行路径没有额外指令，代价转移到异常发生时的展开（unwinding）。
- 展开成本：抛出异常时需要遍历 unwind table、调用所有析构函数，延迟不可预测（通常微秒到毫秒）。
- 二进制膨胀：每个函数需要 unwind 信息，增加可执行文件体积（嵌入式 flash 受限）。
- 确定性问题：实时系统/游戏引擎需要帧内确定时间，异常展开时间不可预测。
- `-fno-exceptions` 后，std 库的 throwing 函数（如 `std::vector::at()`）退化为 `std::terminate`。


常见坑/追问：


- "零代价"指的是 happy path，异常 path 代价依然高，不适合用作流程控制。
- 追问：禁用异常后如何处理错误？通常用返回码、`std::optional`、`std::expected`（C++23）或 outcome 库。

> 💡 **面试追问**：vector 扩容时迭代器为何失效？如何用 `reserve` 优化？`std::deque` 和 `vector` 底层有何不同？



### Q13: 🟡 `std::terminate` 什么时候会被调用？


A: 结论：多种情况会触发 `std::terminate`：未捕获异常逃出 `main`、`noexcept` 函数中抛出、析构函数中抛出、`std::rethrow_exception` 空指针等。


详细解释：


- 未捕获异常：从 `main` 或线程函数传出的未捕获异常。
- `noexcept` 违反：承诺不抛却抛了，直接 terminate，不走 unwind。
- 析构函数抛出：stack unwinding 期间析构函数抛出，导致双重异常，terminate。
- 纯虚函数调用：在构造/析构期间调用纯虚函数。
- `std::thread` 未 join/detach 析构。
- 可自定义：`std::set_terminate()` 设置自定义 terminate handler（常用于记录最后日志）。


代码示例：


```cpp
#include <exception>
#include <iostream>

void myTerminate() {
    std::cerr << "Custom terminate called!\n";
    // 记录日志、生成 core dump...
    std::abort();
}

int main() {
    std::set_terminate(myTerminate);
    throw std::runtime_error("unhandled"); // 触发 myTerminate
}
```


常见坑/追问：


- terminate handler 里不能抛异常，必须以 `abort()`/`exit()` 终止。
- 追问：`std::unexpected`（C++03 dynamic exception spec）在 C++17 已删除。

> 💡 **面试追问**：虚函数表是什么时候创建的？多继承时 vptr 有几个？



### Q14: 🟡 什么是异常安全的 commit-or-rollback 模式？


A: 结论：先在临时副本上执行有风险的操作，成功后再用 `noexcept` 操作（如 swap）提交，失败则自动放弃副本，确保原对象不变（强保证）。


详细解释：


- 也叫 copy-and-swap 惯用法，是实现强异常安全的经典手段。
- 步骤：1. 构造临时副本 → 2. 对副本做修改（可能抛） → 3. `noexcept swap` 提交。
- 同时解决了自赋值安全问题。
- swap 之后旧副本析构（释放旧资源），无泄漏。


代码示例：


```cpp
class Buffer {
    std::unique_ptr<char[]> data;
    size_t size;
public:
    // copy-and-swap 实现拷贝赋值（强保证）
    Buffer& operator=(Buffer other) noexcept { // 值传递 = 拷贝
        std::swap(data, other.data);
        std::swap(size, other.size);
        return *this; // other 析构释放旧资源
    }
    // 不需要自赋值检查，自赋值时 other 是副本，swap 后析构副本，安全
};
```


常见坑/追问：


- 值传递参数触发拷贝，若拷贝构造抛异常，`this` 未被修改，满足强保证。
- 追问：这个模式的缺点是总要拷贝，即使自赋值；高性能场景可能需要单独优化自赋值路径。

> 💡 **面试追问**：这个知识点在实际项目中怎么用？有没有遇到过相关 bug 或性能问题？



### Q15: ⭐🔴 Qt 中如何处理异常与事件循环的兼容性问题？


A: 结论：Qt 事件循环不设计为异常安全，异常从事件处理器逃出行为未定义；应在 Qt 槽/事件函数边界彻底捕获异常，不允许其传播到事件循环。


详细解释：


- `QCoreApplication::exec()` 内部循环不捕获异常，异常从槽函数传出可能导致崩溃或未定义行为。
- Qt 官方立场：异常不应该跨越 Qt API 边界。
- 常见策略：在每个槽函数顶层 try-catch，记录日志/弹出错误对话框，不让异常传播。
- 可以通过继承 `QCoreApplication` 并重写 `notify()` 方法，在全局捕获所有事件处理中的异常。


代码示例：


```cpp
class SafeApplication : public QApplication {
public:
    using QApplication::QApplication;
    bool notify(QObject* receiver, QEvent* event) override {
        try {
            return QApplication::notify(receiver, event);
        } catch (const std::exception& e) {
            qCritical() << "Exception in event handler:" << e.what();
            // 可以显示错误对话框或安全关闭
            return false;
        }
    }
};

int main(int argc, char* argv[]) {
    SafeApplication app(argc, argv);
    // ...
    return app.exec();
}
```


常见坑/追问：


- 重写 `notify()` 是全局兜底，但不替代在业务代码里妥善处理异常。
- 追问：Qt 的 `QEXCEPTION_INITIAL_SIZE` 和 `QException`/`QUnhandledException` 是 Qt 5 提供的跨线程异常工具（配合 `QtConcurrent` 使用）。

---

> 💡 **面试追问**：线程池的核心参数如何调优？线程数设多少合适？

---

## 📊 本章统计

| 指标 | 数量 |
|------|------|
| 总题目数 | 15 |
| 🟢 入门 | 2 |
| 🟡 进阶 | 9 |
| 🔴 高难 | 4 |
