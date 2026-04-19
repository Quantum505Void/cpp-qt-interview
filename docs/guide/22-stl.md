# 22. STL 深入


↑ 回到目录


### Q1: ⭐🟢 vector 为什么通常是默认首选容器？


A: 结论：因为 `vector` 连续内存、缓存友好、随机访问快，综合性能在多数业务场景最好。


详细解释：


- CPU 喜欢连续内存，cache line 命中率更高。
- 遍历、排序、批量处理都很强。
- 现代 CPU 下，缓存友好往往比“理论上 O(1)/O(logN)”更影响真实性能。


代码示例：


```cpp
std::vector<int> v;
v.reserve(1000);
for (int i = 0; i < 1000; ++i) v.push_back(i);
```


常见坑/追问：


- `vector` 中间插入删除不便宜。
- 面试加分点：能主动提“缓存友好”而不只背复杂度。


### Q2: ⭐🟢 map、unordered_map、flat_map 思路上怎么选？


A: 结论：有序需求选 `map`，极致查找吞吐常考虑 `unordered_map`，小规模且读多写少时连续存储的 flat 结构也常很强。


详细解释：


- `map` 是红黑树，稳定有序、迭代器稳定。
- `unordered_map` 基于哈希，平均查找快，但有哈希退化和 rehash 成本。
- 小数据量时，排序数组 + 二分查找经常比想象中更快。


常见坑/追问：


- 不能机械地说 `unordered_map` 一定更快。
- 追问：什么时候 `map` 更合适？需要顺序遍历、范围查询、稳定迭代器时。


### Q3: ⭐🟡 string 的 SSO 是什么？


A: 结论：SSO（Small String Optimization）是小字符串直接存储在对象内部，避免堆分配，提升短字符串性能。


详细解释：


- 很多实现会把十几字节以内字符串放在 `std::string` 对象内部。
- 常见于日志 tag、文件扩展名、短协议字段。
- 这样减少分配、拷贝和 cache miss。


代码示例：


```cpp
std::string a = "ok";      // 可能走 SSO
std::string b = "this is a much longer string"; // 可能堆分配
```


常见坑/追问：


- SSO 属于实现细节，不同标准库实现大小不同。
- 追问：`std::move` 一个 SSO 字符串一定便宜吗？未必，短字符串移动和拷贝成本可能接近。


### Q4: ⭐🟡 迭代器失效是 STL 面试高频，怎么系统回答？


A: 结论：核心是看容器底层存储是否重分配/重链接。连续容器常因扩容失效，链式容器通常局部稳定但被删元素本身失效。


详细解释：


- `vector` 扩容会导致所有迭代器、指针、引用失效。
- `deque` 规则更复杂，头尾插入相对稳定但不是绝对万能。
- `list`/`map`/`set` 一般插入不使已有迭代器失效，删除只影响被删元素。


代码示例：


```cpp
std::vector<int> v{1,2,3};
auto it = v.begin();
v.push_back(4); // 若触发扩容，it 可能失效
```


常见坑/追问：


- 不要背成死表，面试官更想看你是否理解底层结构。


### Q5: 🟡 为什么 emplace_back 不总是比 push_back 更快？


A: 结论：`emplace_back` 只有在“原地构造避免临时对象”时才有优势；如果本来就已有对象，和 `push_back(std::move(x))` 差别可能很小。


详细解释：


- `emplace_back(args...)` 直接在容器尾部构造。
- 但错误使用也可能让重载选择更复杂，可读性变差。
- 对简单类型几乎没差别。


代码示例：


```cpp
std::vector<std::string> v;
v.emplace_back(10, 'a');
std::string s = "hello";
v.push_back(std::move(s));
```


常见坑/追问：


- 不要把 `emplace` 神化成“永远更快”。


### Q6: 🟡 allocator 的存在意义是什么？


A: 结论：allocator 把“对象逻辑”和“内存分配策略”解耦，适合定制内存池、共享内存、追踪分配等高级场景。


详细解释：


- STL 容器默认用标准分配器。
- 高性能场景可以通过 allocator 降低碎片、减少锁竞争。
- 面试里知道其定位比手写 allocator 更重要。


常见坑/追问：


- allocator 不是只为“更快”，也可以为可观测性和特殊内存区域服务。


### Q7: 🔴 erase-remove 惯用法为什么经典？


A: 结论：`std::remove` 不真正删除元素，而是把“保留元素”搬到前面，再由容器的 `erase` 真正缩容。


详细解释：


- 算法层与容器层职责分离，是 STL 设计思想体现。
- C++20 有 `std::erase/std::erase_if`，写法更简洁。
- 这个问题常被用来区分“会背 API”和“理解 STL 模型”。


代码示例：


```cpp
std::vector<int> v{1,2,3,2,4};
v.erase(std::remove(v.begin(), v.end(), 2), v.end());
```


常见坑/追问：


- `remove` 后容器 size 没变，别以为元素已经没了。


### Q8: 🔴 为什么说复杂度不是 STL 选型的全部？


A: 结论：真实性能还受缓存命中、分支预测、内存分配、数据规模、访问模式影响，单看 Big-O 很容易误判。


详细解释：


- 小数据量下，`vector + sort + binary_search` 常赢过树结构。
- 指针追逐会带来 cache miss。
- 哈希表也会受冲突、rehash、装载因子影响。


常见坑/追问：


- 面试高级一点时，主动说“先压测，不迷信理论复杂度”会加分。
