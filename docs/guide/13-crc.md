# 13. CRC 校验

> 难度分布：🟢 入门 1 题 · 🟡 进阶 10 题 · 🔴 高难 4 题

[[toc]]

---

### Q1: ⭐🟢 CRC 是什么？它解决什么问题？


A: 结论：CRC（Cyclic Redundancy Check）是一种基于多项式运算的差错检测码，主要用于检测传输或存储过程中的随机错误，不提供加密能力。


详细解释：


- 它常用于串口、网络帧、文件格式、存储块校验。
- CRC 擅长发现突发错误（burst error）。
- 它只能检测错误，通常不能纠正错误。
- 和 Hash 不同，CRC 更偏工程通信校验，计算快但抗恶意篡改能力弱。


代码示例：


```cpp
uint16_t crc = crc16_modbus(data, len);
```


常见坑/追问：


- CRC 不是安全机制，攻击者能伪造。
- 追问：为什么通信协议里还在大量使用 CRC？因为快、简单、硬件支持多。


### Q2: ⭐🟡 CRC 和校验和（checksum）有什么区别？


A: 结论：CRC 检错能力通常强于简单加和 checksum，尤其对突发错误更敏感；checksum 实现更简单，但漏检概率通常更高。


详细解释：


- checksum 常见是字节求和、反码和。
- CRC 基于 GF(2) 多项式除法，本质更适合检测位级错误模式。
- 网络协议里会根据复杂度和历史兼容性二选一或并用。


常见坑/追问：


- 不要说 checksum 一定没用，比如 IP 头校验历史上就采用 checksum。
- 追问：为什么很多工业协议宁可选 CRC16/CRC32？因为实现成熟、误检率低、成本可接受。


### Q3: ⭐🟡 CRC8、CRC16、CRC32 的区别是什么？


A: 结论：主要区别是校验位宽、生成多项式、检错能力和开销。位数越大，理论上误检率越低，但计算和报文开销也更高。


详细解释：


- CRC8 常见于一些轻量总线或设备寄存器通信。
- CRC16 常见于 Modbus、串口协议。
- CRC32 常见于以太网、ZIP、文件格式。
- 不能只看位数，还要看具体参数：poly、init、xorout、refin、refout。


常见坑/追问：


- “CRC16 都一样”是错的，不同协议参数可能完全不同。
- 追问：CRC32 一定比 CRC16 好吗？检错更强，但对短帧和低带宽场景未必必要。


### Q4: ⭐🔴 CRC 参数为什么容易算错？


A: 结论：因为 CRC 不只是一条 polynomial，还包含 init、xorout、refin、refout、bit order 等参数。哪怕多项式相同，参数不同结果也可能完全不同。


详细解释：


- poly：生成多项式。
- init：初始值。
- refin/refout：输入输出是否反射。
- xorout：最终异或值。
- 有些文档还会把 normal/reversed 表示法混在一起。


代码示例：


```cpp
struct CRCParam {
    uint32_t poly;
    uint32_t init;
    uint32_t xorout;
    bool refin;
    bool refout;
};
```


常见坑/追问：


- 面试官常给你一个“算出来不对”的案例，本质通常是参数表没对齐。
- 追问：怎么验证自己实现对不对？用标准测试串 `123456789` 对比公开结果。


### Q5: ⭐🟡 为什么很多 CRC 实现会用查表法（table-driven）？


A: 结论：查表法用空间换时间，避免逐 bit 迭代，能显著提升吞吐。通信和文件处理里很常见。


详细解释：


- bitwise 实现简单、易理解，但速度较慢。
- table-driven 预先计算 256 个字节可能对应的 CRC 变化。
- 还可以进一步做 slicing-by-4 / slicing-by-8 优化。


代码示例：


```cpp
uint32_t crc = 0xFFFFFFFF;
for (uint8_t b : data) {
    crc = (crc >> 8) ^ table[(crc ^ b) & 0xFF];
}
```


常见坑/追问：


- 查表法 table 必须和参数模型一致，否则看似“很快地算错”。
- 追问：嵌入式 ROM 很小怎么办？可能退回 bitwise 或小表实现。


### Q6: 🟡 Modbus CRC16 有什么特点？


A: 结论：Modbus RTU 常用 CRC16，poly 通常对应 0xA001（反射表示），结果低字节在前、高字节在后。它是工业面试高频点。


详细解释：


- Modbus RTU 帧尾两字节是 CRC。
- 计算范围通常是地址到数据区，不含 CRC 自身。
- 字节序发送顺序常被问：先发低字节，再发高字节。


代码示例：


```cpp
uint16_t crc16_modbus(const uint8_t* data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc & 1) ? (crc >> 1) ^ 0xA001 : (crc >> 1);
        }
    }
    return crc;
}
```


常见坑/追问：


- 别把 0x8005 和 0xA001 机械地当成两个不同算法，它们可能只是 normal/reversed 表示差异。
- 追问：为什么串口抓包里 CRC 字节顺序看起来反着？因为 Modbus 规定低字节先发。


### Q7: 🟡 CRC 能检测哪些错误？不能检测什么？


A: 结论：CRC 对单比特错误、多数短突发错误检测效果很好，但它不是零误检，也不能防止恶意构造的碰撞。


详细解释：


- 对单 bit 错误几乎都能检测。
- 对长度不超过 degree 的 burst error 检测能力通常较强。
- 但两个不同报文仍可能产生同一 CRC，概率虽低但不为零。
- 对恶意攻击应使用 MAC/签名，而不是 CRC。


常见坑/追问：


- “CRC 通过 = 数据绝对没错”是错误说法。
- 追问：既然可能碰撞，为什么还用？因为在随机噪声模型下性价比极高。


### Q8: ⭐🟡 通信协议里 CRC 的校验范围应该怎么设计？


A: 结论：CRC 范围通常覆盖从帧头关键字段到 payload 的所有需要保护内容，但一般不包含起始分隔符和 CRC 字段本身。核心是协议文档要讲清楚且双方一致。


详细解释：


- 有些协议不校验帧头 sync 字节，因为它只用来找边界。
- 有些协议把长度字段也纳入 CRC，以防长度被篡改导致拆包错乱。
- 若有多层封装，需明确每层各自校验边界。


常见坑/追问：


- 最怕“发送端和接收端各自觉得自己没问题”，其实是校验区间不一致。
- 追问：如何快速定位范围问题？抓一帧已知数据，逐字段增减验证。


### Q9: 🟡 软件实现 CRC 和硬件 CRC 外设各有什么优缺点？


A: 结论：软件实现灵活、可移植；硬件 CRC 外设速度高、CPU 占用低，但参数和适配能力可能受限。选型看平台和协议复杂度。


详细解释：


- MCU 常有 CRC 外设，适合固定协议。
- PC/Linux 软件实现足够快，开发和调试更方便。
- 某些硬件外设只支持固定 polynomial 或固定输入格式，需要特别确认。


常见坑/追问：


- 硬件 CRC 不一定和协议要求完全一致，尤其反射和初始值处理。
- 追问：上位机和 MCU CRC 对不齐时先查什么？先查参数，再查字节序和校验范围。


### Q10: ⭐🔴 如何排查“CRC 总是不对”的问题？


A: 结论：按“原始字节流 → 校验范围 → 参数 → 字节序 → 输出顺序”的顺序排查，基本能定位绝大多数 CRC 问题。


详细解释：


- 第一步确认抓到的原始十六进制字节是否完全一致。
- 第二步确认是否把起始符、长度、CRC 本身错误纳入。
- 第三步核对 poly/init/xorout/refin/refout。
- 第四步核对多字节字段编码顺序。
- 第五步看发送时 CRC 高低字节顺序。


代码示例：


```cpp
// 调试建议：把每一步中间值打印出来
printf("i=%zu byte=%02X crc=%04X\n", i, data[i], crc);
```


常见坑/追问：


- 很多“算法错了”其实是抓包工具显示顺序或自己抄协议抄漏字段。
- 追问：标准测试串 `123456789` 的意义是什么？它是 CRC 实现对齐的常用基准样例。


### Q11: ⭐🟡 CRC 和 Fletcher 校验有什么区别？


A: 结论：CRC 基于多项式除法，检错能力强，适合通信和存储；Fletcher 校验用两个累加和，计算更简单，CPU 友好，常用于嵌入式低算力场景；两者都不能检测所有错误模式。


详细解释：


- **CRC**：能检测单比特错、连续多比特错（突发错误，长度 ≤ 多项式阶数）、奇数个比特错（使用特定多项式时）。
- **Fletcher-16/32**：两个运行累加和，比单纯求和增加了位置信息，比 Adler-32 稍弱但更简单。
- **Adler-32**：Zlib 使用，与 Fletcher 类似但模数不同（65521 vs 255），速度和检错能力均衡。
- 嵌入式无硬件 CRC 时，Fletcher-16 是常见替代选择。


常见坑/追问：


- Fletcher 和 CRC 都无法检测某些特定错误模式（如全零数据），要根据实际错误模型选择。
- 追问：为什么 TCP 用 16 位校验和而不用 CRC？历史原因，16 位补码和简单快速，硬件实现早于 CRC，且 TCP 上层有重传机制做兜底。


---


### Q12: ⭐🟡 CRC 硬件加速如何使用？


A: 结论：现代 CPU 提供 CRC32 指令（x86 的 `_mm_crc32_u8/u32/u64`，ARM 的 `__crc32cb` 等），相比软件查表快 5-10 倍；STM32 等 MCU 也有硬件 CRC 外设。


详细解释：


- **x86 SSE4.2**：`_mm_crc32_u8/16/32/64`，直接映射到 `CRC32` 指令，单周期处理 1/2/4/8 字节。
- **ARM CRC 扩展**：`__crc32b/h/w` 内置函数（需 `-march=armv8-a+crc`）。
- **STM32 CRC 外设**：配置多项式寄存器，DMA 搬运数据，CPU 占用极低。
- 注意：硬件 CRC 的多项式和位序需和协议匹配，不一致会得到错误结果。


代码示例：


```cpp
// x86 SSE4.2 CRC32C
#include <nmmintrin.h>
uint32_t crc32c_hw(const uint8_t* data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; i++)
        crc = _mm_crc32_u8(crc, data[i]);
    return crc ^ 0xFFFFFFFF;
}
```


常见坑/追问：


- x86 `CRC32` 指令使用的是 Castagnoli 多项式（CRC32C），不是以太网/ZIP 用的 CRC32。
- 追问：如何判断 CPU 是否支持 SSE4.2？`__builtin_cpu_supports("sse4.2")`（GCC/Clang）或 CPUID。


---


### Q13: ⭐🔴 如何为自定义协议选择合适的 CRC 参数？


A: 结论：参考 Philip Koopman 的 CRC 多项式研究，根据数据块大小和期望的汉明距离（HD）选择多项式；常见场景：短帧（≤128B）用 CRC-8，中等帧用 CRC-16，长帧/高可靠用 CRC-32。


详细解释：


- **汉明距离（HD）**：HD=3 表示能检测所有 2 比特错；HD=4 能检测所有 3 比特错。
- 标准多项式的适用范围已有测试数据（Koopman 数据库）。
- CRC-16/IBM（Modbus）：适合工业串口，短到中等数据块。
- CRC-16/CCITT（0x1021）：适合 HDLC、SD 卡、USB 等。
- CRC-32C（Castagnoli）：性能最优，iSCSI、SCTP、Linux btrfs 使用。


常见坑/追问：


- 随便发明多项式可能检错能力很差，务必选用经过验证的标准多项式。
- 追问：为什么 CRC-32C 比 CRC-32（以太网）更好？Koopman 研究表明 0x1EDC6F41 在各数据长度下汉明距离更优。


---


### Q14: ⭐🟡 在 Qt 中如何封装一个通用的 CRC 校验模块？


A: 结论：封装一个 `CrcCalculator` 类，接受多项式参数（poly/init/xorout/refin/refout），内部按配置生成查找表，提供 `calculate(data, len)` 接口，支持运行时切换协议参数。


详细解释：


- 参数化设计：支持不同 width（8/16/32）、poly、init、xorout、refin、refout，一个类覆盖主流 CRC 变体。
- 查找表缓存：第一次计算时按 poly 生成并缓存，相同 poly 不重复计算。
- Qt 集成：可加 `QByteArray` 重载，方便与 Qt 串口、网络数据配合。


代码示例：


```cpp
class CrcCalculator {
    uint32_t table_[256];
    uint32_t poly_, init_, xorout_;
    bool refin_, refout_;
public:
    CrcCalculator(uint32_t poly, uint32_t init, uint32_t xorout,
                  bool refin, bool refout);
    uint32_t calculate(const uint8_t* data, size_t len) const;
    uint32_t calculate(const QByteArray& data) const {
        return calculate(reinterpret_cast<const uint8_t*>(data.constData()), data.size());
    }
};
```


常见坑/追问：


- 不同 width 的 CRC 需要不同类型的表（uint8_t/uint16_t/uint32_t），泛型设计时注意。
- 追问：如何测试 CRC 实现正确性？用标准测试串 `"123456789"` 对比已知期望值。


---


### Q15: ⭐🔴 CRC 残差（Residue）是什么？如何用它验证接收数据（含 CRC 本身）？


A: 结论：残差是将带 CRC 的完整帧（含 CRC 字段）再做一次 CRC 计算的固定结果；如果传输无误，结果应等于该 CRC 变体的标准残差值，这样无需单独提取 CRC 字段做比较。


详细解释：


- 原理：对数据 `D + CRC(D)` 计算 CRC，因为 CRC 的性质，结果是一个固定常数（残差）。
- CRC-32（IEEE）残差：`0x2144DF1C`；CRC-16/CCITT 残差：`0x1D0F`（具体值依实现参数）。
- 使用：接收端直接对整帧（含 CRC 字节）计算 CRC，与已知残差比对，比提取 CRC 再比较更简洁。
- 注意：只有 refout=false 且正常字节顺序时残差才固定，参数不同残差值也不同。


代码示例：


```cpp
// 接收整帧（含 CRC）后验证
uint32_t residue = crc32_ieee(full_frame, frame_len);
bool valid = (residue == 0x2144DF1C); // CRC-32 IEEE 标准残差
```


常见坑/追问：


- 残差值是协议参数的函数，换多项式或字节顺序后残差值需重新测试确认。
- 追问：残差验证比传统"提取CRC再比对"有什么优势？代码更简单，不需要手动分离 CRC 字段，但需要提前知道残差值。

---

## 📊 本章统计

| 指标 | 数量 |
|------|------|
| 总题目数 | 15 |
| 🟢 入门 | 1 |
| 🟡 进阶 | 10 |
| 🔴 高难 | 4 |
