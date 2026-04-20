# 47. 机器学习模型优化


↑ 回到目录


### Q1: ⭐🟢 Fine-tuning 和 Prompt Engineering 的区别？什么时候用哪个？


A: 结论：Prompt Engineering 是通过设计输入让模型完成任务，零成本但效果有上限；Fine-tuning 是用数据调整模型权重，效果更好但需要数据和计算资源。


详细解释：


| | Prompt Engineering | Fine-tuning |
|--|--|--|
| 成本 | 低（只有 API 费用） | 高（需要标注数据 + GPU） |
| 效果上限 | 受模型能力限制 | 可以超越基础模型在特定任务上的表现 |
| 适用场景 | 通用任务、快速验证 | 特定领域、固定格式输出、垂直行业 |
| 数据需求 | 无 | 至少几百条，最好 1000+ |
| 更新频率 | 随时改 Prompt | 重新 Fine-tune 成本高 |


**决策树：**
- 先用 Prompt Engineering 验证可行性
- Prompt 调到极致还不够 → 考虑 Fine-tuning
- 数据敏感不能上云 → 本地 Fine-tuning（LoRA）


---


### Q2: ⭐🟡 什么是 LoRA？为什么它比全量 Fine-tuning 更常用？


A: 结论：LoRA（Low-Rank Adaptation）是在原模型权重旁插入小矩阵，只训练这些小矩阵，原权重冻结。参数量只有全量的 0.1%-1%，显存需求大幅降低。


详细解释：


```
全量 Fine-tuning：
W_new = W_original + ΔW    (ΔW 和 W 同样大，7B 模型需要 ~40GB 显存)

LoRA：
W_new = W_original + A × B  (A: d×r, B: r×d, r 远小于 d)
只训练 A 和 B，r=8 时参数量 = 2×d×8，极小

示例：
- 7B 模型全量 Fine-tune：需要 ~80GB 显存 (fp16)
- 7B 模型 LoRA（r=8）：需要 ~12GB 显存
```


常见坑/追问：


- `r`（rank）越大，LoRA 参数越多，效果越接近全量，但显存也增加，通常 r=8 或 r=16。
- QLoRA = 量化 + LoRA，先把模型量化到 4-bit，再做 LoRA，8GB 显卡可以 Fine-tune 7B 模型。


---


### Q3: ⭐🟡 模型量化是什么？INT8/FP16/Q4 有什么区别？


A: 结论：量化是把模型权重从高精度（FP32）压缩到低精度（FP16/INT8/INT4），降低显存占用和推理延迟，代价是精度略有损失。


详细解释：


| 精度 | 每参数占用 | 7B 模型显存 | 精度损失 | 推荐场景 |
|------|-----------|------------|---------|---------|
| FP32 | 4 字节 | ~28 GB | 无 | 训练 |
| FP16 / BF16 | 2 字节 | ~14 GB | 极小 | 推理基线 |
| INT8 | 1 字节 | ~7 GB | 小 | 服务端推理 |
| Q4_K_M (GGUF) | ~0.5 字节 | ~4 GB | 中等 | 消费级 GPU/CPU 推理 |


```python
# Transformers + bitsandbytes 量化加载
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-7B",
    load_in_4bit=True,          # INT4 量化
    bnb_4bit_compute_dtype=torch.bfloat16,
    device_map="auto"
)
```


常见坑/追问：


- INT4 量化在数学推理、代码生成等精度敏感任务上损失明显，推荐 INT8 或 Q4_K_M。
- BF16 比 FP16 数值范围更大，训练时更稳定（不容易溢出），推理时两者差不多。


---


### Q4: ⭐🟡 什么是知识蒸馏（Knowledge Distillation）？


A: 结论：知识蒸馏是用大模型（Teacher）的输出来训练小模型（Student），让小模型学到大模型的"软标签"（概率分布），而不只是硬标签（0/1），使小模型达到接近大模型的效果。


详细解释：


```
传统训练：小模型学 Ground Truth（硬标签）
蒸馏训练：小模型学 Teacher 的输出概率分布（软标签）

硬标签（one-hot）：[0, 0, 1, 0, 0]
软标签（Teacher 输出）：[0.01, 0.03, 0.85, 0.08, 0.03]
                                              ↑ 包含"第3和第4类有点像"的信息

损失函数：
L = α × CrossEntropy(student, true_label)
  + (1-α) × KL_divergence(student, teacher)
```


应用场景：
- GPT-4 蒸馏到小模型（OpenAI 的 GPT-3.5 一定程度上用了这个思路）
- 大模型生成数据 → 微调小模型（"合成数据蒸馏"）


常见坑/追问：


- Teacher 模型越大，蒸馏效果通常越好，但 Teacher 和 Student 差距太大时，Student 学不了（capacity gap 问题）。
- 目前 LLM 领域流行"数据蒸馏"：用大模型生成高质量训练数据，而不是直接用 logits 蒸馏。


---


### Q5: ⭐🟡 什么是 RLHF？为什么 LLM 需要它？


A: 结论：RLHF（人类反馈强化学习）是让人类对模型输出打分，训练一个奖励模型，再用强化学习（PPO）优化 LLM 使其输出更符合人类偏好。ChatGPT 就用了 RLHF。


详细解释：


```
RLHF 三步骤：

1. SFT（有监督微调）
   人工写高质量回答 → Fine-tune 基础模型

2. 奖励模型训练（Reward Model）
   人类对多个回答排序 → 训练 RM 预测"哪个回答更好"

3. PPO 强化学习
   LLM 生成回答 → RM 打分 → PPO 更新 LLM 权重（让分数更高）
```


替代方案：
- **DPO**（Direct Preference Optimization）：直接从偏好数据优化，不需要 RM 和 PPO，更简单稳定，目前更主流
- **GRPO**：DeepSeek-R1 使用的方法，基于组相对策略优化


常见坑/追问：


- RLHF 的对齐可能导致"过度对齐"（over-refusal），模型变得太保守拒绝正常请求。
- 奖励模型的质量决定上限，"奖励作弊"（reward hacking）是核心挑战。


---


### Q6: ⭐🟡 模型剪枝（Pruning）是什么原理？


A: 结论：剪枝是移除模型中贡献小的参数（权重置零或删除神经元），减少参数量和计算量。分非结构化剪枝（单个权重）和结构化剪枝（整个注意力头/层）。


详细解释：


```
非结构化剪枝（稀疏化）：
把绝对值小于阈值的权重置零
W = [0.01, 0.8, 0.003, 0.6, 0.002]
      ↓ 剪枝 threshold=0.1
W = [0,    0.8, 0,     0.6, 0    ]
优点：压缩率高；缺点：稀疏矩阵在 GPU 上不一定更快（需要专用硬件）

结构化剪枝（移除整个注意力头）：
评估每个 Attention Head 的重要性 → 删除不重要的头
优点：直接减少计算量，在标准硬件上有实际加速
缺点：精度损失更大
```


常见坑/追问：


- 剪枝后通常需要"再训练"（fine-tune）来恢复精度，叫 prune-then-finetune。
- LLM 领域结构化剪枝更实用，非结构化剪枝需要稀疏计算库支持（如 NVIDIA cuSPARSE）。


---


### Q7: ⭐🟡 什么是 ONNX？为什么用它做模型部署？


A: 结论：ONNX（Open Neural Network Exchange）是跨框架的模型交换格式，把 PyTorch/TensorFlow 训练的模型导出为统一格式，用 ONNX Runtime 在 CPU/GPU/嵌入式上高效推理。


详细解释：


```python
# PyTorch → ONNX 导出
import torch
import torch.onnx

model = MyModel()
model.load_state_dict(torch.load("model.pth"))
model.eval()

dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    opset_version=17,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}}  # 动态 batch
)

# ONNX Runtime 推理（C++）
#include <onnxruntime_cxx_api.h>
Ort::Session session(env, "model.onnx", Ort::SessionOptions{});
// 设置输入张量 → Run → 读取输出
```


常见坑/追问：


- ONNX 不支持所有 PyTorch 算子，导出时可能报 `Unsupported op`，需要用 `torch.jit.script` 或自定义算子。
- `dynamic_axes` 很重要，不加的话 batch_size 固定为导出时的值，不支持变长输入。


---


### Q8: ⭐🟡 TensorRT 是什么？和 ONNX Runtime 的区别？


A: 结论：TensorRT 是 NVIDIA 专为 GPU 推理优化的框架，自动做层融合、精度校准、kernel 调优，推理速度比 ONNX Runtime 快 2-5x。但只能在 NVIDIA GPU 上用。


详细解释：


| | ONNX Runtime | TensorRT |
|--|--|--|
| 硬件支持 | CPU/GPU/NPU（跨平台） | 仅 NVIDIA GPU |
| 优化深度 | 通用优化 | 深度 GPU 专项优化 |
| 推理速度 | 快 | 更快（2-5x） |
| 部署复杂度 | 简单 | 较复杂（需要 build engine） |
| INT8 校准 | 支持 | 支持，精度更高 |


```python
# PyTorch → TensorRT 流程
import torch_tensorrt

model_trt = torch_tensorrt.compile(
    model,
    inputs=[torch_tensorrt.Input((1, 3, 224, 224), dtype=torch.float16)],
    enabled_precisions={torch.float16}  # FP16 推理
)
# 保存并在 C++ 中用 LibTorch 加载推理
```


---


### Q9: ⭐🟡 在嵌入式/边缘设备上部署模型有哪些方案？


A: 结论：嵌入式部署核心是模型要小、推理要快、内存要省，主流方案：TFLite（Android/Linux ARM）、NCNN（移动端，腾讯开源）、llama.cpp（LLM）、OpenVINO（Intel 设备）。


详细解释：


| 框架 | 适用设备 | 特点 |
|------|---------|------|
| TensorFlow Lite | Android/iOS/Linux ARM | Google 生态，文档丰富 |
| NCNN | Android/ARM Linux | 无依赖，腾讯开源，专为移动端 |
| llama.cpp | CPU/GPU 通用 | 纯 C++，支持量化 LLM |
| OpenVINO | Intel CPU/iGPU/VPU | Intel 专项优化 |
| CoreML | Apple 设备 | 苹果 Neural Engine 加速 |


```cpp
// NCNN C++ 推理示例
#include "ncnn/net.h"

ncnn::Net net;
net.load_param("model.param");
net.load_model("model.bin");

ncnn::Mat input = ncnn::Mat::from_float32(...);
ncnn::Extractor ex = net.create_extractor();
ex.input("input", input);

ncnn::Mat output;
ex.extract("output", output);
```


常见坑/追问：


- ARM 设备 FP32 推理太慢，必须量化到 INT8 或 FP16，同时考虑 NEON SIMD 加速。
- 模型太大导致加载时间长，可以只加载常用模型，其他懒加载。


---


### Q10: ⭐🟡 什么是 Batch Inference？如何优化吞吐量？


A: 结论：Batch Inference 是把多个请求合并成一个批次送给模型，充分利用 GPU 并行能力，提升吞吐量。核心优化：动态批处理（Dynamic Batching）和连续批处理（Continuous Batching）。


详细解释：


```
普通推理：每个请求单独处理
请求 1 → GPU → 结果 1
请求 2 → GPU → 结果 2   （GPU 利用率低）

Static Batching：等凑满 batch 再处理
[请求1, 请求2, 请求3, 请求4] → GPU → [结果1,2,3,4]
问题：短请求要等长请求，延迟高

Continuous Batching（LLM 专用）：
每生成一个 token 就检查哪些请求完成了，立即加入新请求
始终保持 GPU 满载，延迟和吞吐都好
```


生产级 LLM 推理框架：
- **vLLM**：PagedAttention + Continuous Batching，吞吐比 HuggingFace 高 24x
- **TGI（Text Generation Inference）**：HuggingFace 官方推理服务
- **SGLang**：支持复杂多步推理的高性能框架


---


### Q11: ⭐🔴 如何做模型的 A/B 测试和灰度发布？


A: 结论：A/B 测试是同时运行两个版本，随机分流用户，收集指标对比；灰度发布是新版本逐步放量（1% → 10% → 50% → 100%），有问题随时回滚。


详细解释：


```python
# 简单 A/B 分流
import hashlib

def get_model_version(user_id: str) -> str:
    # 用 user_id hash 保证同一用户始终路由到同一版本
    hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
    if hash_val < 10:   # 10% 流量给新模型
        return "model_v2"
    return "model_v1"

# 收集指标对比
metrics = {
    "model_v1": {"latency_p99": 450, "thumbs_up_rate": 0.72},
    "model_v2": {"latency_p99": 380, "thumbs_up_rate": 0.78},
}
```


关键指标：
- **延迟**：P50/P95/P99
- **质量**：用户点赞率、任务完成率、LLM-as-Judge 评分
- **成本**：每次请求 token 消耗


常见坑/追问：


- 不要只看平均值，P99 延迟才是用户体感最差的场景。
- 样本量要足够（通常需要数千次请求）才能统计显著，过早下结论会误判。


---


### Q12: ⭐🟡 Transformer 的核心结构是什么？Self-Attention 怎么计算？


A: 结论：Transformer 由 Encoder（Self-Attention + FFN）和 Decoder 组成，LLM 通常只用 Decoder。Self-Attention 通过 Q/K/V 矩阵计算每个 token 对其他 token 的注意力权重。


详细解释：


```
Self-Attention 计算：

1. 输入 X 分别乘三个矩阵得到 Q、K、V
   Q = X × W_Q
   K = X × W_K
   V = X × W_V

2. 计算注意力分数
   Attention(Q, K, V) = softmax(Q × K^T / √d_k) × V

   Q × K^T：每个 token 对其他 token 的相关性得分
   / √d_k：缩放，防止点积过大导致 softmax 梯度消失
   softmax：归一化为概率
   × V：加权求和得到输出

3. Multi-Head Attention：并行做多个 Self-Attention，拼接结果
```


常见坑/追问：


- Self-Attention 的计算复杂度是 O(n²)（n=序列长度），长序列时很慢，这是 Flash Attention 等优化的动机。
- `d_k` 是每个 head 的维度，不是总维度，总维度除以 head 数量 = `d_k`。


---


### Q13: ⭐🟡 什么是 KV Cache？为什么 LLM 推理需要它？


A: 结论：LLM 自回归生成时，每次生成新 token 都需要重新计算所有历史 token 的 K/V，KV Cache 把历史 K/V 缓存起来，避免重复计算，推理速度提升数倍。


详细解释：


```
没有 KV Cache（慢）：
生成第 N 个 token 时，重新计算 token 1~N 的所有 K、V → O(N²) 复杂度

有 KV Cache（快）：
缓存 token 1~N-1 的 K、V，只计算新 token N 的 K、V，拼接上去 → O(N) 复杂度

显存占用（KV Cache）：
= 2 × num_layers × num_heads × head_dim × seq_len × sizeof(dtype)
7B 模型，seq_len=4096，FP16：约 2GB
```


常见坑/追问：


- KV Cache 占显存，长上下文时 KV Cache 可能比模型本身还大，需要显存管理（vLLM 的 PagedAttention 解决这个问题）。
- 量化 KV Cache（KV Cache quantization）是节省显存的有效手段，INT8 量化损失极小。


---


### Q14: ⭐🟢 什么是 Vector Database？常见选择有哪些？


A: 结论：向量数据库专门存储和检索高维向量（Embedding），支持近似最近邻（ANN）搜索，是 RAG 系统的核心组件。


详细解释：


| 数据库 | 特点 | 适用场景 |
|--------|------|---------|
| **Faiss**（Meta） | 本地库，极快，无服务端 | 单机、离线检索 |
| **Chroma** | 轻量，Python 原生，支持持久化 | 开发/原型 |
| **Qdrant** | Rust 编写，高性能，REST/gRPC | 生产部署 |
| **Milvus** | 分布式，大规模 | 亿级向量 |
| **pgvector** | PostgreSQL 插件 | 已有 PG 数据库的场景 |


```python
# Faiss 示例
import faiss
import numpy as np

d = 1024  # 向量维度
index = faiss.IndexFlatIP(d)  # 内积（余弦相似度用归一化后的内积）

# 添加向量
vectors = np.random.random((1000, d)).astype('float32')
faiss.normalize_L2(vectors)
index.add(vectors)

# 检索 Top-5
query = np.random.random((1, d)).astype('float32')
faiss.normalize_L2(query)
distances, indices = index.search(query, k=5)
```


---


### Q15: ⭐🔴 如何把 AI 推理能力集成进 Qt/C++ 桌面应用？架构怎么设计？


A: 结论：推荐"推理服务化"架构：推理逻辑跑在独立进程/线程（llama.cpp server 或 ONNX Runtime worker），Qt 通过 IPC 或本地 HTTP 通信，UI 层只负责展示和交互。


详细解释：


```
推荐架构：

┌─────────────────────────────────────┐
│           Qt 主线程（UI）              │
│  用户输入 → 发送请求 → 显示流式输出     │
└──────────────┬──────────────────────┘
               │ QNetworkAccessManager (HTTP)
               │ 或 QLocalSocket (IPC)
┌──────────────▼──────────────────────┐
│      推理工作进程/线程                  │
│  llama.cpp server / ONNX Runtime    │
│  接收请求 → 推理 → 流式返回结果          │
└─────────────────────────────────────┘

Qt 层关键设计：
- 推理请求在 QThread 发起，避免阻塞 UI
- 流式输出通过 readyRead 信号实时更新 QTextEdit
- 任务队列控制并发（同时只跑 1 个推理任务）
- 模型预热（应用启动时后台加载，首次推理无延迟）
```


```cpp
// Qt 推理任务队列
class InferenceQueue : public QObject {
    Q_OBJECT
    QQueue<QString> m_queue;
    bool m_busy = false;

public slots:
    void enqueue(const QString& prompt) {
        if (m_busy) { m_queue.enqueue(prompt); return; }
        m_busy = true;
        emit startInference(prompt);
    }
    void onFinished() {
        m_busy = false;
        if (!m_queue.isEmpty())
            enqueue(m_queue.dequeue());
    }
signals:
    void startInference(const QString& prompt);
};
```


常见坑/追问：


- 不要在主线程做任何推理操作，哪怕只是模型加载也会卡 UI 数秒。
- 推理进程崩溃要有重启机制（`QProcess::finished` 信号监听并重启）。
