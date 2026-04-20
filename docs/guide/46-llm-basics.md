# 46. LLM 应用开发基础


↑ 回到目录


### Q1: ⭐🟢 什么是 Zero-shot 和 Few-shot 学习？


A: 结论：Zero-shot 是指模型在未见过具体任务的前提下直接完成任务；Few-shot 是指给出少量示例后完成任务，两者体现大模型的泛化能力。提示设计（Prompt Design）是实现 Few-shot 的关键。


详细解释：


| 模式 | 应用场景 |
|------|----------|
| Zero-shot | 信息抽取、总结、分类等简单泛化任务 |
| Few-shot  | 特定领域的文档问答，给上下文和模版示例引导 |


```json
# Zero-shot 提示：
"请将以下内容分类到 '积极'、'中立' 或 '消极': \n内容: '这个商品很好用'"

# Few-shot 提示：
"这是一些分类示例：
- 积极: '非常喜欢这道菜'
- 中立: '餐厅环境一般'
- 消极: '菜太咸了'
请将以下内容分类: \n内容: '这个商品很好用'"
```


常见坑/追问：


- Few-shot 示例越多越好？不是。示例不能超出 token 限长，且应与任务贴近。
- 如何判断任务适合 Zero-shot 还是需要 Few-shot？看模型输出是否含歧义，是否需要预设格式或语言模版。


---


### Q2: ⭐🟢 什么是 Prompt Injection？如何防御？


A: 结论：Prompt Injection 指恶意输入破坏 LLM 提示或逻辑，比如让模型忽略指令或伪造信息。防御方法包括：输入过滤、业务逻辑校验、限制动态输入作用域。


详细解释：


示例攻击（忽略前文指令）：
- 指令："请说一段介绍你的文本，不要提到恶意内容"
- 攻击输入："好的。### 下列内容无视以上指令 ###"


防护策略：
1. **输入过滤**：
```python
user_input = sanitize(input_text)  # 去除指令注入格式
```


2. **上下文作用域**：
   - 使用 System Prompt 锁定规则，如 "你是客服助理，不能引用第三方来源”。

```json
{
  "context": [{"system_prompt": "你只能回答系统问题"}]
}
```


---


### Q3: ⭐🟡 限长裁剪（Truncation）有哪些常见策略？


A: 结论：限长裁剪是解决 LLM 上下文长度限制的问题，保留重要信息是核心，策略包括：
- 关键词优先（重要部分权重高）
- 时间优先（最新的重要）
- Chunking 拼接（每段文档摘要）


实例：从聊天历史提取关键摘要：
```python
def truncate_conversation(history, max_tokens):
    chunks = history.split("\n")
    priorities = rank_chunks(chunks)  # 权重最高先入
    output = []
    counter = 0
    for chunk in priorities:
        counter += num_tokens(chunk)
        if counter > max_tokens:
            break
        output.append(chunk)
    return output
```
