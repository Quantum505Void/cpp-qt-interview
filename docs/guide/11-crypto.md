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
