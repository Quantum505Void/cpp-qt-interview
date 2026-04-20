# 7. 并发与并行


↑ 回到目录


graph TD
    A[多线程共享数据] --> B{数据竞争?}
    B -->|只读| C[无需同步]
    B -->|读写| D{操作是否原子?}
    D -->|是| E[std::atomic]
    D -->|否| F{竞争激烈?}
    F -->|否| G[std::mutex]
    F -->|是| H[读写锁 shared_mutex]

### Q1: ⭐🟢 并发和并行的区别是什么？


A: 结论：并发是多个任务在同一时间段交替推进，并行是多个任务在同一时刻真正同时运行。并发强调结构组织，并行强调硬件同时执行。


详细解释：


- 单核 CPU 也可以并发，但不是真并行。
- 多核 CPU 才能让多个线程物理同时运行。
- 面试里回答时，最好顺带说“并发不一定更快，但能提升响应性和资源利用率”。


常见坑/追问：


- 别把二者混成“多线程就是并行”。


### Q2: ⭐🟢 线程和进程的区别怎么答最稳？


A: 结论：进程是资源分配单位，线程是 CPU 调度单位。进程隔离强、通信重；线程共享地址空间、通信快，但同步更复杂。


详细解释：


- 进程有独立虚拟地址空间。
- 同进程线程共享代码段、堆、全局变量等资源。
- 崩一个线程通常会带崩整个进程。


常见坑/追问：


- 线程共享地址空间不等于天然线程安全。


### Q3: ⭐🟡 什么是数据竞争（data race）？


A: 结论：多个线程同时访问同一内存位置，至少一个访问是写，且没有同步保护，这就是数据竞争。数据竞争属于未定义行为，不是“结果偶尔不对”那么简单。


详细解释：


- 有 data race 时，编译器和 CPU 都可能自由重排。
- 最危险之处在于 bug 可能极难复现。
- 解决方式通常是锁、原子操作或线程间隔离状态。


常见坑/追问：


- “加了 volatile 就安全”是错误答案。


### Q4: ⭐🟡 mutex、lock_guard、unique_lock 有什么区别？


A: 结论：`mutex` 是锁本体，`lock_guard` 是最轻量 RAII 封装，`unique_lock` 更灵活，可延迟加锁、手动解锁、配合条件变量使用。简单场景优先 `lock_guard`，需要灵活控制时用 `unique_lock`。


详细解释：


- `lock_guard` 开销小、语义单纯。
- `unique_lock` 支持 `defer_lock`、`try_lock`、`unlock`。
- 条件变量的 `wait` 需要能解锁再加锁，因此通常搭配 `unique_lock`。


代码示例：


```cpp
std::mutex m;
std::unique_lock<std::mutex> lk(m);
```


常见坑/追问：


- 忘记 RAII，手动 `lock()`/`unlock()` 最容易在异常路径翻车。


### Q5: ⭐🟡 死锁的四个必要条件是什么？怎么避免？


A: 结论：死锁四条件是互斥、请求并保持、不可剥夺、循环等待。要避免死锁，核心就是主动打破其中至少一个条件，工程上最常用的是统一加锁顺序和缩小临界区。


详细解释：


- 多把锁交叉获取是典型根源。
- 用 `std::scoped_lock` 同时锁多把互斥量可减少死锁风险。
- 把耗时操作放到锁外执行也很重要。


代码示例：


```cpp
std::mutex a, b;
void f() {
    std::scoped_lock lock(a, b);
}
```


常见坑/追问：


- 死锁不是只有“两把锁反着拿”这一种，回调重入也常导致隐式死锁。


### Q6: ⭐🟡 条件变量为什么一定要配谓词？什么是虚假唤醒？


A: 结论：条件变量等待必须配合谓词，因为线程被唤醒不代表条件一定成立，可能是虚假唤醒，也可能是别的线程先消费了条件。正确写法永远是“醒来后重新检查条件”。


详细解释：


- `wait` 可能无原因返回。
- 被 `notify_all` 唤醒的多个线程之间也会竞争。
- 谓词版 `wait` 是最稳妥写法。


代码示例：


```cpp
cv.wait(lock, [] { return ready; });
```


常见坑/追问：


- 用 `if` 包裹等待而不是 `while/谓词` 是经典并发 bug。


### Q7: ⭐🟡 shared_mutex / 读写锁适合什么场景？553849536


A: 结论：`shared_mutex` 适合“读多写少”的共享数据场景，允许多个读者并发访问，但写者必须独占。它能提升读密集场景吞吐，但也会引入更复杂的饥饿与升级问题。


详细解释：


- 读操作用共享锁。
- 写操作用独占锁。
- 配置中心、缓存、字典表等场景较常见。


代码示例：


```cpp
std::shared_mutex sm;
{
    std::shared_lock lock(sm); // 读
}
{
    std::unique_lock lock(sm); // 写
}
```


常见坑/追问：


- 不要在读锁下试图“升级”为写锁，很多实现不支持安全升级。


### Q8: ⭐🟡 call_once 和线程安全单例怎么讲？


A: 结论：`std::call_once` 用于保证某段初始化逻辑在多线程环境下只执行一次，非常适合一次性全局初始化。线程安全单例在现代 C++ 中通常直接用函数内静态变量即可。


详细解释：553849536


- `call_once` 搭配 `once_flag` 使用。
- C++11 起函数内静态局部变量初始化是线程安全的。
- 单例设计是否合理，和线程安全是两个层次的问题。


代码示例：


```cpp
std::once_flag flag;
void init() {
    std::call_once(flag, [] { /* only once */ });
}

class Singleton {
public:
    static Singleton& instance() {
        static Singleton s;
        return s;
    }
};
```


常见坑/追问：


- 线程安全不等于测试友好，单例仍有全局状态污染问题。


### Q9: ⭐🟡 std::async 和 std::thread 有什么区别？


A: 结论：`std::thread` 表示“明确创建一个线程执行任务”，`std::async` 表示“提交一个异步任务并拿 future 取结果”，它可能创建线程，也可能延迟执行。前者偏线程控制，后者偏异步结果模型。


详细解释：


- `thread` 需要你自己 `join/detach`。
- `async` 返回 `future`，更自然承载返回值与异常。
- `async` 的调度策略受 launch policy 影响。


代码示例：


```cpp
auto fut = std::async(std::launch::async, [] { return 42; });
int x = fut.get();
```


常见坑/追问：


- 不指定启动策略时，`async` 可能不是立即并发执行。


### Q10: 🟡 原子操作能完全替代锁吗？


A: 结论：不能。原子操作适合简单共享状态，如计数器、标志位；一旦涉及多个变量的一致性、不变量维护或复杂临界区，锁通常更合适。无锁不等于更快，也不等于更高级。


详细解释：


- 原子只保证单个原子对象操作语义。
- 多变量事务性仍需要更高层同步。
- 可维护性也是并发设计成本的一部分。


常见坑/追问：


- 很多“自以为无锁优化”的代码，其实只是把 bug 变高级了。


### Q11: ⭐🟡 线程安全和可重入有什么区别？


A: 结论：线程安全表示多个线程同时调用时结果仍正确；可重入表示函数执行过程中被再次进入也仍安全。可重入通常比线程安全要求更强。


详细解释：


- 可重入函数通常不依赖共享可变状态。
- 带锁函数可以线程安全，但不一定可重入。
- 信号处理函数经常要求可重入。


常见坑/追问：


- 不要把“加锁了”就等同于“可重入”。


### Q12: 🟡 CPU 密集型和 IO 密集型任务在线程策略上有什么区别？


A: 结论：CPU 密集型任务线程数通常接近 CPU 核心数；IO 密集型任务因为大量时间在等待，可以开更多并发任务。线程数不是越多越好，而是要匹配瓶颈类型。


详细解释：


- CPU 密集：过多线程只会增加上下文切换。
- IO 密集：等待期间 CPU 可调度其他任务。
- 实际工程还要结合队列长度、延迟目标、系统负载监控。


常见坑/追问：


- 面试官常追问：为什么上下文切换昂贵？记得提寄存器保存恢复、cache 失效。


### Q13: ⭐🟡 std::future 和 std::promise 怎么配合使用？


A: 结论：`std::promise` 由生产者持有，用于设置值；`std::future` 由消费者持有，用于获取值。二者通过共享状态关联，是跨线程传递单次结果的标准方式。


详细解释：


- 调用 `promise.set_value()` 后，`future.get()` 将返回该值；若设置了异常，`get()` 会重新抛出。
- `future.get()` 会阻塞直到结果可用，只能调用一次。
- `std::packaged_task` 封装可调用对象，自动绑定 promise/future 对。
- `std::async` 是更高层的封装，直接返回 future。


代码示例（如有）：


```cpp
#include <future>
#include <thread>

std::promise<int> prom;
std::future<int> fut = prom.get_future();

std::thread t([&prom] {
    // 在另一个线程里设置结果
    prom.set_value(42);
});

int result = fut.get(); // 阻塞等待，result == 42
t.join();
```


常见坑/追问：


- `future.get()` 只能调 1 次，多次调用抛异常；需要多消费者用 `shared_future`。
- 忘记调用 `set_value` 或 `set_exception`，future 析构时会抛 `broken_promise`。


### Q14: ⭐🟡 std::mutex 的几种锁封装有什么区别（lock_guard vs unique_lock vs scoped_lock）？


A: 结论：`lock_guard` 最轻量，构造加锁析构解锁，不可转移；`unique_lock` 功能最丰富，支持延迟锁、定时锁、手动解锁，可与 `condition_variable` 配合；`scoped_lock`（C++17）支持同时锁多个 mutex，自动按顺序锁定避免死锁。


详细解释：


- `lock_guard`：RAII 最简封装，性能极好，适合不需要解锁弹性的场景。
- `unique_lock`：开销略大，但灵活；条件变量的 `wait()` 要求传 `unique_lock`。
- `scoped_lock`：C++17，接受可变参数 mutex 列表，用 `std::lock` 算法避免死锁，推荐替换双锁场景。


代码示例（如有）：


```cpp
std::mutex m1, m2;

// scoped_lock 同时锁两个 mutex，不会死锁
{
    std::scoped_lock lock(m1, m2);
    // critical section
}

// unique_lock 配合条件变量
std::unique_lock<std::mutex> ul(m1);
cv.wait(ul, [] { return ready; });
```


常见坑/追问：


- 锁的粒度越细，并发越高，但越难推理正确性；粒度太粗，并发度下降。
- 不要在持有锁时调用未知代码（回调/槽函数），容易死锁。


### Q15: 🟡 什么是内存序（memory order）？C++ 中有哪几种？


A: 结论：内存序控制原子操作的可见性和指令重排范围。C++ 提供 6 种：`relaxed`、`acquire`、`release`、`acq_rel`、`consume`（不推荐）、`seq_cst`（最强，默认）。选错内存序会导致细微的并发 bug，选太强则损失性能。


详细解释：


- `seq_cst`：所有线程看到一致的全局操作顺序，最安全，开销最大。
- `acquire`（读）/ `release`（写）：配对使用，保证发布端的写在获取端可见，适合 producer-consumer 同步。
- `relaxed`：只保证原子性，不保证顺序，适合纯计数器（如统计指标）。
- x86 上 TSO 模型让大多数场景 relaxed ≈ seq_cst，但 ARM/RISC-V 差异很大。


代码示例（如有）：


```cpp
std::atomic<bool> ready{false};
std::atomic<int> data{0};

// 生产者
data.store(42, std::memory_order_relaxed);
ready.store(true, std::memory_order_release);  // release：保证 data 的写先于 ready

// 消费者
while (!ready.load(std::memory_order_acquire)); // acquire：看到 ready 后 data 可见
int val = data.load(std::memory_order_relaxed); // val == 42
```


常见坑/追问：


- 面试能说出 acquire/release 配对语义就足够，不需要死记全部规则。
- 不要在不了解 memory model 的情况下随意降低内存序"优化性能"。
