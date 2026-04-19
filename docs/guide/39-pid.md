# 39. PID 控制算法


↑ 回到目录


### Q1: ⭐🟢 PID 控制的基本原理是什么？


A: 结论：PID 通过比例（P）、积分（I）、微分（D）三项之和计算控制量，消除误差。


详细解释：


- **连续时间 PID 公式**：


```


u(t) = Kp*e(t) + Ki*∫e(τ)dτ + Kd*de(t)/dt


```


- `e(t) = setpoint - measurement`：误差
- **P 项**：比例控制，误差越大控制量越大，有稳态误差
- **I 项**：积分控制，消除稳态误差，但响应慢，可能超调
- **D 项**：微分控制，预测误差变化趋势，抑制超调，对噪声敏感
- **各项作用**：


| 参数 | 增大效果 | 减小效果 |


|------|---------|---------|


| Kp | 响应快，超调增大 | 响应慢，稳态误差大 |


| Ki | 消除稳态误差快 | 积分作用弱 |


| Kd | 抑制超调，稳定性好 | 对噪声敏感 |


常见坑/追问：


- 纯 P 控制有稳态误差（除非系统本身有积分特性）。
- D 项对高频噪声放大，实际使用需加低通滤波。


---


### Q2: ⭐🟡 PID 的离散化实现：位置式和增量式的区别？


A: 结论：位置式输出绝对控制量，增量式输出控制量变化值，增量式更安全。


详细解释：


- **位置式 PID**（输出绝对值）：


```cpp


double compute(double setpoint, double measurement) {


double error = setpoint - measurement;


integral_ += error * dt_;


double derivative = (error - prev_error_) / dt_;


prev_error_ = error;


return Kp_*error + Ki_*integral_ + Kd_*derivative;


}


```


- **增量式 PID**（输出增量 Δu）：


```cpp


double compute(double setpoint, double measurement) {


double error = setpoint - measurement;


double delta_u = Kp_*(error - prev_error_)


+ Ki_*error*dt_


+ Kd_*(error - 2*prev_error_ + prev_prev_error_)/dt_;


prev_prev_error_ = prev_error_;


prev_error_ = error;


return delta_u;  // 调用方：output += delta_u


}


```


- **增量式优点**：
- 无积分累积，切换到手动模式时无扰动
- 执行机构（如步进电机）天然适合增量控制
- 参数变化时平滑过渡


常见坑/追问：


- 位置式需要限制积分累积（抗饱和），增量式需要限制输出累积值的范围。
- 上位机控制阀门/电机：增量式更常用，避免突变。


---


### Q3: ⭐🟡 积分饱和问题及抗饱和方法？


A: 结论：积分饱和指执行机构达到极限时积分项继续累积，导致超调严重，需用限幅或条件积分解决。


详细解释：


- **问题**：当输出被限幅（如阀门 0-100%），但误差仍大，积分项持续增大。当误差反向时，需要很长时间才能"消化"积分，导致严重超调。
- **方法一：积分限幅**（最简单）：


```cpp


integral_ += error * dt_;


integral_ = std::clamp(integral_, -integral_limit_, integral_limit_);


```


- **方法二：条件积分（Clamping）**：


```cpp


double output_raw = Kp_*error + Ki_*integral_ + Kd_*derivative;


bool saturated = (output_raw > output_max_ || output_raw < output_min_);


// 只在未饱和，或误差方向与积分方向相反时才积分


if (!saturated || (error * integral_ < 0))


integral_ += error * dt_;


```


- **方法三：Back-calculation（反计算）**：


```cpp


double output_limited = std::clamp(output_raw, output_min_, output_max_);


integral_ += error * dt_ + (output_limited - output_raw) / Ki_ * Kb_;


// Kb_ 为反计算增益，通常 Kb = sqrt(Ki/Kd) 或经验值


```


常见坑/追问：


- 上位机控制加热器：温度超调可能损坏设备，抗饱和是必须实现的功能。
- 方法三（Back-calculation）是工业标准，Simulink 默认使用此方法。


---


### Q4: 🟡 微分项的噪声问题及微分滤波？


A: 结论：微分项放大高频噪声，实际实现需加低通滤波或改用测量值微分。


详细解释：


- **问题**：`de/dt = (e_k - e_{k-1})/dt`，若测量值有噪声，微分项会剧烈抖动。
- **方法一：一阶低通滤波微分**：


```cpp


// 滤波后的微分：D_filtered = α*D_prev + (1-α)*(error-prev_error)/dt


double raw_derivative = (error - prev_error_) / dt_;


filtered_derivative_ = alpha_ * filtered_derivative_ + (1-alpha_) * raw_derivative;


// alpha_ 接近 1 时滤波强，接近 0 时无滤波


```


- **方法二：测量值微分（Derivative on Measurement）**：


```cpp


// 对测量值求微分而非误差，避免设定值阶跃时微分冲击


double derivative = -(measurement - prev_measurement_) / dt_;


prev_measurement_ = measurement;


```


设定值阶跃时，误差微分会产生冲击（"微分踢"），测量值微分可避免。


- **方法三：不完全微分**（传递函数 `s/(Ts+1)`）：


```cpp


// 离散化：d_k = Td/(Td+N*dt) * d_{k-1} + Kd*N/(Td+N*dt) * (e_k - e_{k-1})


// N 为滤波系数，通常 5-20


```


常见坑/追问：


- 工业 PID 标准实现（IEC 61131-3）默认使用测量值微分 + 不完全微分。
- Qt 上位机中，若传感器采样率高（>100Hz），微分滤波尤为重要。


---


### Q5: ⭐🔴 完整的 C++ PID 控制器实现？


A: 结论：工业级 PID 需包含抗饱和、微分滤波、输出限幅、手自动切换。


详细解释：


```cpp
class PIDController {
public:
    struct Config {
        double Kp = 1.0, Ki = 0.0, Kd = 0.0;
        double dt = 0.01;           // 采样周期（秒）
        double output_min = -100.0;
        double output_max =  100.0;
        double integral_limit = 50.0;
        double derivative_filter = 0.1; // 微分低通系数 alpha
    };

    explicit PIDController(const Config& cfg) : cfg_(cfg) { reset(); }

    void reset() {
        integral_ = 0;
        prev_error_ = 0;
        prev_measurement_ = 0;
        filtered_deriv_ = 0;
    }

    double compute(double setpoint, double measurement) {
        double error = setpoint - measurement;

        // 积分（带限幅抗饱和）
        integral_ += error * cfg_.dt;
        integral_ = std::clamp(integral_, -cfg_.integral_limit, cfg_.integral_limit);

        // 微分（测量值微分 + 低通滤波）
        double raw_deriv = -(measurement - prev_measurement_) / cfg_.dt;
        filtered_deriv_ = cfg_.derivative_filter * filtered_deriv_
                        + (1.0 - cfg_.derivative_filter) * raw_deriv;

        prev_error_ = error;
        prev_measurement_ = measurement;

        double output = cfg_.Kp * error
                      + cfg_.Ki * integral_
                      + cfg_.Kd * filtered_deriv_;

        return std::clamp(output, cfg_.output_min, cfg_.output_max);
    }

    void setKp(double v) { cfg_.Kp = v; }
    void setKi(double v) { cfg_.Ki = v; integral_ = 0; }  // 改 Ki 时清积分
    void setKd(double v) { cfg_.Kd = v; }

private:
    Config cfg_;
    double integral_ = 0;
    double prev_error_ = 0;
    double prev_measurement_ = 0;
    double filtered_deriv_ = 0;
};
```


常见坑/追问：


- 改变 Ki 时应清零积分，否则旧积分值在新 Ki 下产生突变。
- Qt 中用 `QTimer` 定时调用 `compute()`，注意实际 dt 可能有抖动，用 `QElapsedTimer` 测量真实间隔。


---


### Q6: 🟡 PID 参数整定方法有哪些？


A: 结论：常用 Ziegler-Nichols 法快速整定，再结合实际响应曲线微调。


详细解释：


- **Ziegler-Nichols 临界振荡法**：


1. 将 Ki=0, Kd=0，逐渐增大 Kp 直到系统持续振荡
2. 记录临界增益 `Ku` 和振荡周期 `Tu`
3. 按表格计算参数：


- P 控制：`Kp = 0.5*Ku`
- PI 控制：`Kp = 0.45Ku, Ki = 1.2Kp/Tu`
- PID 控制：`Kp = 0.6Ku, Ki = 2Kp/Tu, Kd = Kp*Tu/8`
- **阶跃响应法**（更安全）：


1. 给系统一个阶跃输入，记录响应曲线
2. 从曲线读取：延迟时间 L、时间常数 T、稳态增益 K
3. `Kp = 1.2T/(KL), Ki = Kp/(2L), Kd = 0.5Kp*L`


- **经验调参顺序**：先调 Kp（快速响应），再调 Ki（消稳态误差），最后调 Kd（抑制超调）。


常见坑/追问：


- Z-N 法整定的参数通常超调较大，需要进一步减小 Kp（约乘 0.6-0.8）。
- 上位机提供在线调参界面：Qt SpinBox 绑定 PID 参数，实时观察响应曲线。


---


### Q7: 🟡 PID 在上位机软件中的典型应用场景？


A: 结论：上位机 PID 主要用于温度控制、流量控制、位置伺服等闭环控制场景。


详细解释：


- **温度控制**（最常见）：
- 传感器：热电偶/PT100 → ADC → 上位机
- 执行器：加热棒（PWM 占空比）或制冷压缩机
- 特点：大惯性、纯滞后，需要较大 Ti，Kd 通常较小
- **流量/压力控制**：
- 传感器：流量计/压力传感器 → 4-20mA → ADC
- 执行器：调节阀（0-100% 开度）
- 特点：响应较快，需要抗饱和
- **位置伺服**（电机控制）：
- 传感器：编码器 → 脉冲计数
- 执行器：伺服驱动器（速度/力矩指令）
- 特点：响应快，D 项重要，通常用增量式 PID
- **Qt 实现架构**：


```


QTimer(10ms) → 读传感器 → PID.compute() → 写执行器 → 更新图表


```


常见坑/追问：


- 上位机 PID 与 PLC/嵌入式 PID 的区别：上位机实时性差（Windows 非实时 OS），控制周期通常 ≥10ms，精密控制仍需下位机。
- 通信延迟（串口/以太网）会增加等效纯滞后，需在整定时考虑。


---


### Q8: 🔴 串级 PID 的原理和实现？


A: 结论：串级 PID 用外环控制目标量、内环控制中间量，提高响应速度和抗扰能力。


详细解释：


- **原理**：外环（主环）输出作为内环（副环）的设定值，内环响应速度要比外环快 3-10 倍。


```


外环：温度 PID → 输出加热功率设定值


内环：功率 PID → 输出 PWM 占空比


```


- **C++ 实现**：


```cpp


class CascadePID {


PIDController outer_, inner_;


public:


CascadePID(PIDController::Config outer_cfg,


PIDController::Config inner_cfg)


: outer_(outer_cfg), inner_(inner_cfg) {}


double compute(double outer_setpoint,


double outer_measurement,


double inner_measurement) {


// 外环输出作为内环设定值


double inner_setpoint = outer_.compute(outer_setpoint, outer_measurement);


// 内环输出最终控制量


return inner_.compute(inner_setpoint, inner_measurement);


}


};


```


- **调参顺序**：先整定内环（Ki=0, Kd=0 开始），内环稳定后再整定外环。


常见坑/追问：


- 内环设定值需要限幅（即外环输出限幅），防止内环设定值超出物理范围。
- 串级 PID 比单环 PID 对内部扰动（如电源波动）有更强的抑制能力。


---
