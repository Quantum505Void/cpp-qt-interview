# 20. 模板与泛型编程


↑ 回到目录


### Q1: ⭐🟢 模板的本质是什么？


A: 结论：模板本质上是编译期代码生成与泛型抽象机制。它不是简单“类型占位符”，而是让编译器按类型/值实例化出具体代码。


详细解释：


- 函数模板、类模板是最常见形式。
- 模板让算法与类型解耦，例如 `std::sort` 可作用于多种迭代器。
- 代价是编译错误复杂、编译时间变长、二进制可能膨胀。


代码示例：


```cpp
template <typename T>
T add(T a, T b) { return a + b; }
```


常见坑/追问：


- 模板不是运行时多态，实例化发生在编译期。
- 追问：模板和宏区别？模板有类型系统、作用域、可调试性更强。


### Q2: ⭐🟡 模板实例化是什么时候发生的？


A: 结论：模板通常在编译期按需实例化：当你真正用到某个模板参数组合时，编译器才生成对应代码。


详细解释：


- 只声明不用，不一定实例化。
- 类模板成员函数也通常按需实例化。
- 这也是模板定义常放头文件的原因：编译单元需要看到完整定义才能实例化。


常见坑/追问：


- 把模板实现放 cpp 而不显式实例化，常导致链接错误。
- 追问：显式实例化能干嘛？可减少重复实例化，控制编译边界。


### Q3: ⭐🔴 函数模板重载、特化、普通函数优先级怎么理解？


A: 结论：编译器会先做重载决议，再考虑模板匹配和特化。一般普通函数优先于同样匹配的模板，特化是对某些模板参数的定制版本。


详细解释：


- 函数模板可以重载。
- 类模板支持偏特化，函数模板不支持偏特化。
- 函数模板的“看起来像偏特化”通常通过重载实现。


代码示例：


```cpp
void f(int);

template <typename T>
void f(T);
```


常见坑/追问：


- “函数模板也能偏特化”是高频错误答案。
- 追问：那函数模板想做类似偏特化怎么办？靠重载 + SFINAE/concepts。


### Q4: ⭐🔴 全特化和偏特化分别是什么？


A: 结论：全特化是把模板参数全部确定；偏特化是只对一部分模式进行特殊处理。类模板支持二者，函数模板只支持全特化，不支持偏特化。


详细解释：


- 全特化：`Template&lt;int, double&gt;` 这种完全写死。
- 偏特化：`Template&lt;T*&gt;`、`Template&lt;std::vector&lt;T&gt;&gt;` 这种针对模式。
- STL 大量使用偏特化和 traits 技术。


代码示例：


```cpp
template <typename T>
struct Traits { static constexpr bool is_ptr = false; };

template <typename T>
struct Traits<T*> { static constexpr bool is_ptr = true; };
```


常见坑/追问：


- 偏特化容易和重载混淆，尤其函数模板场景。
- 追问：为什么 traits 常用偏特化？因为它天生适合按类型模式分类。


### Q5: ⭐🔴 什么是 SFINAE？


A: 结论：SFINAE（Substitution Failure Is Not An Error）指模板参数替换失败时，不直接报错，而是把该模板候选从重载集中移除。这是 C++11~17 泛型约束的核心技巧之一。


详细解释：


- 常见工具：`std::enable_if`、`void_t`、检测惯用法（detection idiom）。
- 用途：根据类型特征启用/禁用某个模板重载。
- 它让“只有满足某条件的类型才能调用某函数”成为可能。


代码示例：


```cpp
template <typename T,
          typename = std::enable_if_t<std::is_integral_v<T>>>
void foo(T) {}
```


常见坑/追问：


- SFINAE 错误信息往往很长，维护成本不低。
- 追问：C++20 有什么更好的替代？concepts。


### Q6: ⭐🟡 type_traits 是什么？有什么用？


A: 结论：`&lt;type_traits&gt;` 提供编译期类型判断和变换工具，是模板元编程基础设施。没有它，很多泛型约束和优化都得手搓。


详细解释：


- 判断类：`is_same`、`is_integral`、`is_base_of`。
- 变换类：`remove_reference`、`decay`、`conditional`。
- 常与 `if constexpr`、SFINAE、concepts 搭配使用。


代码示例：


```cpp
static_assert(std::is_integral_v<int>);
using T = std::remove_reference_t<int&>;
```


常见坑/追问：


- `std::is_same&lt;T, U&gt;::value` 在 C++17 后通常可写成 `_v` 变量模板更简洁。
- 追问：`decay` 做了什么？大致类似函数传参时的类型退化。


### Q7: ⭐🟡 什么是变参模板（variadic templates）？


A: 结论：变参模板允许模板接收任意数量参数，是现代 C++ 实现通用打印、完美转发工厂、tuple 等能力的核心机制。


详细解释：


- 通过参数包 `typename... Ts`、`Ts... args` 表示。
- 常配合展开表达式（fold expressions）或递归展开。
- 它替代了 C 风格 `...` 可变参数的很多场景。


代码示例：


```cpp
template <typename... Args>
void log(Args&&... args) {
    (std::cout << ... << args) << '\n';
}
```


常见坑/追问：


- 参数包展开位置和语法很容易第一次写懵。
- 追问：C++17 对它的改进？fold expressions 让展开更优雅。


### Q8: ⭐🔴 什么是完美转发？它和模板有什么关系？


A: 结论：完美转发是指在模板中保留实参的值类别（左值/右值）并转发给下游函数，核心工具是转发引用 + `std::forward`。


详细解释：


- `T&amp;&amp;` 在模板推导场景下可能是 forwarding reference。
- 左值传入时 T 推导为 `U&amp;`，右值传入时 T 推导为 `U`。
- `std::forward&lt;T&gt;(arg)` 能保留原始值类别。
- 工厂函数、emplace 系列 heavily rely on it。


代码示例：


```cpp
template <typename T, typename... Args>
std::unique_ptr<T> make_obj(Args&&... args) {
    return std::make_unique<T>(std::forward<Args>(args)...);
}
```


常见坑/追问：


- `std::move` 和 `std::forward` 不能乱替换。
- 追问：什么情况下 `T&amp;&amp;` 不是转发引用？当 T 不是模板推导来的，比如类模板已确定类型时。


### Q9: ⭐🔴 concepts 是什么？为什么说它改善了模板可读性？


A: 结论：concepts 是 C++20 引入的模板约束机制，用来明确表达“这个模板参数必须满足什么能力”。它让错误信息和接口意图都比 SFINAE 更清晰。


详细解释：


- 可以用标准 concepts，如 `std::integral`、`std::ranges::range`。
- 也可自定义 concept。
- 它本质上仍是编译期约束，但语法更直接。


代码示例：


```cpp
#include <concepts>

template <std::integral T>
T gcd(T a, T b) {
    while (b != 0) {
        T t = a % b;
        a = b;
        b = t;
    }
    return a;
}
```


常见坑/追问：


- concepts 改善的是约束表达和诊断体验，不代表模板复杂度自动消失。
- 追问：它和 `static_assert` 区别？concept 是接口层约束，`static_assert` 更像内部断言。


### Q10: ⭐🔴 泛型编程最容易写成什么样的“高级灾难”？


A: 结论：最容易写成“抽象很炫、报错很长、没人敢改”的模板黑魔法。泛型的目标应是复用和约束清晰，而不是炫技。


详细解释：


- 先确认是否真有多类型复用需求。
- 优先简单模板 + traits + `if constexpr`。
- 必要时再上 SFINAE / concepts / 元编程。
- 过度模板化会拖慢编译、放大错误信息、增加维护成本。


常见坑/追问：


- 面试官如果问“你如何控制模板复杂度”，最好答：限制抽象层级、补静态测试、用 concepts 提升接口可读性。
- 追问：什么时候不用模板更好？当实现只有一种类型、变化不值得抽象时。
