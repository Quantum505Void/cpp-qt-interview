# 11. C++ 加密体系


↑ 回到目录


### Q1: ⭐🟢 对称加密和非对称加密的核心区别是什么？


A: 结论：对称加密使用同一把密钥做加解密，速度快；非对称加密使用公钥/私钥对，便于密钥分发但速度慢。工程上通常是“非对称交换密钥 + 对称加密传数据”。


详细解释：


- 对称加密常见算法：AES、SM4、ChaCha20。
- 非对称加密常见算法：RSA、ECC、SM2。
- TLS/HTTPS 里通常不会直接用 RSA 加密大量业务数据，而是通过 ECDHE/RSA 完成密钥协商，再用 AES-GCM 或 ChaCha20-Poly1305 传输数据。
- 面试里要说清：对称加密强在性能，非对称加密强在密钥管理。


代码示例：


```cpp
// 伪代码：真实项目通常用 OpenSSL / Botan / Crypto++
std::vector<unsigned char> cipher = AES_Encrypt(plain, key, iv);
std::vector<unsigned char> plain2 = AES_Decrypt(cipher, key, iv);
```


常见坑/追问：


- 不要说“RSA 比 AES 更安全所以都用 RSA”，这是典型误区。
- 追问常见：为什么非对称加密慢？因为大整数运算开销更高。


### Q2: ⭐🟡 哈希（Hash）和加密（Encryption）有什么区别？


A: 结论：哈希是单向摘要，目标是校验完整性和快速比对；加密是可逆变换，目标是保密。二者解决的问题完全不同。


详细解释：


- 哈希常见算法：SHA-256、SHA-3、SM3。
- 加密常见算法：AES、RSA、SM4。
- 哈希不能“解密”回原文，理论上只能重新计算比对。
- 密码存储通常不是“加密后入库”，而是加盐哈希（salt + hash），否则一旦密钥泄露会整体失守。


代码示例：


```cpp
std::string digest = SHA256("hello");
bool ok = (digest == SHA256("hello"));
```


常见坑/追问：


- MD5/SHA1 现在不适合安全敏感场景。
- 追问：文件完整性校验为什么常用哈希而不是加密？因为不需要可逆，只需要检测篡改。


### Q3: ⭐🟡 什么是数字签名？它和“加密”是什么关系？


A: 结论：数字签名是“用私钥对摘要签名，用公钥验签”，目标是证明消息来源和完整性，不是保密。它和加密经常一起出现，但语义不同。


详细解释：


- 发送方先对消息做哈希，再用私钥对摘要签名。
- 接收方用公钥验签，并重新计算消息摘要比对。
- 数字签名提供：身份认证、完整性、不可否认性。
- 如果还要保密，就需要再叠加加密。


代码示例：


```cpp
// 伪代码
auto digest = SHA256(message);
auto sign = RSA_Sign(privateKey, digest);
bool ok = RSA_Verify(publicKey, SHA256(message), sign);
```


常见坑/追问：


- “私钥加密、公钥解密”这句话只能粗略类比签名过程，严格说签名和加密不是同一个算法流程。
- 追问：为什么签名通常签摘要不签原文？因为效率更高，而且签名算法输入长度常有限制。


### Q4: ⭐🟡 AES 的 ECB、CBC、CTR、GCM 有什么区别？


A: 结论：ECB 不安全；CBC 需要 IV 且只保密不认证；CTR 把分组算法变成流模式；GCM 同时提供保密性和完整性，现代网络协议里很常见。


详细解释：


- ECB：相同明文块得到相同密文块，模式泄露明显，几乎不应使用。
- CBC：每块依赖前一块，IV 必须随机且不可复用。
- CTR：通过计数器生成密钥流，支持并行，IV/nonce 绝不能重复。
- GCM：在 CTR 基础上加 GHASH 认证，属于 AEAD 模式。
- 工程上优先选 GCM 或 ChaCha20-Poly1305 这类 AEAD。


代码示例：


```cpp
// OpenSSL 里常见的是 EVP 接口，示意：
// EVP_aes_256_gcm()
```


常见坑/追问：


- IV/nonce 重复是灾难性错误，尤其是 CTR/GCM。
- 追问：为什么 GCM 比 CBC 更常见？因为它同时解决加密和认证问题。


### Q5: 🟢 什么是 IV、nonce、salt？三者不要混。


A: 结论：IV/nonce 主要用于加密过程避免模式重复，salt 主要用于哈希场景抵御彩虹表。它们都像“随机值”，但用途不同。


详细解释：


- IV（Initialization Vector）：常见于 CBC、CFB 等模式。
- nonce：常见于 CTR、GCM、ChaCha20，一般要求唯一而非绝对随机。
- salt：用于密码哈希，确保相同密码不会产生相同摘要。
- 它们通常不需要保密，但必须正确生成和管理。


代码示例：


```cpp
auto salt = RandomBytes(16);
auto hash = PBKDF2(password, salt, 100000);
```


常见坑/追问：


- 不要把 salt 当作“密钥”。
- 不要把固定 IV 写死到代码里。


### Q6: ⭐🟡 什么是 HMAC？它和普通 Hash 的差别是什么？


A: 结论：HMAC 是“带密钥的哈希”，用于消息认证；普通 Hash 只能做摘要，不能证明消息来自谁。HMAC 解决的是完整性 + 身份确认问题。


详细解释：


- HMAC = Hash(key ⊕ opad, Hash(key ⊕ ipad, message)) 的结构。
- 常见组合有 HMAC-SHA256。
- 即使攻击者知道消息内容，没有密钥也无法伪造正确 HMAC。
- 在 API 签名、Webhook 校验、设备报文认证里都很常见。


代码示例：


```cpp
std::string mac = HMAC_SHA256(secret, payload);
bool ok = (mac == HMAC_SHA256(secret, payload));
```


常见坑/追问：


- 不要直接拼接 `hash(key + msg)` 代替 HMAC，可能有长度扩展等问题。
- 比较 HMAC 时最好用常量时间比较。


### Q7: ⭐🟡 TLS 握手过程大致做了什么？


A: 结论：TLS 握手主要完成三件事：协商算法、验证证书、建立会话密钥。之后业务数据通常走对称加密。


详细解释：


- ClientHello：客户端发支持的版本、cipher suites、随机数。
- ServerHello：服务端选择参数并返回证书。
- 客户端验证证书链、域名、有效期。
- 双方通过 ECDHE 等方式协商共享密钥。
- 握手完成后，用会话密钥做对称加密传输。


代码示例：


```cpp
// Qt 中可通过 QSslSocket 使用 TLS
QSslSocket socket;
socket.connectToHostEncrypted("example.com", 443);
```


常见坑/追问：


- “用了 HTTPS 就绝对安全”是错的，证书校验、主机名校验、过期证书处理都可能出问题。
- 追问：为什么 TLS 1.3 更快？因为减少了握手轮次。


### Q8: 🟡 证书链校验时主要校验什么？


A: 结论：证书链校验至少要看签发链是否可信、证书是否过期、域名是否匹配、是否被吊销。核心是“这个公钥到底能不能信”。


详细解释：


- 从服务器证书一路校验到受信任根证书。
- 检查 Not Before / Not After。
- 检查 Subject Alternative Name 中域名是否匹配。
- 有条件时检查 CRL 或 OCSP 吊销状态。
- 自签证书不是不能用，但默认不被系统信任。


常见坑/追问：


- 开发时为了省事“忽略 SSL 错误”是非常危险的坏习惯。
- 面试官常追问：证书和公钥是什么关系？证书本质上是对公钥和身份信息的签名封装。


### Q9: 🟡 OpenSSL 在 C++ 项目里通常怎么用？


A: 结论：现代项目里建议走 OpenSSL EVP 高层接口，而不是直接操作底层算法细节。这样更统一、更易替换，也更不容易踩坑。


详细解释：


- EVP 封装了加密、摘要、签名等统一接口。
- 优点是算法切换方便，例如 SHA256 换成 SM3 时调用层变化较小。
- C++ 中通常还要自己封装 RAII，避免 `EVP_PKEY_free`、`EVP_MD_CTX_free` 漏掉。


代码示例：


```cpp
// 伪代码
EVP_MD_CTX* ctx = EVP_MD_CTX_new();
EVP_DigestInit_ex(ctx, EVP_sha256(), nullptr);
EVP_DigestUpdate(ctx, data.data(), data.size());
EVP_DigestFinal_ex(ctx, out, &len);
EVP_MD_CTX_free(ctx);
```


常见坑/追问：


- OpenSSL 是 C 风格接口，异常安全和资源释放需要自己兜住。
- 追问：为什么建议封装成 RAII 类？因为失败路径很多，手工释放易泄漏。


### Q10: ⭐🔴 密码存储为什么不能直接 SHA256(password)？


A: 结论：因为太快，而且无 salt，容易被彩虹表和 GPU 暴力破解。密码存储应该使用专门的 password hashing 算法，如 bcrypt、scrypt、Argon2，至少也要 PBKDF2 + salt。


详细解释：


- 快速哈希适合文件摘要，不适合密码学意义上的口令防护。
- 攻击者拿到数据库后，可以对海量常见密码并行计算。
- salt 解决同密码同摘要的问题。
- cost/work factor 解决“太快”的问题。


代码示例：


```cpp
// 伪代码
auto salt = RandomBytes(16);
auto hash = Argon2(password, salt, /*memoryCost*/65536, /*timeCost*/3);
```


常见坑/追问：


- “数据库不出网所以明文/快哈希也行”是典型事故前夜发言。
- 追问：登录时怎么验证？重新用同样参数计算并比对结果。


### Q11: ⭐🟡 数字签名和消息认证码（HMAC）有什么区别？


A: 结论：HMAC 是对称的（双方共享密钥），只能验证消息完整性和来源，不能证明是"谁"发的（因为双方都有密钥）；数字签名是非对称的（私钥签名，公钥验证），可实现不可否认性。


详细解释：


- HMAC：`HMAC(key, message)` → MAC 值，接收方用相同 key 验证，适合服务内部通信。
- 数字签名：发送方用私钥签名，任何人用公钥验证，适合证书、代码签名等公开场景。
- HMAC 性能优于数字签名（对称 vs 非对称）。
- 不可否认性：HMAC 无法区分是 A 发的还是 B 发的（双方都有 key）；数字签名私钥唯一，具有不可否认性。


代码示例：


```cpp
// OpenSSL HMAC-SHA256
unsigned char result[EVP_MAX_MD_SIZE];
unsigned int len;
HMAC(EVP_sha256(), key, key_len, msg, msg_len, result, &len);
```


常见坑/追问：


- HMAC 密钥泄漏 = 完全失效；数字签名私钥泄漏 = 完全失效，但公钥可以自由分发。
- 追问：JWT 用哪种？HS256 用 HMAC，RS256 用 RSA 数字签名，ES256 用 ECDSA。


---


### Q12: ⭐🔴 TLS 握手过程是什么？C++ 程序如何使用 TLS？


A: 结论：TLS 握手包括协商密码套件、交换证书、验证身份、协商会话密钥几个阶段；C++ 通过 OpenSSL 的 `SSL_CTX`/`SSL` API 或 Qt 的 `QSslSocket` 使用 TLS。


详细解释：


- TLS 1.3 握手（简化）：ClientHello → ServerHello + Certificate + CertificateVerify → Finished → 开始加密通信。
- 证书验证：客户端验证服务器证书链直到可信根 CA。
- 会话密钥：使用 ECDHE 密钥交换，每次连接生成新密钥（前向保密）。
- Qt 中：`QSslSocket::connectToHostEncrypted()` 封装了握手过程，`sslErrors` 信号处理证书验证失败。


代码示例：


```cpp
// Qt TLS
QSslSocket* socket = new QSslSocket(this);
connect(socket, &QSslSocket::encrypted, this, &MyClass::onConnected);
connect(socket, QOverload<const QList<QSslError>&>::of(&QSslSocket::sslErrors),
        this, [socket](const QList<QSslError>& errors) {
    // 生产环境不应忽略错误！
    socket->ignoreSslErrors(errors); // 仅测试
});
socket->connectToHostEncrypted("example.com", 443);
```


常见坑/追问：


- `ignoreSslErrors()` 忽略证书错误是严重安全漏洞，生产环境绝不允许。
- 追问：自签名证书如何在 Qt 中使用？手动加载 CA 证书到 `QSslConfiguration::addCaCertificate`。


---


### Q13: ⭐🟡 对称加密中 IV（初始化向量）的作用是什么？


A: 结论：IV 保证相同明文在不同加密调用中产生不同密文，防止攻击者通过密文相同推断明文相同；IV 无需保密，但必须每次随机生成且不可重用。


详细解释：


- 没有 IV（ECB 模式）：相同明文块产生相同密文块，数据模式泄露（著名的 Linux Penguin 图片例子）。
- CBC 模式：IV XOR 明文后再加密，每次不同 IV 产生完全不同的密文链。
- IV 要求：随机（非零、非可预测），每次加密新生成，与密文一起传输给接收方。
- GCM 模式：IV 又称 Nonce，12 字节最优，GCM Nonce 重用会完全破坏安全性（比 CBC 更严格）。


常见坑/追问：


- GCM Nonce 重用是最危险的错误之一，直接泄露认证密钥。
- 追问：IV 和 Salt 的区别？IV 用于加密模式初始化，Salt 用于密钥派生（KDF）或密码哈希，概念不同但目的类似（防重放/防彩虹表）。


---


### Q14: ⭐🔴 如何在 C++ 中安全地存储和使用密钥？


A: 结论：密钥不应硬编码在源码或二进制中；生产环境应使用密钥管理系统（KMS/HSM）、OS 密钥存储（Keychain/DPAPI/Linux Keyring）或环境变量注入，并确保密钥用后及时清零。


详细解释：


- **硬编码密钥**：逆向工程即可提取，是严重安全漏洞。
- **OS 密钥存储**：macOS Keychain、Windows DPAPI/Credential Manager、Linux `libsecret`，API 调用复杂但安全。
- **环境变量**：比硬编码安全，但进程内存仍可读，不适合高安全场景。
- **密钥清零**：用完后用 `OPENSSL_cleanse()` 或 `explicit_bzero()` 清零内存，防止 core dump 泄露。


代码示例：


```cpp
// 密钥清零
std::vector<uint8_t> key(32);
// ... 使用密钥 ...
OPENSSL_cleanse(key.data(), key.size());
// 注意：普通 memset 可能被编译器优化掉！
```


常见坑/追问：


- `memset` 清零可能被优化掉（dead store elimination），必须用 `explicit_bzero`/`OPENSSL_cleanse`。
- 追问：什么是密钥轮换（Key Rotation）？定期更换加密密钥，旧密钥只用于解密历史数据，降低密钥泄露的影响范围。


---


### Q15: ⭐🔴 什么是前向保密（Perfect Forward Secrecy）？为什么重要？


A: 结论：前向保密指即使长期私钥（如服务器证书私钥）泄露，过去的加密通信也无法被解密；实现方式是每次会话使用临时 ECDHE 密钥协商，不使用静态私钥加密会话密钥。


详细解释：


- 无 PFS（如 RSA 密钥交换）：攻击者录制所有加密流量，一旦拿到私钥即可解密全部历史通信。
- 有 PFS（ECDHE）：每次握手生成临时密钥对，会话密钥不依赖服务器私钥，临时密钥用完即丢弃。
- TLS 1.3：强制使用 ECDHE，移除了所有非 PFS 密钥交换算法。
- TLS 1.2：需要显式选择 ECDHE 密码套件（如 `ECDHE-RSA-AES256-GCM-SHA384`）。


常见坑/追问：


- TLS 1.2 中 RSA 密钥交换（`TLS_RSA_WITH_*`）没有 PFS，应从密码套件中移除。
- 追问：PFS 和证书安全性有什么关系？证书用于身份认证，ECDHE 用于密钥协商，两者解决不同问题；PFS 保护通信内容，证书保护身份。
