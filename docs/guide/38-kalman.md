# 38. 卡尔曼滤波


↑ 回到目录


### Q1: ⭐🟡 卡尔曼滤波的基本原理是什么？


A: 结论：卡尔曼滤波通过预测-更新两步循环，融合系统模型和带噪声的观测，得到最优状态估计。


详细解释：


- **核心思想**：在线性高斯系统中，卡尔曼滤波给出均方误差意义下的最优估计（MMSE）。
- **两步循环**：
- **预测步**（时间更新）：根据上一时刻状态和系统模型，预测当前状态和误差协方差。
- **更新步**（测量更新）：用当前观测值修正预测，计算卡尔曼增益，更新状态估计。
- **关键变量**：
- `x̂`：状态估计向量
- `P`：估计误差协方差矩阵
- `K`：卡尔曼增益（决定信任模型还是观测）
- `Q`：过程噪声协方差（系统模型不确定性）
- `R`：观测噪声协方差（传感器噪声）


常见坑/追问：


- Q 大 → 更信任观测，响应快但噪声大；R 大 → 更信任模型，平滑但响应慢。
- 卡尔曼滤波假设噪声是高斯白噪声，实际传感器若有偏置需先标定。


---


### Q2: ⭐🟡 卡尔曼滤波的状态方程和观测方程是什么？


A: 结论：状态方程描述系统动态演化，观测方程描述传感器如何观测状态。


详细解释：


- **状态方程（过程模型）**：


```


x_k = F * x_{k-1} + B * u_k + w_k


```


- `F`：状态转移矩阵（系统动力学）
- `B`：控制输入矩阵，`u_k`：控制输入
- `w_k ~ N(0, Q)`：过程噪声
- **观测方程（测量模型）**：


```


z_k = H * x_k + v_k


```


- `H`：观测矩阵（状态到观测的映射）
- `v_k ~ N(0, R)`：观测噪声
- **预测步**：


```


x̂_k|k-1 = F * x̂_{k-1|k-1}


P_k|k-1  = F * P_{k-1|k-1} * F^T + Q


```


- **更新步**：


```


K_k = P_k|k-1 * H^T * (H * P_k|k-1 * H^T + R)^{-1}


x̂_k|k = x̂_k|k-1 + K_k * (z_k - H * x̂_k|k-1)


P_k|k  = (I - K_k * H) * P_k|k-1


```


常见坑/追问：


- 创新量 `z_k - H * x̂_k|k-1` 称为"残差"，若残差持续偏大说明模型或噪声参数设置有问题。
- `(I - KH)` 的数值稳定形式：`P = (I-KH)P(I-KH)^T + KR*K^T`（Joseph 形式）。


---


### Q3: ⭐🔴 用 C++ 和 Eigen 实现一维卡尔曼滤波？


A: 结论：Eigen 提供高效矩阵运算，是 C++ 实现卡尔曼滤波的标准选择。


详细解释：


```cpp
#include <Eigen/Dense>
#include <vector>

class KalmanFilter1D {
public:
    // 状态：[位置, 速度]
    Eigen::Vector2d x;   // 状态估计
    Eigen::Matrix2d P;   // 误差协方差
    Eigen::Matrix2d F;   // 状态转移矩阵
    Eigen::Matrix2d Q;   // 过程噪声
    Eigen::RowVector2d H; // 观测矩阵（只观测位置）
    double R;             // 观测噪声方差

    KalmanFilter1D(double dt, double process_noise, double meas_noise) {
        x = Eigen::Vector2d::Zero();
        P = Eigen::Matrix2d::Identity() * 1000.0;  // 初始不确定性大

        // 匀速运动模型
        F << 1, dt,
             0,  1;

        // 过程噪声（加速度不确定性）
        double q = process_noise;
        Q << q*dt*dt*dt/3, q*dt*dt/2,
             q*dt*dt/2,    q*dt;

        H << 1, 0;  // 只观测位置
        R = meas_noise * meas_noise;
    }

    void predict() {
        x = F * x;
        P = F * P * F.transpose() + Q;
    }

    void update(double measurement) {
        double S = H * P * H.transpose() + R;
        Eigen::Vector2d K = P * H.transpose() / S;
        x = x + K * (measurement - H * x);
        P = (Eigen::Matrix2d::Identity() - K * H) * P;
    }

    double position() const { return x(0); }
    double velocity() const { return x(1); }
};

// 使用示例
int main() {
    KalmanFilter1D kf(0.1, 0.1, 2.0);  // dt=0.1s, 过程噪声=0.1, 测量噪声=2m
    std::vector<double> measurements = {1.2, 2.1, 2.9, 4.1, 5.0};
    for (double z : measurements) {
        kf.predict();
        kf.update(z);
        printf("pos=%.3f vel=%.3f\n", kf.position(), kf.velocity());
    }
}
```


常见坑/追问：


- Eigen 矩阵默认列主序，与数学公式一致，不需要转置。
- 初始 P 设大一点（如 1000*I）表示初始状态不确定，滤波器会快速收敛。


---


### Q4: 🟡 Q 和 R 矩阵如何调参？


A: 结论：Q 反映模型不确定性，R 反映传感器噪声，通过实验数据统计或经验调整。


详细解释：


- **R 的确定**：相对容易，对传感器静止时采集一段数据，计算方差即为 R。


```cpp


// 传感器静止时采集 N 个样本


double mean = 0, var = 0;


for (auto v : samples) mean += v;


mean /= samples.size();


for (auto v : samples) var += (v-mean)*(v-mean);


double R = var / (samples.size() - 1);


```


- **Q 的调整原则**：
- Q 太小：滤波器过于相信模型，对突变响应慢（滞后）
- Q 太大：滤波器过于相信观测，输出噪声大
- 经验法：从 `Q = 0.01*R` 开始，观察残差序列是否白噪声
- **自适应卡尔曼**：在线估计 Q/R，适合噪声特性变化的场景（如 GPS 信号质量变化）。


常见坑/追问：


- 调参时画出：原始测量值、滤波输出、真实值（如有）三条曲线对比。
- 残差（新息）应该是零均值白噪声，若有自相关说明模型不匹配。


---


### Q5: ⭐🔴 扩展卡尔曼滤波（EKF）解决什么问题，原理是什么？


A: 结论：EKF 通过一阶泰勒展开将非线性系统线性化，使卡尔曼滤波适用于非线性场景。


详细解释：


- **问题**：标准卡尔曼滤波要求 F 和 H 是线性矩阵，但实际系统（如 GPS 坐标转换、IMU 积分）是非线性的。
- **EKF 方法**：在当前估计点对非线性函数求雅可比矩阵（Jacobian），用雅可比代替线性矩阵。


```


非线性系统：


x_k = f(x_{k-1}, u_k) + w_k


z_k = h(x_k) + v_k


EKF 线性化：


F_k = ∂f/∂x |_{x̂_{k-1}}  (雅可比矩阵)


H_k = ∂h/∂x |_{x̂_k|k-1}


预测步：


x̂_k|k-1 = f(x̂_{k-1|k-1}, u_k)


P_k|k-1  = F_k * P_{k-1|k-1} * F_k^T + Q


更新步（同标准 KF，用 H_k 代替 H）


```


- **C++ 实现要点**：需要手动推导并实现雅可比矩阵的计算函数。


常见坑/追问：


- EKF 在强非线性或初始误差大时可能发散，此时考虑 UKF（无迹卡尔曼滤波）。
- 雅可比矩阵推导容易出错，可用数值微分验证：`(f(x+ε) - f(x-ε)) / (2ε)`。


---


### Q6: 🟡 卡尔曼滤波在 GPS 轨迹平滑中如何应用？


A: 结论：用匀速或匀加速运动模型作为过程模型，GPS 坐标作为观测，滤除定位噪声。


详细解释：


```cpp
// GPS 轨迹平滑：状态 [lat, lon, vLat, vLon]
class GPSKalmanFilter {
    Eigen::Vector4d x;
    Eigen::Matrix4d P, F, Q;
    Eigen::Matrix<double,2,4> H;
    Eigen::Matrix2d R;
public:
    GPSKalmanFilter(double dt) {
        x.setZero();
        P = Eigen::Matrix4d::Identity() * 100.0;

        // 匀速模型
        F << 1, 0, dt, 0,
             0, 1, 0, dt,
             0, 0, 1,  0,
             0, 0, 0,  1;

        // 只观测位置
        H << 1, 0, 0, 0,
             0, 1, 0, 0;

        // GPS 精度约 5m，转换为度：5/111000 ≈ 4.5e-5
        double gps_noise = 4.5e-5;
        R = Eigen::Matrix2d::Identity() * gps_noise * gps_noise;

        double q = 1e-5;
        Q = Eigen::Matrix4d::Identity() * q;
    }

    Eigen::Vector2d update(double lat, double lon) {
        // 预测
        x = F * x;
        P = F * P * F.transpose() + Q;
        // 更新
        Eigen::Vector2d z(lat, lon);
        Eigen::Matrix2d S = H * P * H.transpose() + R;
        Eigen::Matrix<double,4,2> K = P * H.transpose() * S.inverse();
        x = x + K * (z - H * x);
        P = (Eigen::Matrix4d::Identity() - K * H) * P;
        return Eigen::Vector2d(x(0), x(1));
    }
};
```


常见坑/追问：


- GPS 坐标直接用经纬度（度）计算时，经度和纬度的物理距离不等，精确应用需转换到 UTM 坐标系。
- 车辆停止时速度应接近 0，可加速度约束或检测静止状态后重置速度分量。


---


### Q7: 🟡 卡尔曼滤波与低通滤波、移动平均的区别？


A: 结论：卡尔曼滤波利用系统模型动态调整权重，比固定权重的低通滤波更优。


详细解释：


- **移动平均**：等权重平均最近 N 个样本，简单但有固定延迟，无法利用运动模型。
- **低通滤波（一阶 IIR）**：`y = αy_prev + (1-α)x`，固定权重，不随信噪比变化。
- **卡尔曼滤波**：
- 权重（卡尔曼增益 K）根据当前不确定性动态计算
- 利用运动模型预测，在无观测时也能估计状态
- 多传感器融合时自然扩展（扩展观测矩阵 H）
- **选择建议**：
- 简单去噪、无模型：低通滤波
- 有运动模型、需要速度估计：卡尔曼滤波
- 非线性系统：EKF/UKF


常见坑/追问：


- 卡尔曼滤波计算量更大，嵌入式资源受限时可用简化版（标量卡尔曼）。
- Qt 中实时显示滤波结果：在数据接收槽函数中调用 `kf.update()`，更新图表。


---


### Q8: 🔴 多传感器融合时卡尔曼滤波如何扩展？


A: 结论：扩展观测矩阵 H 和噪声矩阵 R，或用序贯更新分别处理每个传感器。


详细解释：


- **方法一：联合更新**（同时融合多个传感器）：


```


若有 GPS（观测位置）和加速度计（观测加速度）：


H = [H_gps; H_acc]  (垂直拼接)


R = diag(R_gps, R_acc)


z = [z_gps; z_acc]


```


- **方法二：序贯更新**（逐个传感器更新，数值更稳定）：


```cpp


// 先用 GPS 更新


kf.update(z_gps, H_gps, R_gps);


// 再用 IMU 更新（使用上一步更新后的 P）


kf.update(z_imu, H_imu, R_imu);


```


- **异步传感器**：不同传感器采样率不同，低频传感器（GPS 1Hz）只在有数据时做更新步，高频传感器（IMU 100Hz）每步都更新。


常见坑/追问：


- 传感器时间戳对齐很重要，时间不同步会引入系统误差。
- Qt 中多传感器数据通过不同信号槽接收，在同一个 QObject 中串行处理保证线程安全。


---
