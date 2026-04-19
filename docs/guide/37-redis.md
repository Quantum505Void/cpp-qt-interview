# 37. Redis 原理与应用


↑ 回到目录


### Q1: ⭐🟢 Redis 有哪些基础数据结构，各适合什么场景？


A: 结论：Redis 提供 5 种核心数据结构，每种针对不同访问模式优化。


详细解释：


- **String**：最基础，存单值、计数器、序列化对象。`SET key value EX 60`
- **Hash**：存对象字段，比 JSON 字符串更节省内存且支持部分更新。`HSET device:1 temp 25.6 status online`
- **List**：有序列表，支持两端操作，适合消息队列、最近记录。`LPUSH / RPOP`
- **Set**：无序不重复集合，适合去重、标签、交并差运算。`SADD / SINTER`
- **Sorted Set (ZSet)**：带分数的有序集合，适合排行榜、延迟队列。`ZADD leaderboard 100 user1`


常见坑/追问：


- String 存 JSON 和 Hash 存字段的选择：字段少且整体读取多用 String；字段多且频繁部分更新用 Hash。
- List 做消息队列的缺点：不支持消费者组，生产环境推荐 Stream 类型。


---


### Q2: ⭐🟡 Redis 持久化 RDB 和 AOF 的区别，如何选择？


A: 结论：RDB 是快照，恢复快但可能丢数据；AOF 是日志，数据安全但文件大。


详细解释：


- **RDB**：按配置间隔（如 `save 900 1`）将内存快照写入 `.rdb` 文件。fork 子进程写，主进程不阻塞。重启恢复速度快，但最多丢失上次快照后的数据。
- **AOF**：记录每条写命令到 `.aof` 文件。`appendfsync` 有三种策略：
- `always`：每次写都 fsync，最安全，性能最差
- `everysec`（推荐）：每秒 fsync，最多丢 1 秒数据
- `no`：由 OS 决定，性能最好，不可控
- **混合持久化**（Redis 4.0+）：AOF 重写时先写 RDB 快照再追加增量 AOF，兼顾恢复速度和数据安全。


常见坑/追问：


- 工业上位机场景：若 Redis 只做缓存（数据库有持久化），可关闭持久化提升性能；若做消息中转，用 AOF everysec。
- AOF 文件膨胀：`BGREWRITEAOF` 触发重写压缩。


---


### Q3: ⭐🟡 Redis 过期策略和内存淘汰机制是什么？


A: 结论：Redis 用惰性删除 + 定期删除处理过期键，内存满时按淘汰策略驱逐键。


详细解释：


- **过期删除**：
- 惰性删除：访问时检查是否过期，过期则删除。节省 CPU 但可能内存泄漏。
- 定期删除：每 100ms 随机抽取部分设了过期的键检查删除。
- **内存淘汰策略**（`maxmemory-policy`）：
- `noeviction`：不淘汰，写操作报错（默认）
- `allkeys-lru`：所有键中淘汰最近最少使用（最常用）
- `volatile-lru`：只淘汰设了过期时间的键中 LRU
- `allkeys-lfu`：按访问频率淘汰（Redis 4.0+）
- `volatile-ttl`：淘汰剩余 TTL 最短的键


常见坑/追问：


- 上位机缓存设备状态时，建议用 `volatile-lru` + 给所有缓存键设 TTL，防止内存无限增长。
- LRU 是近似算法（随机采样），不是精确 LRU。


---


### Q4: 🟡 Redis 发布订阅（Pub/Sub）原理及局限性？


A: 结论：Pub/Sub 是简单的消息广播机制，但不持久化、不支持消费确认，生产慎用。


详细解释：


- **原理**：发布者 `PUBLISH channel message`，订阅者 `SUBSCRIBE channel`。Redis 服务端维护频道到订阅者列表的映射，收到消息立即推送。
- **模式订阅**：`PSUBSCRIBE sensor:*` 支持通配符订阅多个频道。
- **局限性**：
- 消息不持久化：订阅者离线期间的消息丢失
- 无消费确认：无法保证消息被处理
- 无消费者组：所有订阅者都收到同一消息（广播语义）
- **替代方案**：Redis Stream（`XADD/XREAD/XGROUP`）支持持久化、消费者组、消息确认。


常见坑/追问：


- Qt 应用订阅 Redis 消息：需在独立线程中阻塞等待，收到消息后通过信号槽传递给 UI 线程。
- Pub/Sub 适合：实时广播（如设备状态变更通知），不适合：需要可靠投递的命令消息。


---


### Q5: ⭐🔴 如何在 C++ 中使用 hiredis 连接 Redis？


A: 结论：hiredis 是 Redis 官方 C 客户端，提供同步和异步两种 API。


详细解释：


```cpp
#include <hiredis/hiredis.h>
#include <iostream>
#include <string>

class RedisClient {
    redisContext* ctx_ = nullptr;
public:
    bool connect(const std::string& host, int port) {
        ctx_ = redisConnect(host.c_str(), port);
        if (!ctx_ || ctx_->err) {
            if (ctx_) {
                std::cerr << "Redis error: " << ctx_->errstr << std::endl;
                redisFree(ctx_);
                ctx_ = nullptr;
            }
            return false;
        }
        return true;
    }

    bool set(const std::string& key, const std::string& val, int ttl = 0) {
        redisReply* reply;
        if (ttl > 0)
            reply = (redisReply*)redisCommand(ctx_, "SET %s %s EX %d",
                                              key.c_str(), val.c_str(), ttl);
        else
            reply = (redisReply*)redisCommand(ctx_, "SET %s %s",
                                              key.c_str(), val.c_str());
        bool ok = reply && reply->type != REDIS_REPLY_ERROR;
        freeReplyObject(reply);
        return ok;
    }

    std::string get(const std::string& key) {
        redisReply* reply = (redisReply*)redisCommand(ctx_, "GET %s", key.c_str());
        std::string result;
        if (reply && reply->type == REDIS_REPLY_STRING)
            result = reply->str;
        freeReplyObject(reply);
        return result;
    }

    ~RedisClient() { if (ctx_) redisFree(ctx_); }
};
```


常见坑/追问：


- hiredis 同步 API 非线程安全，多线程需每线程独立连接或加锁。
- 推荐用 `redis-plus-plus`（基于 hiredis 的 C++17 封装），支持连接池、异常处理、Pipeline。


---


### Q6: ⭐🔴 redis-plus-plus 如何使用连接池和 Pipeline？


A: 结论：redis-plus-plus 提供 RAII 风格 API，连接池自动管理，Pipeline 批量减少 RTT。


详细解释：


```cpp
#include <sw/redis++/redis++.h>
using namespace sw::redis;

// 连接池配置
ConnectionPoolOptions pool_opts;
pool_opts.size = 5;           // 池大小
pool_opts.wait_timeout = std::chrono::milliseconds(100);

ConnectionOptions conn_opts;
conn_opts.host = "127.0.0.1";
conn_opts.port = 6379;
conn_opts.socket_timeout = std::chrono::milliseconds(50);

Redis redis(conn_opts, pool_opts);

// 基本操作
redis.set("device:1:temp", "25.6", std::chrono::seconds(60));
auto val = redis.get("device:1:temp");  // OptionalString

// Pipeline 批量写入（减少网络往返）
auto pipe = redis.pipeline();
for (int i = 0; i < 100; ++i) {
    pipe.set("sensor:" + std::to_string(i), std::to_string(i * 0.1));
}
pipe.exec();  // 一次性发送所有命令

// Hash 操作
redis.hset("device:1", "temp", "25.6");
redis.hset("device:1", "status", "online");
auto temp = redis.hget("device:1", "temp");
```


常见坑/追问：


- Pipeline 不是事务，命令可能部分失败；需要原子性用 `MULTI/EXEC`。
- Qt 中使用：在 `QThread` 子线程中操作 Redis，结果通过 `emit signal` 传给 UI。


---


### Q7: 🟡 Redis 在工业上位机软件中有哪些典型应用场景？


A: 结论：上位机中 Redis 主要用于设备状态缓存、实时数据共享、进程间通信和报警去重。


详细解释：


- **设备状态缓存**：多个 Qt 进程共享设备在线状态，避免每次查数据库。`HSET device:{id} status online temp 25.6`，设 TTL 防止僵尸状态。
- **实时数据共享**：采集进程写 Redis，显示进程读 Redis，解耦采集与展示。比共享内存更灵活，支持跨机器。
- **进程间通信**：用 Pub/Sub 或 List 实现轻量级消息队列，替代复杂的 IPC 机制。
- **报警去重**：`SET alarm:{id} 1 EX 300 NX`，5 分钟内同一报警只触发一次。
- **限流**：`INCR rate:{user} / EXPIRE`，防止操作过于频繁。
- **分布式配置**：多台上位机共享运行参数，修改后 Pub/Sub 通知各节点刷新。


常见坑/追问：


- Redis 不适合存大量历史数据（内存贵），历史数据用 InfluxDB/TimescaleDB。
- 网络抖动时 Redis 操作超时，需设合理的 `socket_timeout` 并做降级处理（读本地缓存）。


---


### Q8: 🟡 Redis 事务（MULTI/EXEC）和 Lua 脚本的区别？


A: 结论：MULTI/EXEC 提供命令批量执行但不支持条件判断；Lua 脚本原子执行且支持逻辑。


详细解释：


- **MULTI/EXEC**：


```


MULTI


INCR counter


SET last_update "2026-04-19"


EXEC


```


命令入队后一次性执行，期间其他客户端命令不会插入。但命令语法错误会导致整批失败，运行时错误（如对 String 执行 LPUSH）不会回滚。


- **Lua 脚本**（`EVAL`）：


```lua


-- 原子性 CAS 操作


local current = redis.call('GET', KEYS[1])


if current == ARGV[1] then


redis.call('SET', KEYS[1], ARGV[2])


return 1


end


return 0


```


`EVAL script numkeys key [key...] arg [arg...]`，脚本执行期间 Redis 单线程不处理其他命令，真正原子。


常见坑/追问：


- Lua 脚本执行时间过长会阻塞 Redis，避免在脚本中做复杂计算。
- `WATCH` + `MULTI/EXEC` 实现乐观锁：WATCH 监视键，若执行前键被修改则 EXEC 返回 nil。


---


### Q9: ⭐🔴 如何用 Redis 实现分布式锁？


A: 结论：用 `SET key value NX EX ttl` 实现简单分布式锁，Redlock 算法用于高可用场景。


详细解释：


```cpp
#include <sw/redis++/redis++.h>
#include <uuid/uuid.h>  // 或用随机字符串

class DistributedLock {
    sw::redis::Redis& redis_;
    std::string key_;
    std::string token_;  // 唯一标识，防止误删他人的锁

public:
    DistributedLock(sw::redis::Redis& r, const std::string& resource)
        : redis_(r), key_("lock:" + resource) {
        // 生成唯一 token
        token_ = std::to_string(std::chrono::steady_clock::now()
                                    .time_since_epoch().count());
    }

    // 尝试加锁，ttl 毫秒
    bool tryLock(int ttl_ms = 5000) {
        return redis_.set(key_, token_,
                          std::chrono::milliseconds(ttl_ms),
                          sw::redis::UpdateType::NOT_EXIST);
    }

    // 释放锁（Lua 脚本保证原子性）
    void unlock() {
        auto script = R"(
            if redis.call('GET', KEYS[1]) == ARGV[1] then
                return redis.call('DEL', KEYS[1])
            else
                return 0
            end
        )";
        redis_.eval<long long>(script, {key_}, {token_});
    }
};
```


常见坑/追问：


- 必须用唯一 token：防止锁超时后被其他进程获取，原持有者误删新锁。
- TTL 要大于业务执行时间，否则锁自动过期导致并发问题。
- Redlock：在 N 个独立 Redis 节点上加锁，超过半数成功才算获锁，防单点故障。


---


### Q10: 🟡 Redis 主从复制和哨兵模式的工作原理？


A: 结论：主从复制实现数据冗余，哨兵模式在主节点故障时自动完成故障转移。


详细解释：


- **主从复制**：
- 从节点 `REPLICAOF master_ip port`，首次全量同步（RDB），后续增量同步（命令流）。
- 主节点写，从节点只读，读写分离减轻主节点压力。
- **哨兵模式**（Sentinel）：
- 多个 Sentinel 进程监控主从节点，通过心跳检测故障。
- 主观下线（单个 Sentinel 认为主节点不可达）→ 客观下线（多数 Sentinel 确认）→ 选举 Leader Sentinel → 从节点晋升为主节点 → 通知客户端更新连接。
- **C++ 客户端高可用**：redis-plus-plus 支持 Sentinel 模式：


```cpp


SentinelOptions sentinel_opts;


sentinel_opts.nodes = {{"127.0.0.1", 26379}, {"127.0.0.1", 26380}};


auto sentinel = std::make_shared<Sentinel>(sentinel_opts);


Redis redis(sentinel, "mymaster", Role::MASTER);


```


常见坑/追问：


- 哨兵模式不解决写扩展问题，写仍然只有主节点；水平扩展用 Redis Cluster。
- 故障转移期间（通常几秒）写操作会失败，客户端需做重试。


---
