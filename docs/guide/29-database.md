# 29. 数据库基础


↑ 回到目录


### Q1: ⭐🟢 ACID 分别代表什么？


A: 结论：ACID 是事务四大特性：原子性、一致性、隔离性、持久性。


详细解释：


- 原子性：事务要么全成功，要么全失败。
- 一致性：事务前后数据满足约束。
- 隔离性：并发事务互不干扰到规定级别。
- 持久性：提交后结果不丢。


常见坑/追问：


- 一致性不是数据库单方面保证，应用逻辑也有责任。


### Q2: ⭐🟢 B+ 树为什么适合数据库索引？


A: 结论：B+ 树层高低、磁盘/页访问友好、范围查询高效，叶子节点有序链表特性特别适合数据库索引。


详细解释：


- 非叶子节点只存键，分支更多，树更矮。
- 叶子节点顺序连接，便于范围扫描。
- 它本质是在减少磁盘/页 IO 次数。


常见坑/追问：


- 追问：为什么不是红黑树？因为数据库更关心页 IO 和范围扫描，不是内存指针结构。


### Q3: ⭐🟡 聚簇索引和非聚簇索引怎么理解？


A: 结论：聚簇索引决定数据物理组织方式；非聚簇索引存的是索引键 + 定位信息，查数据可能需要回表。


详细解释：


- InnoDB 主键索引是聚簇索引。
- 二级索引命中后通常再按主键回表取完整行。
- 这也是“覆盖索引”优化的重要背景。


常见坑/追问：


- 主键过大时，所有二级索引都会更胖。


### Q4: ⭐🟡 什么是覆盖索引？为什么它快？


A: 结论：查询所需字段全部都在索引里，无需回表，这就叫覆盖索引，通常能显著减少 IO。


详细解释：


- `select a,b from t where a=?` 若索引正好覆盖 `a,b`，就不用再访问主数据页。
- 高频读场景优化价值很大。


常见坑/追问：


- 不要为了覆盖索引无脑堆很多列，索引太宽会拖慢写入。


### Q5: 🟡 常见事务隔离级别有哪些？


A: 结论：常见有读未提交、读已提交、可重复读、串行化，隔离越强，通常并发代价越高。


详细解释：


- 读未提交可能脏读。
- 读已提交避免脏读，但可能不可重复读。
- 可重复读进一步加强，但实现细节依赖数据库。
- 串行化最强但并发最差。


常见坑/追问：


- MySQL InnoDB 的可重复读配合 MVCC 和 gap lock，有自己的实现特点。


### Q6: 🟡 为什么索引不是越多越好？


A: 结论：索引能加速查询，但会增加写入成本、存储开销和维护成本，过多索引会拖慢插入更新删除。


详细解释：


- 每次写入都可能要更新多个索引结构。
- 索引设计应围绕主要查询模式。


常见坑/追问：


- 复合索引要考虑最左前缀原则和查询实际顺序。


### Q7: 🔴 MVCC 是什么？它解决了什么问题？


A: 结论：MVCC（多版本并发控制）通过保存数据版本，让读操作尽量不阻塞写、写尽量不阻塞读，从而提升并发性能。


详细解释：


- 事务读取的是符合其视图版本的数据。
- 这是很多数据库实现读已提交/可重复读的重要基础。


常见坑/追问：


- MVCC 不是银弹，仍需配合锁解决写写冲突和幻读等问题。


### Q8: 🔴 上位机项目里的数据库设计常见踩坑有哪些？


A: 结论：最常见的问题是把数据库当日志文件乱塞、缺少索引、时间字段/状态字段设计混乱、归档策略缺失，导致查询和维护双双崩盘。


详细解释：


- 设备数据常增长很快，要预留分表/归档策略。
- 采样点、报警表、操作日志表通常访问模式不同，别混成一锅粥。
- Qt 项目里若主线程直接查大表，也会拖慢 UI。


常见坑/追问：


- 面试时能结合“历史数据归档 + 热冷分离”会更像做过项目的人。


### Q9: ⭐🟡 事务隔离级别有哪四种？各自解决了什么问题？


A: 结论：读未提交、读已提交、可重复读、串行化，隔离级别越高并发能力越低，需要根据业务一致性要求权衡选择。


详细解释：


- 读未提交（Read Uncommitted）：能读到未提交数据，存在脏读。
- 读已提交（Read Committed）：解决脏读，但存在不可重复读（同一事务两次读值不同）。
- 可重复读（Repeatable Read）：解决不可重复读，MySQL InnoDB 默认级别，通过 MVCC + Gap Lock 避免大部分幻读。
- 串行化（Serializable）：完全串行，最安全但最慢。


常见坑/追问：


- 追问：MySQL 默认级别是可重复读，PostgreSQL 默认是读已提交，两者行为有差异。
- 追问：幻读和不可重复读的区别？前者是行数变化，后者是同一行数据变化。


### Q10: ⭐🟡 索引失效的常见场景有哪些？


A: 结论：隐式类型转换、在索引列上使用函数/运算、不符合最左前缀原则、LIKE 以 % 开头、OR 条件不当，都会导致索引失效走全表扫描。


详细解释：


- `WHERE YEAR(create_time) = 2024`：对列用函数，索引失效，应改为范围查询。
- `WHERE id + 1 = 10`：对列做运算，失效，改为 `WHERE id = 9`。
- `WHERE name LIKE '%abc'`：前缀通配符，失效；`LIKE 'abc%'` 可用索引。
- 复合索引 `(a, b, c)`：查询只用 `b`/`c` 跳过 `a`，最左前缀不满足，失效。
- 数字列与字符串比较：`WHERE phone = 13800000000`（phone 为 varchar），隐式转换导致失效。


代码示例：


```sql
-- 失效
SELECT * FROM t WHERE YEAR(created_at) = 2024;
-- 正确
SELECT * FROM t WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';
```


常见坑/追问：


- `EXPLAIN` 查执行计划是排查索引失效的标准手段，面试时提到它会加分。


### Q11: ⭐🟡 什么是 N+1 查询问题？如何避免？


A: 结论：N+1 查询指先查出 N 条主记录，再对每条记录各发一次子查询，总计发出 N+1 次 SQL，性能极差，应用 JOIN 或批量查询优化。


详细解释：


- 典型场景：查出 100 个设备，再用循环逐个查每台设备的报警记录。
- 优化方案：用 `WHERE device_id IN (...)` 一次批量查，或用 JOIN 合并查询。
- ORM 中常见：Hibernate 的 LazyLoad、Qt 里手写循环查数据库都容易踩。


代码示例：


```sql
-- 错误：N+1
SELECT * FROM devices;  -- 返回 100 条
-- 循环执行 100 次：
SELECT * FROM alarms WHERE device_id = ?;

-- 正确：一次 JOIN
SELECT d.*, a.* FROM devices d
LEFT JOIN alarms a ON a.device_id = d.id;
```


常见坑/追问：


- 追问：批量 IN 查询时，IN 列表过长（如几千个 id）也会有性能问题，可分批处理。


### Q12: 🟡 SQLite 适合哪些场景？在上位机项目里怎么用好它？


A: 结论：SQLite 适合本地嵌入式存储，零部署、单文件、支持 ACID，上位机项目中常用于设备配置、历史数据、操作日志本地持久化。


详细解释：


- 优点：零配置、单文件便于部署和备份、支持全文 SQL、跨平台。
- 缺点：写并发差（WAL 模式改善），不适合高吞吐多写场景。
- WAL 模式：`PRAGMA journal_mode=WAL;` 开启后，读写并发性明显提升。
- Qt 的 `QSqlDatabase` 原生支持 SQLite，开箱即用。


代码示例：


```cpp
QSqlDatabase db = QSqlDatabase::addDatabase("QSQLITE");
db.setDatabaseName("data.db");
db.open();
QSqlQuery q;
q.exec("PRAGMA journal_mode=WAL");
q.exec("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, ts INTEGER, val REAL)");
```


常见坑/追问：


- 多线程写 SQLite：每个线程需要独立 connection，不能共享同一 QSqlDatabase 对象。
- 数据库文件较大时定期 `VACUUM` 回收空间。


### Q13: 🟡 数据库连接池的作用是什么？如何在上位机 Qt 项目里实现简单的连接复用？


A: 结论：建立 TCP 连接开销大，连接池预先创建并维护一批可复用的连接，减少每次请求的建连/断连开销。


详细解释：


- 上位机若连接 MySQL/PostgreSQL 远程数据库，频繁 open/close 会拖慢 UI。
- 简单方案：Qt 多个 `QSqlDatabase` 命名连接，按业务功能分配复用。
- 完整方案：维护空闲队列，取出时标记占用，用完归还，加超时与健康检查。


代码示例：


```cpp
// 初始化命名连接（只做一次）
auto db = QSqlDatabase::addDatabase("QMYSQL", "conn_1");
db.setHostName("127.0.0.1");
db.setDatabaseName("mydb");
db.open();

// 使用时直接取
QSqlDatabase conn = QSqlDatabase::database("conn_1");
QSqlQuery q(conn);
q.exec("SELECT ...");
```


常见坑/追问：


- 追问：连接长时间不用可能被服务器断开，需要定期发 ping 或捕获错误后重连。


### Q14: ⭐🔴 如何为上位机设计历史数据归档策略？


A: 结论：区分热数据（近期高频查询）和冷数据（历史归档），热表保留最近 N 天/N 条，定期将超期数据迁移到归档表或导出文件，并配合索引和分区表提升查询性能。


详细解释：


- 采样数据表按天/设备分表，避免单表膨胀到千万行。
- 归档策略：定时任务将 30 天前数据 INSERT INTO archive_table + DELETE FROM hot_table。
- 若用 SQLite，可按月创建新库文件，历史查询路由到对应文件。
- Qt 项目中可用 `QTimer` 触发归档任务，在后台线程执行。


代码示例：


```sql
-- 定时归档 SQL
INSERT INTO records_archive SELECT * FROM records WHERE ts < strftime('%s', 'now', '-30 days');
DELETE FROM records WHERE ts < strftime('%s', 'now', '-30 days');
```


常见坑/追问：


- 归档和查询可能并发，需要事务保证一致性。
- 追问：如何支持跨归档时间范围的历史查询？需要统一查询路由层。


### Q15: ⭐🔴 如何在 Qt 中安全地在子线程操作数据库并更新 UI？


A: 结论：数据库操作放到专用工作线程（`QThread` 或线程池），通过信号槽将结果传回主线程更新 UI，绝不在主线程做耗时查询。


详细解释：


- `QSqlDatabase` 连接不能跨线程共享，工作线程需创建自己命名的连接。
- 工作线程完成查询后，通过信号将数据（QList、struct 等）发射到主线程的槽函数刷新 UI。
- 使用 `Qt::QueuedConnection` 保证跨线程安全投递。


代码示例：


```cpp
// 工作线程
class DbWorker : public QObject {
    Q_OBJECT
public slots:
    void query() {
        auto db = QSqlDatabase::addDatabase("QSQLITE", "worker_conn");
        db.setDatabaseName("data.db");
        db.open();
        QSqlQuery q(db);
        q.exec("SELECT * FROM records LIMIT 100");
        QList<Record> result;
        while (q.next()) result.append({q.value(0).toInt(), q.value(1).toReal()});
        emit done(result);
    }
signals:
    void done(QList<Record>);
};
```


常见坑/追问：


- 不要在主线程槽里直接打开 QSqlDatabase，UI 卡顿的主要来源之一。
- 追问：`QSqlDatabase::removeDatabase` 要在对应线程销毁连接，否则有资源泄漏警告。
