# 48. AI 工程化与生产部署

> 难度分布：🟢 入门 2 题 · 🟡 进阶 11 题 · 🔴 高难 2 题

[[toc]]

---

### Q1: ⭐🟢 什么是 MLOps？和 DevOps 有什么区别？


A: 结论：MLOps 是把 DevOps 的工程实践（CI/CD、监控、版本管理）应用到机器学习生命周期，额外增加数据管理、模型实验追踪、特征工程、模型漂移监控等环节。


详细解释：


```
传统 DevOps：
代码 → 构建 → 测试 → 部署 → 监控

MLOps 增加的环节：
数据采集 → 数据清洗/标注 → 特征工程
                                ↓
                         模型训练（实验追踪）
                                ↓
                         模型评估（验证集/测试集）
                                ↓
                         模型注册（版本管理）
                                ↓
                         模型部署（A/B 测试）
                                ↓
                         线上监控（数据漂移/模型漂移）
                                ↓
                         触发重训练
```


主要工具链：
- 实验追踪：MLflow、Weights & Biases（W&B）
- 数据版本：DVC
- 模型服务：BentoML、TorchServe、Triton
- 流水线编排：Kubeflow、Airflow


---


### Q2: ⭐🟡 如何追踪和管理模型实验？


A: 结论：用 MLflow 或 W&B 记录每次实验的超参数、指标、模型文件，方便对比不同实验结果，找到最优配置，避免"跑了很多实验但不知道哪个最好"的混乱状态。


详细解释：


```python
import mlflow
import mlflow.pytorch

with mlflow.start_run(run_name="qwen-lora-v2"):
    # 记录超参数
    mlflow.log_params({
        "model": "Qwen2.5-7B",
        "lora_r": 16,
        "lora_alpha": 32,
        "learning_rate": 2e-4,
        "epochs": 3,
        "batch_size": 8
    })

    # 训练循环中记录指标
    for epoch in range(3):
        train_loss = train_one_epoch(...)
        eval_loss = evaluate(...)
        mlflow.log_metrics({
            "train_loss": train_loss,
            "eval_loss": eval_loss
        }, step=epoch)

    # 保存模型
    mlflow.pytorch.log_model(model, "model")

# 之后可以在 mlflow ui 中对比所有实验
```


常见坑/追问：


- 不记录随机种子是实验无法复现的常见原因，`mlflow.log_param("seed", 42)` + `torch.manual_seed(42)` 必须同时做。
- 模型文件太大不适合存 MLflow，可以只记录 checkpoint 路径，模型存 S3/OSS。


---


### Q3: ⭐🟡 什么是数据漂移（Data Drift）和模型漂移（Model Drift）？如何监控？


A: 结论：数据漂移指线上输入数据的分布偏离了训练数据；模型漂移指模型效果随时间下降。两者都是线上模型"悄悄变差"的主要原因，需要持续监控。


详细解释：


```
数据漂移示例：
训练时用户年龄分布：18-35 岁为主
6 个月后线上：40-60 岁用户增多
→ 模型对老年用户的理解不足，准确率下降

模型漂移示例：
垃圾邮件过滤模型训练时没见过新的钓鱼邮件词汇
→ 新型垃圾邮件漏检率上升

监控方案：
1. 数据漂移检测：
   - PSI（Population Stability Index）：特征分布稳定性
   - KS 检验、卡方检验：比较训练集和线上分布

2. 模型效果监控：
   - 有标签：精度/召回率持续追踪
   - 无标签：用代理指标（点击率、用户反馈、拒绝率）

3. 告警 + 重训练触发：
   PSI > 0.2 → 告警
   准确率下降 > 5% → 触发重训练流水线
```


---


### Q4: ⭐🟡 模型服务化有哪些架构模式？


A: 结论：三种主流模式：同步 REST API（简单，适合低并发）、异步消息队列（高并发，解耦）、流式 SSE（LLM 生成，实时返回）。


详细解释：


```
1. 同步 REST API（最简单）
   客户端 → POST /predict → 等待 → 返回结果
   适合：延迟低（<200ms）、并发不高的场景

2. 异步消息队列（高并发推理）
   客户端 → 发消息到 Kafka/Redis → 推理 Worker 消费 → 结果写回 → 客户端轮询/回调
   适合：推理耗时较长、需要削峰填谷

3. 流式 SSE（LLM 专用）
   客户端 → 长连接 → Server 逐 token 推送 → 客户端实时展示
   适合：LLM 生成、用户需要即时反馈

4. gRPC 双向流（高性能场景）
   适合：微服务内部、延迟敏感、需要类型安全的场景
```


---


### Q5: ⭐🟡 如何对 LLM 推理服务做限流和降级？


A: 结论：限流防止推理服务被打爆（令牌桶/滑动窗口算法），降级在服务异常时返回兜底回复，保证基础可用性。


详细解释：


```python
import asyncio
from collections import deque
import time

class RateLimiter:
    """令牌桶限流：每秒最多 N 个请求"""
    def __init__(self, rate: int, burst: int):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_refill = time.monotonic()

    async def acquire(self):
        now = time.monotonic()
        # 补充令牌
        elapsed = now - self.last_refill
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False  # 限流，拒绝请求

# 降级策略
async def infer_with_fallback(prompt: str) -> str:
    try:
        result = await asyncio.wait_for(llm.infer(prompt), timeout=10.0)
        return result
    except asyncio.TimeoutError:
        return "服务繁忙，请稍后再试"  # 超时降级
    except Exception:
        return fallback_model.infer(prompt)  # 降级到小模型
```


常见坑/追问：


- 按用户 ID 限流比按 IP 限流更精准，防止一个用户打爆服务。
- 降级不等于报错，应该返回有意义的兜底内容，用户体验更好。


---


### Q6: ⭐🟡 如何用 Docker 打包和部署 AI 推理服务？


A: 结论：AI 推理服务 Docker 化的关键是：基础镜像选对（CUDA 版本匹配）、模型文件不放镜像里（挂载或运行时下载）、多阶段构建减小镜像体积。


详细解释：


```dockerfile
# 多阶段构建：先安装依赖，再复制代码
FROM nvidia/cuda:12.1-cudnn8-runtime-ubuntu22.04 AS base

# 安装系统依赖
RUN apt-get update && apt-get install -y python3.10 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码（不含模型文件）
COPY app/ /app/
WORKDIR /app

# 模型通过环境变量指定路径，运行时挂载
ENV MODEL_PATH=/models/qwen2.5-7b-q4.gguf

EXPOSE 8080
CMD ["python", "server.py"]
```


```yaml
# docker-compose.yml
services:
  llm-service:
    image: myapp/llm-service:latest
    runtime: nvidia          # 使用 GPU
    environment:
      - NVIDIA_VISIBLE_DEVICES=0
      - MODEL_PATH=/models/qwen2.5-7b-q4.gguf
    volumes:
      - /data/models:/models  # 模型文件从宿主机挂载
    ports:
      - "8080:8080"
```


常见坑/追问：


- CUDA 版本必须和宿主机驱动兼容，`nvidia-smi` 显示的 CUDA 版本是上限，镜像里的 CUDA 不能高于它。
- 模型文件放镜像里会导致镜像几十 GB，CI/CD 推拉镜像极慢，务必用挂载。


---


### Q7: ⭐🟡 Prompt 版本管理怎么做？


A: 结论：Prompt 和代码一样需要版本管理，存 Git 里、用专门的 Prompt 管理工具（LangSmith/PromptLayer）或者简单的数据库方案，配合 A/B 测试比较不同版本效果。


详细解释：


```python
# 方案 1：YAML 文件 + Git 管理（简单）
# prompts/v2_classification.yaml
"""
version: "2.1"
template: |
  你是一个专业的分类助手。
  请将以下文本分类为：{categories}

  文本：{input}

  输出格式：{"category": "xxx", "confidence": 0.9}
"""

# 方案 2：数据库管理（生产推荐）
class PromptManager:
    def get_prompt(self, name: str, version: str = "latest") -> str:
        return db.query(
            "SELECT template FROM prompts WHERE name=? AND version=?",
            (name, version)
        ).fetchone()["template"]

    def create_version(self, name: str, template: str) -> str:
        version = f"v{self.get_latest_version(name) + 1}"
        db.execute("INSERT INTO prompts VALUES (?,?,?,now())",
                   (name, version, template))
        return version
```


常见坑/追问：


- Prompt 改动和代码改动要一起发布（同一个 PR），防止代码期望新格式但 Prompt 还是旧版本。
- 重要 Prompt 变更要先做 offline 评估（在测试集上跑一遍），不要直接上线。


---


### Q8: ⭐🟡 如何监控线上 LLM 应用的质量？


A: 结论：建立多层监控：系统层（延迟/错误率）、应用层（token 消耗/成本）、质量层（用户反馈/LLM-as-Judge 抽样评估），三层缺一不可。


详细解释：


```python
# 结构化日志 + 指标上报
import time
import logging

def traced_llm_call(prompt: str, user_id: str) -> dict:
    start = time.monotonic()
    try:
        response = llm.chat(prompt)
        latency = time.monotonic() - start

        # 上报指标
        metrics.histogram("llm.latency_ms", latency * 1000)
        metrics.counter("llm.input_tokens", count_tokens(prompt))
        metrics.counter("llm.output_tokens", count_tokens(response))

        # 结构化日志（便于后续 LLM-as-Judge 抽样）
        logging.info({
            "event": "llm_response",
            "user_id": user_id,
            "prompt_hash": hash(prompt),
            "latency_ms": latency * 1000,
            "output_preview": response[:100]
        })
        return {"status": "ok", "response": response}

    except Exception as e:
        metrics.counter("llm.errors", tags={"error": type(e).__name__})
        raise
```


监控大盘必须包含：
- **P50/P95/P99 延迟**
- **每日成本**（token 消耗 × 单价）
- **错误率**（超时、API 限速、内容过滤）
- **用户点赞/差评率**（直接质量信号）


---


### Q9: ⭐🟡 大模型推理的显存不够怎么办？有哪些方案？


A: 结论：显存不足时按场景选方案：量化（最简单）、模型并行（多卡）、CPU 卸载（慢但能跑）、换更小模型（根本解决）。


详细解释：


| 方案 | 操作复杂度 | 速度影响 | 适用场景 |
|------|-----------|---------|---------|
| INT4 量化 | 低 | 轻微 | 单卡显存不够 |
| 张量并行（多卡） | 中 | 无负面影响 | 多卡服务器 |
| CPU 卸载（offload） | 低 | 明显变慢 | 没有足够 GPU |
| 换更小模型 | 低 | 提升 | 任务不需要大模型 |
| Flash Attention 2 | 低（换库） | 显存降 30-50% | Attention 层显存优化 |


```python
# CPU 卸载（部分层放 CPU）
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "Qwen2.5-14B",
    load_in_4bit=True,
    device_map="auto",   # 自动分配：GPU 放不下的层放 CPU
    max_memory={0: "10GB", "cpu": "30GB"}
)
```


---


### Q10: ⭐🟡 如何用 Triton Inference Server 部署模型？


A: 结论：Triton 是 NVIDIA 出品的高性能推理服务框架，支持 ONNX/TensorRT/PyTorch/TensorFlow 多后端，内置动态批处理和并发控制，是大规模 AI 服务的标准选择。


详细解释：


```
# 目录结构
model_repository/
└── resnet50/
    ├── config.pbtxt       # 模型配置
    └── 1/
        └── model.onnx     # 模型文件

# config.pbtxt
name: "resnet50"
backend: "onnxruntime"
max_batch_size: 32
input [{ name: "input", data_type: TYPE_FP32, dims: [3, 224, 224] }]
output [{ name: "output", data_type: TYPE_FP32, dims: [1000] }]
dynamic_batching { preferred_batch_size: [8, 16, 32] }
instance_group [{ count: 2, kind: KIND_GPU }]  # 2 个 GPU 实例
```


```bash
# 启动 Triton
docker run --gpus all -p 8000:8000 -p 8001:8001 \
  -v /path/to/model_repository:/models \
  nvcr.io/nvidia/tritonserver:24.01-py3 \
  tritonserver --model-repository=/models
```


常见坑/追问：


- `max_batch_size: 0` 表示禁用批处理，只在模型不支持批处理时设置。
- Triton 的性能瓶颈通常在前处理/后处理（Python），可以用 BLS（Business Logic Scripting）把预处理也放进 Triton。


---


### Q11: ⭐🔴 如何设计一个生产级 RAG 系统？


A: 结论：生产 RAG 系统需要考虑：文档解析（多格式）、分块策略、Embedding 选型、混合检索（向量+关键词）、重排序（Reranker）、答案生成、引用溯源、缓存、监控。


详细解释：


```
生产级 RAG 架构：

【离线索引流水线】
文档（PDF/Word/HTML）
   ↓ 解析（pymupdf/unstructured）
   ↓ 清洗（去页眉页脚、表格处理）
   ↓ 分块（512 token，50% overlap）
   ↓ Embedding（bge-m3）
   ↓ 存入向量数据库（Qdrant）+ 全文索引（Elasticsearch）

【在线检索流水线】
用户问题
   ↓ Query 改写（多角度扩展）
   ↓ 混合检索（向量检索 + BM25 关键词检索）
   ↓ 结果合并（RRF 算法）
   ↓ Reranker（cross-encoder 精排，Top-5 → Top-3）
   ↓ 拼入 Prompt
   ↓ LLM 生成（含引用标注）
   ↓ 返回答案 + 来源文档
```


关键优化点：
- **Query 改写**：一个问题生成 3-5 个变体，扩大召回
- **混合检索**：向量检索擅长语义，BM25 擅长精确关键词，互补
- **Reranker**：用 cross-encoder 精排，比向量检索准确率高很多
- **引用溯源**：每段答案标注来源，用户可验证


---


### Q12: ⭐🟡 如何在 C++ 应用中集成 ONNX Runtime 做本地 AI 推理？


A: 结论：ONNX Runtime 提供 C++ API，直接链接库，适合在桌面/嵌入式 C++ 应用中做本地推理，不需要 Python 环境，支持 CPU/CUDA/DirectML 等多个 EP（Execution Provider）。


详细解释：


```cpp
#include <onnxruntime_cxx_api.h>
#include <vector>

class ONNXInference {
    Ort::Env m_env{ORT_LOGGING_LEVEL_WARNING, "inference"};
    Ort::Session m_session{nullptr};

public:
    ONNXInference(const std::string& modelPath) {
        Ort::SessionOptions opts;
        opts.SetIntraOpNumThreads(4);
        opts.SetGraphOptimizationLevel(ORT_ENABLE_ALL);

        // 可选：启用 CUDA
        // OrtCUDAProviderOptions cudaOpts;
        // opts.AppendExecutionProvider_CUDA(cudaOpts);

        m_session = Ort::Session(m_env, modelPath.c_str(), opts);
    }

    std::vector<float> run(const std::vector<float>& input,
                           const std::vector<int64_t>& shape) {
        Ort::MemoryInfo memInfo = Ort::MemoryInfo::CreateCpu(
            OrtArenaAllocator, OrtMemTypeDefault);

        auto inputTensor = Ort::Value::CreateTensor<float>(
            memInfo, const_cast<float*>(input.data()),
            input.size(), shape.data(), shape.size());

        const char* inputNames[]  = {"input"};
        const char* outputNames[] = {"output"};

        auto outputs = m_session.Run(
            Ort::RunOptions{}, inputNames, &inputTensor, 1,
            outputNames, 1);

        float* outData = outputs[0].GetTensorMutableData<float>();
        size_t outSize = outputs[0].GetTensorTypeAndShapeInfo().GetElementCount();
        return std::vector<float>(outData, outData + outSize);
    }
};
```


常见坑/追问：


- `Ort::Session` 构造很慢（加载模型），必须复用，不能每次推理都重建。
- 输入输出名称必须和 ONNX 导出时指定的一致，可以用 `Netron` 工具查看 ONNX 模型结构。
- Qt 中推理要放在 `QThread` 里，避免阻塞主线程。


---


### Q13: ⭐🟢 Ollama 是什么？如何在开发中使用？


A: 结论：Ollama 是一个本地 LLM 运行工具，一行命令拉取并运行各种开源模型，提供兼容 OpenAI 格式的 REST API，开发时可以用它替代 OpenAI API，零费用且数据不出本机。


详细解释：


```bash
# 安装并运行模型
ollama pull qwen2.5:7b
ollama run qwen2.5:7b "解释一下 C++ 虚函数表"

# Ollama 默认提供 OpenAI 兼容 API（http://localhost:11434）
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "你好"}]
  }'

# Python（直接用 openai 库切换 base_url）
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
response = client.chat.completions.create(
    model="qwen2.5:7b",
    messages=[{"role": "user", "content": "解释虚函数表"}]
)
```


常见坑/追问：


- Ollama 使用 llama.cpp 作为后端，支持 CPU 推理，没有 GPU 也能用（只是慢）。
- 模型存储在 `~/.ollama/models/`，大模型注意磁盘空间。


---


### Q14: ⭐🟡 如何评估 RAG 系统的检索质量？


A: 结论：RAG 检索质量用 Recall@K（检索结果里是否包含正确文档）和 MRR（正确文档排名）评估；生成质量用 Faithfulness（答案是否忠于检索结果）和 Answer Relevance（答案是否回答了问题）评估。


详细解释：


| 指标 | 含义 | 计算方式 |
|------|------|---------|
| Recall@K | Top-K 里含正确文档的比例 | 命中数 / 总问题数 |
| MRR | 正确文档平均排名倒数 | mean(1/rank) |
| Faithfulness | 答案内容是否来自检索结果 | LLM-as-Judge |
| Answer Relevance | 答案是否回答了原始问题 | Embedding 相似度 |
| Context Precision | 检索结果中有多少是相关的 | LLM-as-Judge |


```python
# 用 RAGAS 框架自动评估 RAG
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall

dataset = [...]  # 问题、检索上下文、生成答案、参考答案
result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_recall])
print(result)
# {'faithfulness': 0.87, 'answer_relevancy': 0.82, 'context_recall': 0.91}
```


---


### Q15: ⭐🔴 一个 AI 功能从 0 到生产上线，完整流程是什么？


A: 结论：完整流程分 5 个阶段：需求定义→原型验证→离线评估→灰度上线→持续监控。每个阶段有明确的 Go/No-Go 标准，不要跳步骤。


详细解释：


```
阶段 1：需求定义（1-2 天）
- 明确任务：分类/生成/检索？
- 定义成功指标：准确率 >90%？延迟 <500ms？
- 数据现状：有多少标注数据？

阶段 2：原型验证（3-5 天）
- Prompt Engineering 快速验证可行性
- 在 20-50 条样本上手工测试
- Go：基本可行，确定技术路线

阶段 3：离线评估（1-2 周）
- 建立评估数据集（100-500 条）
- 跑自动评估（BLEU/LLM-as-Judge）
- A/B 对比不同方案
- Go：核心指标达标，成本可接受

阶段 4：灰度上线（1 周）
- 1% → 10% 流量
- 监控错误率/延迟/用户反馈
- Go：线上指标和离线一致

阶段 5：持续监控
- 每日成本报表
- 周度质量评估抽样
- 数据漂移告警
- 季度模型迭代评估
```


常见坑/追问：


- 跳过离线评估直接上线是最常见的失误，线上出问题影响用户且难以快速定位。
- "数据飞轮"：线上用户反馈（差评/纠正）是最宝贵的训练数据，要建立收集机制。

---

## 📊 本章统计

| 指标 | 数量 |
|------|------|
| 总题目数 | 15 |
| 🟢 入门 | 2 |
| 🟡 进阶 | 11 |
| 🔴 高难 | 2 |
