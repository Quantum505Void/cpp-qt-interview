# 50. 算法与复杂度分析

↑ 回到目录

## 一、复杂度基础

### Q1: ⭐🟢 如何分析时间复杂度和空间复杂度？

A: 时间复杂度描述算法执行步数随输入规模 n 的增长趋势，空间复杂度描述额外内存使用量。

常见复杂度从优到劣：O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)

```
二分查找：O(log n)
单层循环：O(n)
归并排序：O(n log n)
冒泡排序：O(n²)
全排列：O(n!)
```

**摊销分析**：如 `vector::push_back` 偶尔 O(n) 扩容，但均摊为 O(1)。

**递推关系**：归并排序 T(n) = 2T(n/2) + O(n)，用主定理解得 O(n log n)。

---

## 二、排序算法

### Q2: ⭐🟢 各排序算法的时间/空间复杂度对比？

A:

| 算法 | 平均 | 最坏 | 最好 | 空间 | 稳定 |
|------|------|------|------|------|------|
| 冒泡 | O(n²) | O(n²) | O(n) | O(1) | ✅ |
| 选择 | O(n²) | O(n²) | O(n²) | O(1) | ❌ |
| 插入 | O(n²) | O(n²) | O(n) | O(1) | ✅ |
| 快排 | O(n log n) | O(n²) | O(n log n) | O(log n) | ❌ |
| 归并 | O(n log n) | O(n log n) | O(n log n) | O(n) | ✅ |
| 堆排 | O(n log n) | O(n log n) | O(n log n) | O(1) | ❌ |
| 计数 | O(n+k) | O(n+k) | O(n+k) | O(k) | ✅ |
| 基数 | O(nk) | O(nk) | O(nk) | O(n+k) | ✅ |

### Q3: ⭐🟡 快速排序的实现及优化？

A:

```cpp
// 标准快排
void quickSort(vector<int>& arr, int l, int r) {
    if (l >= r) return;

    // 三数取中选 pivot，避免最坏情况
    int mid = l + (r - l) / 2;
    if (arr[l] > arr[mid]) swap(arr[l], arr[mid]);
    if (arr[l] > arr[r])   swap(arr[l], arr[r]);
    if (arr[mid] > arr[r]) swap(arr[mid], arr[r]);
    int pivot = arr[mid];
    swap(arr[mid], arr[r - 1]);

    int i = l, j = r - 1;
    while (true) {
        while (arr[++i] < pivot);
        while (arr[--j] > pivot);
        if (i < j) swap(arr[i], arr[j]);
        else break;
    }
    swap(arr[i], arr[r - 1]);
    quickSort(arr, l, i - 1);
    quickSort(arr, i + 1, r);
}

// 随机化 pivot（防止有序输入退化）
void quickSortRand(vector<int>& arr, int l, int r) {
    if (l >= r) return;
    int pivot_idx = l + rand() % (r - l + 1);
    swap(arr[pivot_idx], arr[r]);
    int pivot = arr[r], i = l - 1;
    for (int j = l; j < r; j++)
        if (arr[j] <= pivot) swap(arr[++i], arr[j]);
    swap(arr[i + 1], arr[r]);
    int p = i + 1;
    quickSortRand(arr, l, p - 1);
    quickSortRand(arr, p + 1, r);
}
```

优化：小数组用插入排序（< 16 元素），三路快排处理大量重复元素。

### Q4: ⭐🟡 归并排序及其应用（逆序对统计）？

A:

```cpp
long long mergeCount(vector<int>& arr, int l, int r) {
    if (l >= r) return 0;
    int mid = l + (r - l) / 2;
    long long cnt = mergeCount(arr, l, mid) + mergeCount(arr, mid + 1, r);

    vector<int> tmp;
    int i = l, j = mid + 1;
    while (i <= mid && j <= r) {
        if (arr[i] <= arr[j]) {
            tmp.push_back(arr[i++]);
        } else {
            cnt += mid - i + 1;  // arr[i..mid] 都比 arr[j] 大
            tmp.push_back(arr[j++]);
        }
    }
    while (i <= mid) tmp.push_back(arr[i++]);
    while (j <= r)   tmp.push_back(arr[j++]);
    copy(tmp.begin(), tmp.end(), arr.begin() + l);
    return cnt;
}
```

归并排序适合**外排序**（数据量超过内存），以及链表排序（不需要随机访问）。

### Q5: ⭐🟢 堆排序的实现？

A:

```cpp
void heapify(vector<int>& arr, int n, int i) {
    int largest = i, l = 2*i+1, r = 2*i+2;
    if (l < n && arr[l] > arr[largest]) largest = l;
    if (r < n && arr[r] > arr[largest]) largest = r;
    if (largest != i) {
        swap(arr[i], arr[largest]);
        heapify(arr, n, largest);
    }
}

void heapSort(vector<int>& arr) {
    int n = arr.size();
    // 建堆：从最后一个非叶子节点向上
    for (int i = n/2 - 1; i >= 0; i--) heapify(arr, n, i);
    // 排序
    for (int i = n - 1; i > 0; i--) {
        swap(arr[0], arr[i]);   // 最大元素放到末尾
        heapify(arr, i, 0);     // 重新堆化
    }
}
```

建堆时间 O(n)，整体 O(n log n)，原地排序（O(1) 额外空间），不稳定。

### Q6: ⭐🟡 什么时候用计数排序/基数排序？

A:

计数排序：值域范围 k 较小时（如 0~1000），O(n+k)。

```cpp
void countSort(vector<int>& arr, int maxVal) {
    vector<int> cnt(maxVal + 1, 0);
    for (int x : arr) cnt[x]++;
    int idx = 0;
    for (int i = 0; i <= maxVal; i++)
        while (cnt[i]--) arr[idx++] = i;
}
```

基数排序：按位从低到高排序，适合整数或固定长度字符串，O(nk)（k 为位数）。

```cpp
void radixSort(vector<int>& arr) {
    int maxVal = *max_element(arr.begin(), arr.end());
    for (int exp = 1; maxVal / exp > 0; exp *= 10) {
        vector<int> output(arr.size()), cnt(10, 0);
        for (int x : arr) cnt[(x / exp) % 10]++;
        for (int i = 1; i < 10; i++) cnt[i] += cnt[i-1];
        for (int i = arr.size()-1; i >= 0; i--)
            output[--cnt[(arr[i]/exp)%10]] = arr[i];
        arr = output;
    }
}
```

---

## 三、查找算法

### Q7: ⭐🟢 二分查找及常见变体？

A:

```cpp
// 标准二分：找目标值
int binarySearch(vector<int>& arr, int target) {
    int l = 0, r = arr.size() - 1;
    while (l <= r) {
        int mid = l + (r - l) / 2;  // 防溢出
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) l = mid + 1;
        else r = mid - 1;
    }
    return -1;
}

// 找第一个 >= target 的位置（lower_bound）
int lowerBound(vector<int>& arr, int target) {
    int l = 0, r = arr.size();
    while (l < r) {
        int mid = l + (r - l) / 2;
        if (arr[mid] < target) l = mid + 1;
        else r = mid;
    }
    return l;  // arr[l] >= target，或 l == n（不存在）
}

// 找第一个 > target 的位置（upper_bound）
int upperBound(vector<int>& arr, int target) {
    int l = 0, r = arr.size();
    while (l < r) {
        int mid = l + (r - l) / 2;
        if (arr[mid] <= target) l = mid + 1;
        else r = mid;
    }
    return l;
}
```

STL 提供：`std::lower_bound`, `std::upper_bound`, `std::binary_search`。

### Q8: ⭐🟡 在旋转有序数组中查找目标值？

A:

```cpp
int searchRotated(vector<int>& nums, int target) {
    int l = 0, r = nums.size() - 1;
    while (l <= r) {
        int mid = l + (r - l) / 2;
        if (nums[mid] == target) return mid;
        // 左半段有序
        if (nums[l] <= nums[mid]) {
            if (nums[l] <= target && target < nums[mid]) r = mid - 1;
            else l = mid + 1;
        } else {  // 右半段有序
            if (nums[mid] < target && target <= nums[r]) l = mid + 1;
            else r = mid - 1;
        }
    }
    return -1;
}
```

---

## 四、动态规划

### Q9: ⭐🟡 动态规划的核心思路？

A: DP 三要素：**状态定义、状态转移方程、初始条件**。

适用场景：最优子结构（全局最优由局部最优推导）+ 重叠子问题（避免重复计算）。

解题步骤：
1. 定义 dp 数组含义
2. 找状态转移方程
3. 确定初始值和遍历顺序
4. 空间优化（滚动数组）

### Q10: ⭐🟡 最长递增子序列（LIS）？

A:

```cpp
// O(n²) DP
int lis_n2(vector<int>& nums) {
    int n = nums.size();
    vector<int> dp(n, 1);
    for (int i = 1; i < n; i++)
        for (int j = 0; j < i; j++)
            if (nums[j] < nums[i]) dp[i] = max(dp[i], dp[j] + 1);
    return *max_element(dp.begin(), dp.end());
}

// O(n log n)：贪心 + 二分
int lis_nlogn(vector<int>& nums) {
    vector<int> tails;
    for (int x : nums) {
        auto it = lower_bound(tails.begin(), tails.end(), x);
        if (it == tails.end()) tails.push_back(x);
        else *it = x;
    }
    return tails.size();
}
```

### Q11: ⭐🟡 0-1 背包问题？

A:

```cpp
// dp[i][j] = 前 i 个物品，容量 j 的最大价值
int knapsack01(vector<int>& w, vector<int>& v, int W) {
    int n = w.size();
    vector<vector<int>> dp(n + 1, vector<int>(W + 1, 0));
    for (int i = 1; i <= n; i++)
        for (int j = 0; j <= W; j++) {
            dp[i][j] = dp[i-1][j];  // 不选第 i 个
            if (j >= w[i-1])
                dp[i][j] = max(dp[i][j], dp[i-1][j-w[i-1]] + v[i-1]);
        }
    return dp[n][W];
}

// 空间优化为一维（逆序遍历）
int knapsack01_opt(vector<int>& w, vector<int>& v, int W) {
    vector<int> dp(W + 1, 0);
    for (int i = 0; i < (int)w.size(); i++)
        for (int j = W; j >= w[i]; j--)  // 必须逆序
            dp[j] = max(dp[j], dp[j - w[i]] + v[i]);
    return dp[W];
}
```

### Q12: ⭐🟡 编辑距离？

A:

```cpp
// dp[i][j] = word1[0..i-1] 转换为 word2[0..j-1] 的最少操作数
int editDistance(string word1, string word2) {
    int m = word1.size(), n = word2.size();
    vector<vector<int>> dp(m + 1, vector<int>(n + 1));
    for (int i = 0; i <= m; i++) dp[i][0] = i;
    for (int j = 0; j <= n; j++) dp[0][j] = j;

    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++) {
            if (word1[i-1] == word2[j-1]) dp[i][j] = dp[i-1][j-1];
            else dp[i][j] = 1 + min({dp[i-1][j],    // 删除
                                      dp[i][j-1],    // 插入
                                      dp[i-1][j-1]}); // 替换
        }
    return dp[m][n];
}
```

### Q13: ⭐🔴 最短路径 - Dijkstra 算法？

A:

```cpp
// 单源最短路，非负权图，O((V+E) log V)
vector<int> dijkstra(int src, int n, vector<vector<pair<int,int>>>& adj) {
    vector<int> dist(n, INT_MAX);
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;
    dist[src] = 0;
    pq.push({0, src});

    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d > dist[u]) continue;  // 过时状态
        for (auto [v, w] : adj[u]) {
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

负权边用 Bellman-Ford（O(VE)）；全源最短路用 Floyd-Warshall（O(V³)）。

---

## 五、图算法

### Q14: ⭐🟡 BFS vs DFS 的选择？

A:

| 场景 | 选择 | 原因 |
|------|------|------|
| 最短路径（无权图） | BFS | 按层扩展，第一次到达即最短 |
| 拓扑排序 | DFS 或 BFS(Kahn) | 均可，BFS 更直观 |
| 连通分量 | DFS | 递归代码简洁 |
| 判断二分图 | BFS 或 DFS | 均可 |
| 树的路径问题 | DFS | 递归自然 |

```cpp
// BFS 模板
void bfs(int start, vector<vector<int>>& adj) {
    int n = adj.size();
    vector<bool> visited(n, false);
    queue<int> q;
    q.push(start); visited[start] = true;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u])
            if (!visited[v]) {
                visited[v] = true;
                q.push(v);
            }
    }
}

// DFS 模板（迭代版，防栈溢出）
void dfs(int start, vector<vector<int>>& adj) {
    int n = adj.size();
    vector<bool> visited(n, false);
    stack<int> st;
    st.push(start); visited[start] = true;
    while (!st.empty()) {
        int u = st.top(); st.pop();
        for (int v : adj[u])
            if (!visited[v]) { visited[v] = true; st.push(v); }
    }
}
```

### Q15: ⭐🟡 拓扑排序（Kahn 算法）？

A:

```cpp
// BFS + 入度，O(V+E)
vector<int> topoSort(int n, vector<vector<int>>& adj) {
    vector<int> indegree(n, 0);
    for (int u = 0; u < n; u++)
        for (int v : adj[u]) indegree[v]++;

    queue<int> q;
    for (int i = 0; i < n; i++)
        if (indegree[i] == 0) q.push(i);

    vector<int> order;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        order.push_back(u);
        for (int v : adj[u])
            if (--indegree[v] == 0) q.push(v);
    }
    return order.size() == n ? order : vector<int>{};  // 空表示有环
}
```

应用：课程调度、构建系统依赖、编译顺序。

---

## 六、贪心算法

### Q16: ⭐🟡 贪心算法的适用条件和经典问题？

A: 贪心适用条件：**贪心选择性质**（局部最优导致全局最优）+ **最优子结构**。

证明方法：交换论证法（Proof by exchange argument）。

```cpp
// 经典：区间调度最大化（按结束时间贪心）
int intervalSchedule(vector<pair<int,int>>& intervals) {
    sort(intervals.begin(), intervals.end(),
         [](auto& a, auto& b){ return a.second < b.second; });
    int count = 0, end = INT_MIN;
    for (auto& [s, e] : intervals) {
        if (s >= end) { count++; end = e; }
    }
    return count;
}

// 经典：跳跃游戏
bool canJump(vector<int>& nums) {
    int maxReach = 0;
    for (int i = 0; i < (int)nums.size(); i++) {
        if (i > maxReach) return false;
        maxReach = max(maxReach, i + nums[i]);
    }
    return true;
}
```

---

## 七、字符串算法

### Q17: ⭐🔴 KMP 算法原理和实现？

A: KMP 通过预处理**前缀函数（失配表 next）**，避免模式串回溯，时间 O(n+m)。

```cpp
// 构建 next 数组：next[i] = pattern[0..i] 的最长真前后缀长度
vector<int> buildNext(const string& pattern) {
    int m = pattern.size();
    vector<int> next(m, 0);
    for (int i = 1, j = 0; i < m; i++) {
        while (j > 0 && pattern[i] != pattern[j]) j = next[j - 1];
        if (pattern[i] == pattern[j]) j++;
        next[i] = j;
    }
    return next;
}

// KMP 搜索，返回所有匹配位置
vector<int> kmpSearch(const string& text, const string& pattern) {
    vector<int> next = buildNext(pattern);
    vector<int> result;
    int n = text.size(), m = pattern.size();
    for (int i = 0, j = 0; i < n; i++) {
        while (j > 0 && text[i] != pattern[j]) j = next[j - 1];
        if (text[i] == pattern[j]) j++;
        if (j == m) {
            result.push_back(i - m + 1);
            j = next[j - 1];
        }
    }
    return result;
}
```

### Q18: ⭐🟡 滑动窗口解决字符串问题？

A: 滑动窗口用于解决"连续子串/子数组"问题，双指针维护窗口，O(n) 时间。

```cpp
// 无重复字符的最长子串
int lengthOfLongestSubstring(string s) {
    unordered_map<char, int> last;
    int res = 0, l = 0;
    for (int r = 0; r < (int)s.size(); r++) {
        if (last.count(s[r]) && last[s[r]] >= l)
            l = last[s[r]] + 1;
        last[s[r]] = r;
        res = max(res, r - l + 1);
    }
    return res;
}

// 最小覆盖子串
string minWindow(string s, string t) {
    unordered_map<char, int> need, window;
    for (char c : t) need[c]++;
    int l = 0, valid = 0, start = 0, minLen = INT_MAX;
    for (int r = 0; r < (int)s.size(); r++) {
        char c = s[r];
        window[c]++;
        if (need.count(c) && window[c] == need[c]) valid++;
        while (valid == (int)need.size()) {
            if (r - l + 1 < minLen) { minLen = r - l + 1; start = l; }
            char d = s[l++];
            if (need.count(d) && window[d]-- == need[d]) valid--;
        }
    }
    return minLen == INT_MAX ? "" : s.substr(start, minLen);
}
```

### Q19: ⭐🟡 双指针的典型应用？

A:

```cpp
// 两数之和（有序数组）
vector<int> twoSum(vector<int>& nums, int target) {
    int l = 0, r = nums.size() - 1;
    while (l < r) {
        int sum = nums[l] + nums[r];
        if (sum == target) return {l, r};
        else if (sum < target) l++;
        else r--;
    }
    return {};
}

// 三数之和
vector<vector<int>> threeSum(vector<int>& nums) {
    sort(nums.begin(), nums.end());
    vector<vector<int>> res;
    for (int i = 0; i < (int)nums.size() - 2; i++) {
        if (i > 0 && nums[i] == nums[i-1]) continue;
        int l = i + 1, r = nums.size() - 1;
        while (l < r) {
            int s = nums[i] + nums[l] + nums[r];
            if (s == 0) {
                res.push_back({nums[i], nums[l], nums[r]});
                while (l < r && nums[l] == nums[l+1]) l++;
                while (l < r && nums[r] == nums[r-1]) r--;
                l++; r--;
            } else if (s < 0) l++;
            else r--;
        }
    }
    return res;
}
```

---

## 八、递归与分治

### Q20: ⭐🟡 分治算法的经典应用？

A:

```cpp
// 快速幂：O(log n)
long long power(long long base, long long exp, long long mod) {
    long long result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) result = result * base % mod;
        base = base * base % mod;
        exp >>= 1;
    }
    return result;
}

// 最大子数组和（分治，O(n log n)，不如 Kadane's O(n)）
int maxCrossing(vector<int>& arr, int l, int mid, int r) {
    int leftSum = INT_MIN, sum = 0;
    for (int i = mid; i >= l; i--) { sum += arr[i]; leftSum = max(leftSum, sum); }
    int rightSum = INT_MIN; sum = 0;
    for (int i = mid + 1; i <= r; i++) { sum += arr[i]; rightSum = max(rightSum, sum); }
    return leftSum + rightSum;
}

// Kadane's 算法（更优）
int maxSubarray(vector<int>& nums) {
    int res = nums[0], cur = nums[0];
    for (int i = 1; i < (int)nums.size(); i++) {
        cur = max(nums[i], cur + nums[i]);
        res = max(res, cur);
    }
    return res;
}
```

### Q21: ⭐🟡 尾递归优化及 C++ 中的应用？

A: 尾递归：递归调用是函数的**最后一步操作**，可被编译器优化为循环（节省栈空间）。

```cpp
// 普通递归：O(n) 栈空间
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);  // 非尾递归（还需乘 n）
}

// 尾递归版本
int factTail(int n, int acc = 1) {
    if (n <= 1) return acc;
    return factTail(n - 1, n * acc);  // 最后一步是递归调用
}
```

C++ 标准不强制要求尾递归优化，但 GCC/Clang 在 `-O2` 下通常会优化。深度递归（如 n > 10000）建议改写为迭代。

### Q22: ⭐🔴 如何处理超大数据量的排序（外排序）？

A: 当数据量超过内存时，使用**外排序（外部归并）**。

步骤：
1. **分割**：将数据分成 M 个能装入内存的块，各自内部排序（生成有序"归并段"）
2. **多路归并**：用小根堆维护各块当前最小元素，逐步输出，写入结果文件

```cpp
// 多路归并核心（K路）
struct Chunk { int value, chunkId; };
auto cmp = [](Chunk& a, Chunk& b) { return a.value > b.value; };
priority_queue<Chunk, vector<Chunk>, decltype(cmp)> pq(cmp);

// 初始化：各块取第一个元素入堆
// 循环：取堆顶输出，从对应块补充下一个元素
```

实际工程：Hadoop MapReduce 排序、数据库外排序、`sort` 命令（`sort -T` 指定临时目录）。

### Q23: ⭐🟡 如何高效求两个有序数组的中位数？

A:

```cpp
// O(log(min(m,n)))：二分在较短数组上找分割点
double findMedianSortedArrays(vector<int>& A, vector<int>& B) {
    if (A.size() > B.size()) swap(A, B);
    int m = A.size(), n = B.size();
    int lo = 0, hi = m;

    while (lo <= hi) {
        int i = (lo + hi) / 2;
        int j = (m + n + 1) / 2 - i;

        int maxL_A = (i == 0) ? INT_MIN : A[i-1];
        int minR_A = (i == m) ? INT_MAX : A[i];
        int maxL_B = (j == 0) ? INT_MIN : B[j-1];
        int minR_B = (j == n) ? INT_MAX : B[j];

        if (maxL_A <= minR_B && maxL_B <= minR_A) {
            if ((m + n) % 2 == 1) return max(maxL_A, maxL_B);
            return (max(maxL_A, maxL_B) + min(minR_A, minR_B)) / 2.0;
        } else if (maxL_A > minR_B) hi = i - 1;
        else lo = i + 1;
    }
    return 0;
}
```

### Q24: ⭐🟡 `std::sort` 的底层实现是什么？

A: C++ STL 的 `std::sort` 通常使用 **Introsort**（内省排序）：

1. 小数组（< 16 元素）：**插入排序**（缓存友好，常数小）
2. 递归深度超过 2log₂n：**堆排序**（防止快排退化到 O(n²)）
3. 其他情况：**快速排序**（三数取中选 pivot）

```cpp
// 自定义比较器
vector<pair<int,string>> v = {{3,"c"},{1,"a"},{2,"b"}};
sort(v.begin(), v.end(), [](auto& a, auto& b){
    return a.first < b.first;
});

// stable_sort（归并排序，O(n log n)，稳定）
stable_sort(v.begin(), v.end(), [](auto& a, auto& b){
    return a.second < b.second;
});
```

`std::sort` 不稳定，需要稳定排序用 `std::stable_sort`（底层归并）。
