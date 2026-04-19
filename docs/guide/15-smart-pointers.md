# 15. 智能指针深入


↑ 回到目录


### Q1: ⭐🟢 unique_ptr、shared_ptr、weak_ptr 分别适合什么场景？


A: 结论：`unique_ptr` 表示独占所有权，默认首选；`shared_ptr` 表示共享所有权；`weak_ptr` 用来观察 `shared_ptr` 管理对象，解决循环引用和悬空访问判断。


详细解释：


- `unique_ptr` 零额外引用计数开销，语义清晰。
- `shared_ptr` 适合多个对象共同持有同一资源。
- `weak_ptr` 不增加引用计数，需 `lock()` 后使用。
- 面试标准答法：能独占就别共享，能不用堆就别上智能指针。


代码示例：


```cpp
auto p1 = std::make_unique<int>(42);
auto p2 = std::make_shared<int>(42);
std::weak_ptr<int> wp = p2;
```


常见坑/追问：


- 不要把 `shared_ptr` 当“默认安全指针”。
- 追问：为什么 `weak_ptr` 不能直接解引用？因为对象可能已被释放。


### Q2: ⭐🟡 为什么推荐 make_unique / make_shared？


A: 结论：因为它们更安全、更简洁，能减少重复写 `new`，并在异常场景下更稳。`make_shared` 还通常只做一次内存分配。


详细解释：


- `make_unique&lt;T&gt;(args...)` 避免手写 `new T(...)`。
- `make_shared&lt;T&gt;(args...)` 往往把对象和控制块放在同一块内存中。
- 性能和异常安全通常优于分开 `new`。


代码示例：


```cpp
auto p = std::make_shared<MyClass>(1, 2, 3);
```


常见坑/追问：


- 如果需要自定义 deleter 或和 C API 资源深度结合，未必总能直接 `make_*`。
- 追问：`make_shared` 的潜在代价？对象和控制块同分配，若还有 `weak_ptr` 残留，整块内存释放时机可能更晚。


### Q3: ⭐🟡 shared_ptr 的引用计数是怎么工作的？


A: 结论：`shared_ptr` 内部有控制块，记录强引用计数和弱引用计数。强计数归零时析构对象，弱计数归零时释放控制块。


详细解释：


- 控制块通常包含：引用计数、deleter、allocator 等信息。
- 多个 `shared_ptr` 拷贝共享同一控制块。
- `weak_ptr` 只影响弱计数，不延长对象生命周期。
- 引用计数的增减通常是原子操作，存在一定性能成本。


常见坑/追问：


- `shared_ptr` 线程安全不等于“对象本身线程安全”。
- 追问：为什么高频路径滥用 `shared_ptr` 会慢？因为原子计数和控制块管理有开销。


### Q4: ⭐🔴 循环引用为什么会发生？怎么解决？


A: 结论：两个或多个对象彼此用 `shared_ptr` 持有，会导致强引用计数永不归零，造成内存泄漏。解决办法是把至少一端改成 `weak_ptr`。


详细解释：


- 经典例子：父子节点、观察者、双向链表。
- 谁拥有谁要设计清楚，不要所有边都共享所有权。
- `weak_ptr` 表示“我知道你，但不拥有你”。


代码示例：


```cpp
struct B;
struct A { std::shared_ptr<B> b; };
struct B { std::weak_ptr<A> a; };
```


常见坑/追问：


- 看到泄漏别只怪 `shared_ptr`，根因通常是所有权建模错了。
- 追问：Qt 的 `QObject` 对象树和 `shared_ptr` 混用要小心什么？可能出现双重管理和析构顺序问题。


### Q5: ⭐🟡 unique_ptr 可以放进 STL 容器吗？


A: 结论：可以。`unique_ptr` 支持移动不支持拷贝，所以放容器时要用 move/emplace。这是现代 C++ 很常见的资源管理方式。


详细解释：


- `std::vector&lt;std::unique_ptr&lt;T&gt;&gt;` 非常常见。
- 扩容时元素通过 move 转移。
- 容器销毁时会自动销毁其中的 `unique_ptr`。


代码示例：


```cpp
std::vector<std::unique_ptr<int>> v;
v.push_back(std::make_unique<int>(1));
v.emplace_back(std::make_unique<int>(2));
```


常见坑/追问：


- 不要写 `v.push_back(p);`，除非 `std::move(p)`。
- 追问：为什么 `initializer_list` 初始化 `vector&lt;unique_ptr&lt;T&gt;&gt;` 不方便？因为 `initializer_list` 元素是 const，不支持移动。


### Q6: 🟡 智能指针怎么管理 C 风格资源？


A: 结论：可以通过自定义 deleter 管理 `FILE*`、socket、`malloc` 内存、OpenSSL 对象等非 `new` 资源。关键是“释放方式要匹配申请方式”。


详细解释：


- `unique_ptr&lt;T, Deleter&gt;` 很适合独占 C 资源。
- `shared_ptr` 也支持自定义 deleter，但如果无需共享，一般优先 `unique_ptr`。
- 这是 C++ 封装 RAII 的常见方式。


代码示例：


```cpp
using FilePtr = std::unique_ptr<FILE, decltype(&fclose)>;
FilePtr fp(fopen("a.txt", "r"), &fclose);
```


常见坑/追问：


- socket 在 Linux 上用 `close`，Windows 上是 `closesocket`，别混。
- 追问：为什么不用裸指针 + finally 风格？因为 C++ 没原生 finally，RAII 更稳。


### Q7: ⭐🟡 什么是 enable_shared_from_this？


A: 结论：它让对象内部安全地拿到指向自己的 `shared_ptr`。如果一个对象已经被 `shared_ptr` 管理，不能再用 `shared_ptr(this)` 重新构造控制块，否则会双重释放。


详细解释：


- 继承 `std::enable_shared_from_this&lt;T&gt;` 后，可调用 `shared_from_this()`。
- 它依赖对象已经被某个 `shared_ptr` 托管。
- 常用于异步回调中延长自身生命周期。


代码示例：


```cpp
struct Session : std::enable_shared_from_this<Session> {
    void start() {
        auto self = shared_from_this();
        // 在异步任务中捕获 self
    }
};
```


常见坑/追问：


- 在构造函数里调用 `shared_from_this()` 是未定义/异常行为，因为控制块可能还没建立。
- 追问：`weak_from_this()` 是什么？C++17 起提供，拿 `weak_ptr` 更安全。


### Q8: ⭐🔴 shared_ptr 的线程安全边界是什么？


A: 结论：不同 `shared_ptr` 实例对同一控制块做引用计数增减通常是线程安全的，但被管理对象本身的读写不自动线程安全。


详细解释：


- 线程 A 拷贝 `shared_ptr`，线程 B 销毁 `shared_ptr`，引用计数层面通常没问题。
- 但若多个线程同时调用对象成员函数，仍需要锁或无锁同步。
- 不能因为用了 `shared_ptr` 就以为数据竞争消失。


常见坑/追问：


- `use_count()` 不是并发逻辑判断的可靠依据。
- 追问：原子化 `shared_ptr` 怎么做？C++20 有 `std::atomic&lt;std::shared_ptr&lt;T&gt;&gt;` 支持。


### Q9: 🟡 Qt 里为什么很多时候不建议用智能指针管理 QObject？


A: 结论：因为 `QObject` 已经有 parent-child 对象树管理生命周期，再叠加智能指针容易形成双重所有权、析构顺序冲突。Qt 对象通常遵循 Qt 自己的生命周期模型。


详细解释：


- 有 parent 的 QObject 往往由父对象析构时统一释放。
- 若再塞进 `shared_ptr`/`unique_ptr`，很容易二次 delete。
- 但对无 parent、非 QObject 资源封装对象，智能指针仍然很好用。


常见坑/追问：


- `QObject::deleteLater()` 和 `shared_ptr` deleter 混用更要谨慎。
- 追问：那 Qt 场景下完全不能用智能指针吗？不是，关键看是否与对象树冲突。


### Q10: ⭐🔴 智能指针最大的面试陷阱是什么？


A: 结论：最大的陷阱不是 API 记不住，而是所有权模型说不清。面试官真正想听的是：谁创建、谁拥有、谁释放、是否共享、是否跨线程、是否循环引用。


详细解释：


- 先建模所有权，再选指针。
- 如果对象天然唯一拥有，用 `unique_ptr`。
- 如果多个组件共同持有且生命周期交织，才考虑 `shared_ptr`。
- 如果只是引用观察，不拥有，就用裸指针/引用/`weak_ptr`，视场景而定。


常见坑/追问：


- “统一全用 `shared_ptr` 最安全”是非常典型的错误回答。
- 追问：什么时候裸指针仍然合理？当它只表达非拥有关系时。
