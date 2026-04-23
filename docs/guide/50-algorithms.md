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


---

### Q25: ⭐🟡 希尔排序的原理是什么？为什么比插入排序更快？

A: 希尔排序（Shell Sort）是**插入排序的改进版**，通过逐渐缩小间隔（gap）让数组"大致有序"，最终 gap=1 时退化为插入排序，但此时数组已接近有序，效率很高。

**核心思想：** 分组插入排序，每次对间隔为 gap 的子序列排序，gap 逐渐缩小到 1

```cpp
void shellSort(vector<int>& arr) {
    int n = arr.size();
    // 使用 Knuth 序列：1, 4, 13, 40, 121, ...
    int gap = 1;
    while (gap < n / 3) gap = 3 * gap + 1;

    while (gap >= 1) {
        // 对间隔为 gap 的子序列做插入排序
        for (int i = gap; i < n; i++) {
            int temp = arr[i];
            int j = i;
            while (j >= gap && arr[j - gap] > temp) {
                arr[j] = arr[j - gap];
                j -= gap;
            }
            arr[j] = temp;
        }
        gap /= 3;
    }
}
```

**复杂度：**
- 时间：依赖 gap 序列，Knuth 序列下约 O(n^1.5)
- 空间：O(1)，原地排序
- 不稳定排序

**与插入排序对比：**
插入排序每次只移动一位，希尔排序通过大步长交换，一次操作能跨越多位置，减少总移动次数。

> 💡 面试追问：选择不同 gap 序列（Hibbard、Sedgewick）会有什么影响？  
> 理论上 Sedgewick 序列可达 O(n^4/3)，但实践中差距不大，记住 Knuth 序列即可。

---

### Q26: ⭐🟡 桶排序和计数排序如何实现？适用什么场景？

A: 两者都是非比较排序，利用数据分布特性突破 O(n log n) 下界。

**计数排序（Counting Sort）**：适合数据范围小的整数

```cpp
void countingSort(vector<int>& arr) {
    if (arr.empty()) return;
    int maxVal = *max_element(arr.begin(), arr.end());
    int minVal = *min_element(arr.begin(), arr.end());
    int range = maxVal - minVal + 1;

    vector<int> count(range, 0);
    for (int x : arr) count[x - minVal]++;

    // 计算前缀和（稳定排序需要此步）
    for (int i = 1; i < range; i++) count[i] += count[i-1];

    vector<int> output(arr.size());
    for (int i = arr.size()-1; i >= 0; i--) {
        output[--count[arr[i] - minVal]] = arr[i];
    }
    arr = output;
}
// 时间 O(n+k)，空间 O(n+k)，k 为数值范围，稳定
```

**桶排序（Bucket Sort）**：适合均匀分布的浮点数

```cpp
void bucketSort(vector<float>& arr) {
    int n = arr.size();
    vector<vector<float>> buckets(n);

    // 将元素分配到桶
    for (float x : arr) {
        int idx = (int)(x * n);  // 假设数据在 [0, 1)
        buckets[idx].push_back(x);
    }

    // 每个桶内排序
    int pos = 0;
    for (auto& bucket : buckets) {
        sort(bucket.begin(), bucket.end());
        for (float x : bucket) arr[pos++] = x;
    }
}
// 平均 O(n)，最坏 O(n²)，空间 O(n)
```

| 算法 | 时间（平均） | 空间 | 稳定 | 适用 |
|------|------------|------|------|------|
| 计数排序 | O(n+k) | O(k) | ✅ | 小范围整数（如年龄、成绩） |
| 桶排序 | O(n) | O(n) | ✅ | 均匀分布浮点数 |
| 基数排序 | O(d(n+k)) | O(n+k) | ✅ | 多位整数 |

> 💡 面试追问：为什么计数排序要从右向左填充 output？  
> 保证稳定性：相同元素后者放后面，维持原有相对顺序。

---

### Q27: ⭐🟡 `std::stable_sort` 和 `std::sort` 有什么区别？何时必须用前者？

A: 核心区别是**稳定性**——相等元素在排序后是否保持原有相对顺序。

| 特性 | `std::sort` | `std::stable_sort` |
|------|------------|-------------------|
| 稳定性 | ❌ 不稳定 | ✅ 稳定 |
| 底层算法 | Introsort（快排+堆排+插排） | TimSort / 归并排序 |
| 时间复杂度 | O(n log n) | O(n log n) |
| 空间复杂度 | O(log n)（递归栈） | O(n)（额外缓冲区） |
| 速度 | 更快（常数小） | 稍慢 |

```cpp
struct Student { string name; int score; };
vector<Student> students = {{"Alice", 90}, {"Bob", 90}, {"Charlie", 85}};

// stable_sort：Alice 和 Bob 分数相同，原始顺序保留（Alice 在前）
stable_sort(students.begin(), students.end(),
    [](const Student& a, const Student& b) { return a.score > b.score; });

// sort：Alice 和 Bob 的相对顺序不确定
sort(students.begin(), students.end(),
    [](const Student& a, const Student& b) { return a.score > b.score; });

// 何时必须用 stable_sort：
// 1. 多关键字排序（先按 score，已排序后再按 name，需保持 score 的顺序）
// 2. UI 列表排序（用户可能期望"相同条件下保持原顺序"）
// 3. 分布式合并（各分片已排序，归并时需保证稳定性）
```

> 💡 面试追问：如何用 `sort` 模拟稳定排序？  
> 在比较函数中加入原始下标作为最后一个比较键：`if (a.score == b.score) return a.index < b.index;`

---

### Q28: ⭐🟡 插值查找和斐波那契查找与二分查找有何不同？

A: 两者都是**非均匀划分的查找算法**，试图根据数据分布更智能地选择比较点。

**插值查找（Interpolation Search）**：
- 根据目标值估算位置（类似字典查找）
- `mid = lo + (target - arr[lo]) * (hi - lo) / (arr[hi] - arr[lo])`

```cpp
int interpolationSearch(vector<int>& arr, int target) {
    int lo = 0, hi = arr.size() - 1;
    while (lo <= hi && target >= arr[lo] && target <= arr[hi]) {
        if (lo == hi) return arr[lo] == target ? lo : -1;
        // 按比例估算位置
        int mid = lo + (long long)(target - arr[lo]) * (hi - lo) / (arr[hi] - arr[lo]);
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
// 均匀分布时：O(log log n)；最坏情况：O(n)
```

**斐波那契查找（Fibonacci Search）**：
- 用斐波那契数列划分区间，避免浮点除法
- 相比二分查找，只需加减运算，对某些硬件更友好

```cpp
int fibonacciSearch(vector<int>& arr, int target) {
    int n = arr.size();
    // 生成斐波那契数列
    vector<int> fib = {1, 1};
    while (fib.back() < n) fib.push_back(fib[fib.size()-1] + fib[fib.size()-2]);

    int k = fib.size() - 1;  // 使用 fib[k] >= n
    // 用最后一个元素填充
    vector<int> padded = arr;
    padded.resize(fib[k], arr.back());

    int lo = 0;
    while (k > 1) {
        int mid = lo + fib[k-1] - 1;
        if (target < padded[mid]) k--;
        else if (target > padded[mid]) { lo = mid + 1; k -= 2; }
        else return mid < n ? mid : n - 1;
    }
    return (lo < n && padded[lo] == target) ? lo : -1;
}
```

| 算法 | 平均时间 | 最坏时间 | 优势 |
|------|---------|---------|------|
| 二分查找 | O(log n) | O(log n) | 稳定，通用 |
| 插值查找 | O(log log n) | O(n) | 均匀分布数据 |
| 斐波那契查找 | O(log n) | O(log n) | 无乘除法运算 |

> 💡 面试追问：插值查找在什么数据上性能最差？  
> 严重不均匀分布（如指数分布），估算点严重偏离实际位置，退化到 O(n)。

---

### Q29: ⭐🟡 红黑树查找 vs B+ 树查找，分别适合什么场景？

A: 两者都支持 O(log n) 查找，但设计目标不同：

| 特性 | 红黑树 | B+ 树 |
|------|--------|-------|
| 优化目标 | **内存访问效率** | **磁盘 I/O 效率** |
| 节点大小 | 每节点1个key | 每节点可有数百个key |
| 树高 | O(log n) 较高 | O(log_M n) 极低（M为阶） |
| 缓存友好 | 一般（节点小，跳转多） | 很好（块读取整个节点） |
| 范围查询 | 需中序遍历 | **叶链表直接扫描** |
| 实现复杂度 | 中等 | 较复杂 |

**适用场景：**

```
红黑树适合：
- 内存中的数据结构（C++ std::map, Java TreeMap）
- 需要频繁插入删除，数据量在内存范围内
- Linux 进程调度（CFS 完全公平调度器）
- Nginx 定时器管理

B+ 树适合：
- 数据库索引（MySQL InnoDB, PostgreSQL）
- 文件系统（NTFS, ext4 的目录索引）
- 数据远大于内存，需要分页加载
- 频繁范围查询
```

```cpp
// 使用 std::map（红黑树底层）
map<int, string> rbtree;
rbtree[1] = "a";
auto it = rbtree.lower_bound(5);  // O(log n)

// 范围查询（需要迭代器遍历）
for (auto it = rbtree.lower_bound(3); it != rbtree.upper_bound(7); it++) {
    cout << it->first << " ";
}
```

> 💡 面试追问：为什么 Linux 内核选红黑树而不是 AVL 树？  
> 红黑树旋转操作更少（AVL 严格平衡，插删时旋转更多），对频繁修改场景更高效。

---

### Q30: ⭐🟡 完全背包问题与 0-1 背包有什么区别？

A: 两者都是经典 DP，区别在于每种物品**能否重复选取**：

- **0-1 背包**：每种物品最多选 1 次
- **完全背包**：每种物品可选无限次

```cpp
// 0-1 背包：倒序遍历（防止同一物品被选多次）
int knapsack01(int W, vector<int>& weight, vector<int>& value) {
    int n = weight.size();
    vector<int> dp(W + 1, 0);
    for (int i = 0; i < n; i++) {
        for (int w = W; w >= weight[i]; w--) {  // ← 倒序
            dp[w] = max(dp[w], dp[w - weight[i]] + value[i]);
        }
    }
    return dp[W];
}

// 完全背包：正序遍历（允许同一物品重复选）
int knapsackComplete(int W, vector<int>& weight, vector<int>& value) {
    int n = weight.size();
    vector<int> dp(W + 1, 0);
    for (int i = 0; i < n; i++) {
        for (int w = weight[i]; w <= W; w++) {  // ← 正序！
            dp[w] = max(dp[w], dp[w - weight[i]] + value[i]);
        }
    }
    return dp[W];
}

// 完全背包变体：零钱兑换（最少硬币数）LeetCode 322
int coinChange(vector<int>& coins, int amount) {
    vector<int> dp(amount + 1, INT_MAX);
    dp[0] = 0;
    for (int coin : coins) {
        for (int i = coin; i <= amount; i++) {
            if (dp[i - coin] != INT_MAX)
                dp[i] = min(dp[i], dp[i - coin] + 1);
        }
    }
    return dp[amount] == INT_MAX ? -1 : dp[amount];
}
```

**关键区别记忆**：
- 倒序 → 0-1（保证每件只用一次）
- 正序 → 完全（当前轮允许再次使用本物品）

**时间/空间**：O(nW) / O(W)

> 💡 面试追问：多重背包（每种物品最多 k 次）如何解决？  
> 二进制拆分：将 k 件物品拆成 1, 2, 4, ... 件的若干组，转化为 0-1 背包，时间降至 O(nW log k)。

---

### Q31: ⭐🟡 最长公共子序列（LCS）如何实现？与最长公共子串有什么区别？

A: LCS（Longest Common Subsequence）允许不连续，LCS（子串）要求连续。

```cpp
// LCS（子序列，不要求连续）
int longestCommonSubsequence(string s1, string s2) {
    int m = s1.size(), n = s2.size();
    vector<vector<int>> dp(m+1, vector<int>(n+1, 0));

    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            if (s1[i-1] == s2[j-1])
                dp[i][j] = dp[i-1][j-1] + 1;
            else
                dp[i][j] = max(dp[i-1][j], dp[i][j-1]);
        }
    }
    return dp[m][n];
}

// 还原 LCS 序列（回溯）
string getLCS(string s1, string s2) {
    int m = s1.size(), n = s2.size();
    vector<vector<int>> dp(m+1, vector<int>(n+1, 0));
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            dp[i][j] = s1[i-1] == s2[j-1] ? dp[i-1][j-1] + 1
                                            : max(dp[i-1][j], dp[i][j-1]);
    string lcs;
    int i = m, j = n;
    while (i > 0 && j > 0) {
        if (s1[i-1] == s2[j-1]) { lcs = s1[i-1] + lcs; i--; j--; }
        else if (dp[i-1][j] > dp[i][j-1]) i--;
        else j--;
    }
    return lcs;
}

// 最长公共子串（要求连续）
int longestCommonSubstring(string s1, string s2) {
    int m = s1.size(), n = s2.size(), res = 0;
    vector<vector<int>> dp(m+1, vector<int>(n+1, 0));
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++) {
            dp[i][j] = s1[i-1] == s2[j-1] ? dp[i-1][j-1] + 1 : 0;  // ← 不同！
            res = max(res, dp[i][j]);
        }
    return res;
}
```

**状态转移方程对比：**

| | LCS（子序列） | LCS（子串） |
|--|--|--|
| 字符相等 | `dp[i][j] = dp[i-1][j-1] + 1` | `dp[i][j] = dp[i-1][j-1] + 1` |
| 字符不等 | `dp[i][j] = max(dp[i-1][j], dp[i][j-1])` | `dp[i][j] = 0` |

**时间/空间**：O(mn) / O(mn)（可用滚动数组压缩到 O(n)）

> 💡 面试追问：edit distance（编辑距离）和 LCS 有什么关系？  
> `edit_distance = m + n - 2 * LCS_length`（只考虑插入删除时）。

---

### Q32: ⭐🔴 股票买卖系列问题如何用状态机 DP 统一解决？

A: 股票问题（LeetCode 121/122/123/188/309/714）可以用**状态机 DP** 统一框架：

**状态定义**：`dp[i][k][hold]`
- `i`：第 i 天
- `k`：还剩几次交易机会（每次买入消耗一次）
- `hold`：0=不持股，1=持股

```cpp
// 通用框架（以最多 k 次交易为例）
int maxProfit_k(int K, vector<int>& prices) {
    int n = prices.size();
    if (n == 0 || K == 0) return 0;

    // K >= n/2 时等价于无限次交易
    if (K >= n / 2) {
        int profit = 0;
        for (int i = 1; i < n; i++)
            profit += max(0, prices[i] - prices[i-1]);
        return profit;
    }

    // dp[k][0/1] = 还剩 k 次机会时，不持股/持股的最大利润
    vector<vector<int>> dp(K+1, vector<int>(2, 0));
    for (int k = 0; k <= K; k++) dp[k][1] = INT_MIN;

    for (int price : prices) {
        for (int k = K; k >= 1; k--) {
            dp[k][0] = max(dp[k][0], dp[k][1] + price);     // 卖出
            dp[k][1] = max(dp[k][1], dp[k-1][0] - price);   // 买入
        }
    }
    return dp[K][0];
}

// 含冷冻期（卖出后需等一天）
int maxProfit_cooldown(vector<int>& prices) {
    int hold = INT_MIN, sold = 0, rest = 0;
    for (int p : prices) {
        int prevSold = sold;
        sold = hold + p;          // 今天卖
        hold = max(hold, rest - p); // 今天买（必须从 rest 状态）
        rest = max(rest, prevSold); // 今天休息
    }
    return max(sold, rest);
}

// 含手续费
int maxProfit_fee(vector<int>& prices, int fee) {
    int cash = 0, hold = INT_MIN;
    for (int p : prices) {
        cash = max(cash, hold + p - fee);  // 卖出
        hold = max(hold, cash - p);        // 买入
    }
    return cash;
}
```

**状态转移核心**：
- `不持股 = max(昨天不持股, 昨天持股+今天卖价)`
- `持股 = max(昨天持股, 昨天不持股-今天买价)`

> 💡 面试追问：如何在 O(n) 时间 O(1) 空间解决 k=2 次交易的问题？  
> 维护 4 个变量：buy1, sell1, buy2, sell2 分别表示两次买卖的状态。

---

### Q33: ⭐🔴 Floyd-Warshall 全源最短路算法如何实现？

A: Floyd-Warshall 用动态规划计算所有顶点对之间的最短路径。

**核心思想**：`dp[i][j][k]` = 只经过编号 ≤ k 的中间节点时，i 到 j 的最短路

```cpp
// Floyd-Warshall，O(V³) 时间，O(V²) 空间
void floydWarshall(vector<vector<int>>& dist) {
    int V = dist.size();

    // 初始化：dist[i][j] = 直接边权，dist[i][i] = 0，无边 = INF
    for (int k = 0; k < V; k++) {    // 中间节点
        for (int i = 0; i < V; i++) { // 起点
            for (int j = 0; j < V; j++) { // 终点
                if (dist[i][k] != INT_MAX && dist[k][j] != INT_MAX)
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
            }
        }
    }

    // 检测负环：对角线有负值则存在负环
    for (int i = 0; i < V; i++)
        if (dist[i][i] < 0) { cout << "Negative cycle!"; return; }
}

// 还原路径（需额外 next 矩阵）
void floydWithPath(vector<vector<int>>& dist, vector<vector<int>>& next) {
    int V = dist.size();
    // 初始化 next[i][j] = j（直接到达）
    for (int k = 0; k < V; k++)
        for (int i = 0; i < V; i++)
            for (int j = 0; j < V; j++)
                if (dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j];
                    next[i][j] = next[i][k];  // 经过 k 到达 j
                }

    // 还原路径
    auto getPath = [&](int src, int dst) {
        vector<int> path = {src};
        while (src != dst) { src = next[src][dst]; path.push_back(src); }
        return path;
    };
}
```

**适用场景：**
- 图规模小（V ≤ 500），需要所有点对最短路
- 传递闭包问题（dist 改为 bool，min → OR，+ → AND）
- 检测负环

> 💡 面试追问：V=1000 时用 Floyd 可行吗？  
> 1000³ = 10⁹ 次操作，约需 1-2 秒，勉强可行。更大规模应对每个源点跑 Dijkstra，总计 O(VE log V)。

---

### Q34: ⭐🟡 欧拉路径和哈密顿路径有什么区别？如何判断存在性？

A: 两者都是图遍历问题，但约束对象不同：

| 概念 | 约束 | 判断 | 算法复杂度 |
|------|------|------|-----------|
| **欧拉路径** | 经过**每条边**恰好一次 | 简单（度数条件） | O(E) |
| **欧拉回路** | 欧拉路径且首尾相连 | 简单 | O(E) |
| **哈密顿路径** | 经过**每个顶点**恰好一次 | NP 完全！ | O(n! 或 2ⁿ·n²) |
| **哈密顿回路** | 哈密顿路径且首尾相连 | NP 完全 | O(2ⁿ·n²) |

**欧拉路径/回路的判断条件：**

```cpp
// 无向图：
// - 欧拉回路：连通 + 所有顶点度数为偶数
// - 欧拉路径：连通 + 恰好 0 或 2 个奇度顶点

// 有向图：
// - 欧拉回路：强连通 + 所有顶点 in-degree == out-degree
// - 欧拉路径：连通 + 恰好一个顶点 out-in=1（起点），一个 in-out=1（终点）

// Hierholzer 算法求欧拉路径（O(E)）
vector<int> eulerPath(int n, vector<vector<int>>& adj, int start) {
    vector<int> path;
    stack<int> stk;
    vector<int> degree(n, 0);
    for (int u = 0; u < n; u++) degree[u] = adj[u].size();

    stk.push(start);
    while (!stk.empty()) {
        int u = stk.top();
        if (degree[u] == 0) {
            path.push_back(u);
            stk.pop();
        } else {
            int v = adj[u][--degree[u]];
            stk.push(v);
        }
    }
    reverse(path.begin(), path.end());
    return path;
}
```

**哈密顿路径（状压 DP，O(2ⁿ·n²)）**：

```cpp
// dp[mask][i] = 经过 mask 集合的顶点，最后在 i 的路径是否存在
bool hamiltonianPath(int n, vector<vector<bool>>& adj) {
    vector<vector<bool>> dp(1<<n, vector<bool>(n, false));
    for (int i = 0; i < n; i++) dp[1<<i][i] = true;

    for (int mask = 1; mask < (1<<n); mask++)
        for (int u = 0; u < n; u++) {
            if (!dp[mask][u]) continue;
            for (int v = 0; v < n; v++) {
                if (!(mask & (1<<v)) && adj[u][v])
                    dp[mask|(1<<v)][v] = true;
            }
        }

    int fullMask = (1<<n) - 1;
    for (int i = 0; i < n; i++)
        if (dp[fullMask][i]) return true;
    return false;
}
```

> 💡 面试追问：TSP（旅行商问题）和哈密顿回路是什么关系？  
> TSP 是带权哈密顿回路问题（找最短的哈密顿回路），同样是 NP 完全。

---

### Q35: ⭐🟡 Rabin-Karp 字符串匹配算法的原理是什么？

A: Rabin-Karp 用**滚动哈希**将字符串比较转为哈希值比较，平均 O(n+m)。

**核心思想：**
1. 计算模式串 P 的哈希值
2. 在文本串 T 中滑动窗口，用滚动哈希 O(1) 更新窗口哈希
3. 哈希匹配时才真正比较字符串（避免哈希冲突漏报）

```cpp
vector<int> rabinKarp(const string& text, const string& pattern) {
    int n = text.size(), m = pattern.size();
    const long long BASE = 31, MOD = 1e9 + 9;
    vector<int> matches;

    if (m > n) return matches;

    // 计算 BASE^(m-1) % MOD
    long long power = 1;
    for (int i = 0; i < m - 1; i++) power = power * BASE % MOD;

    auto charHash = [](char c) { return c - 'a' + 1; };

    // 计算模式串哈希
    long long patHash = 0;
    for (char c : pattern) patHash = (patHash * BASE + charHash(c)) % MOD;

    // 计算文本串第一个窗口哈希
    long long winHash = 0;
    for (int i = 0; i < m; i++) winHash = (winHash * BASE + charHash(text[i])) % MOD;

    for (int i = 0; i <= n - m; i++) {
        if (winHash == patHash) {
            // 哈希匹配，验证实际字符串（防止冲突）
            if (text.substr(i, m) == pattern)
                matches.push_back(i);
        }
        // 滚动更新哈希
        if (i < n - m) {
            winHash = (winHash - charHash(text[i]) * power % MOD + MOD) % MOD;
            winHash = (winHash * BASE + charHash(text[i+m])) % MOD;
        }
    }
    return matches;
}
```

**复杂度：**
- 平均 O(n+m)（哈希冲突少时）
- 最坏 O(nm)（哈希冲突严重时）

**应用：** 抄袭检测（Rabin-Karp 可同时搜索多个模式串）

> 💡 面试追问：KMP vs Rabin-Karp 如何选择？  
> KMP 保证 O(n+m) 最坏情况；Rabin-Karp 适合多模式匹配（同时检测 k 个模式只需 O(n+k·m)）。

---

### Q36: ⭐🔴 Manacher 算法如何在 O(n) 时间内找到最长回文子串？

A: Manacher 通过**利用已知回文信息避免重复扫描**，将暴力 O(n²) 降至 O(n)。

```cpp
string manacher(const string& s) {
    // 插入分隔符，统一处理奇偶长度
    string t = "#";
    for (char c : s) { t += c; t += '#'; }
    int n = t.size();

    vector<int> p(n, 0);  // p[i] = 以 i 为中心的回文半径
    int center = 0, right = 0;  // 已知最右回文的中心和右边界

    for (int i = 0; i < n; i++) {
        if (i < right) {
            int mirror = 2 * center - i;  // i 关于 center 的镜像
            p[i] = min(right - i, p[mirror]);  // 利用镜像信息
        }

        // 尝试扩展
        while (i + p[i] + 1 < n && i - p[i] - 1 >= 0
               && t[i + p[i] + 1] == t[i - p[i] - 1])
            p[i]++;

        // 更新最右回文
        if (i + p[i] > right) {
            center = i;
            right = i + p[i];
        }
    }

    // 找最大回文
    int maxLen = 0, centerIdx = 0;
    for (int i = 0; i < n; i++) {
        if (p[i] > maxLen) { maxLen = p[i]; centerIdx = i; }
    }

    // 还原到原始字符串
    int start = (centerIdx - maxLen) / 2;
    return s.substr(start, maxLen);
}
```

**关键洞察：**  
若 `i < right`（i 在已知最右回文内），则 `p[i] >= min(right-i, p[mirror])`，只需从这个起点扩展，不用从 0 开始。

**时间复杂度**：O(n)（right 指针单调递增，总扩展次数 O(n)）  
**空间复杂度**：O(n)

> 💡 面试追问：如何用 DP 解最长回文子串？  
> `dp[i][j]` = s[i..j] 是否回文，转移：`dp[i][j] = dp[i+1][j-1] && s[i]==s[j]`，O(n²) 时间。

---

### Q37: ⭐🟡 接雨水问题有哪几种解法？

A: 接雨水（LeetCode 42）是高频题，四种解法从 O(n²) 到 O(n)：

```cpp
// 方法1：暴力 O(n²) — 每个位置找左右最大值
int trap_brute(vector<int>& h) {
    int n = h.size(), ans = 0;
    for (int i = 1; i < n-1; i++) {
        int lmax = *max_element(h.begin(), h.begin()+i+1);
        int rmax = *max_element(h.begin()+i, h.end());
        ans += min(lmax, rmax) - h[i];
    }
    return ans;
}

// 方法2：前缀/后缀预处理 O(n) 时间 O(n) 空间
int trap_prefix(vector<int>& h) {
    int n = h.size();
    vector<int> lmax(n), rmax(n);
    lmax[0] = h[0];
    for (int i = 1; i < n; i++) lmax[i] = max(lmax[i-1], h[i]);
    rmax[n-1] = h[n-1];
    for (int i = n-2; i >= 0; i--) rmax[i] = max(rmax[i+1], h[i]);
    int ans = 0;
    for (int i = 0; i < n; i++) ans += min(lmax[i], rmax[i]) - h[i];
    return ans;
}

// 方法3：双指针 O(n) 时间 O(1) 空间 ★推荐★
int trap_twoptr(vector<int>& h) {
    int lo = 0, hi = h.size()-1, lmax = 0, rmax = 0, ans = 0;
    while (lo < hi) {
        if (h[lo] < h[hi]) {
            h[lo] >= lmax ? lmax = h[lo] : ans += lmax - h[lo];
            lo++;
        } else {
            h[hi] >= rmax ? rmax = h[hi] : ans += rmax - h[hi];
            hi--;
        }
    }
    return ans;
}

// 方法4：单调栈 O(n) — 按横向计算每层积水
int trap_stack(vector<int>& h) {
    stack<int> stk;
    int ans = 0;
    for (int i = 0; i < h.size(); i++) {
        while (!stk.empty() && h[i] > h[stk.top()]) {
            int bottom = stk.top(); stk.pop();
            if (stk.empty()) break;
            int width = i - stk.top() - 1;
            int height = min(h[i], h[stk.top()]) - h[bottom];
            ans += width * height;
        }
        stk.push(i);
    }
    return ans;
}
```

| 方法 | 时间 | 空间 | 备注 |
|------|------|------|------|
| 暴力 | O(n²) | O(1) | 面试别用 |
| 前缀预处理 | O(n) | O(n) | 易理解 |
| 双指针 | O(n) | O(1) | **最优** |
| 单调栈 | O(n) | O(n) | 横向思维 |

---

### Q38: ⭐🟡 三数之和如何高效求解并去重？

A: LeetCode 15，排序 + 双指针，核心难点在去重：

```cpp
vector<vector<int>> threeSum(vector<int>& nums) {
    sort(nums.begin(), nums.end());
    vector<vector<int>> res;
    int n = nums.size();

    for (int i = 0; i < n - 2; i++) {
        if (nums[i] > 0) break;  // 最小值已>0，不可能三数和为0
        if (i > 0 && nums[i] == nums[i-1]) continue;  // 去重：跳过相同的 i

        int lo = i + 1, hi = n - 1;
        while (lo < hi) {
            int sum = nums[i] + nums[lo] + nums[hi];
            if (sum == 0) {
                res.push_back({nums[i], nums[lo], nums[hi]});
                // 去重：跳过相同的 lo 和 hi
                while (lo < hi && nums[lo] == nums[lo+1]) lo++;
                while (lo < hi && nums[hi] == nums[hi-1]) hi--;
                lo++; hi--;
            } else if (sum < 0) lo++;
            else hi--;
        }
    }
    return res;
}
```

**时间复杂度**：O(n²)（排序 O(n log n) + 双指针 O(n²)）  
**空间复杂度**：O(1)（不计输出）

**去重三要点**：
1. `i` 去重：`i > 0 && nums[i] == nums[i-1]` 时跳过
2. `lo` 去重：找到答案后，跳过所有 `nums[lo] == nums[lo+1]`
3. `hi` 去重：找到答案后，跳过所有 `nums[hi] == nums[hi-1]`

> 💡 面试追问：四数之和怎么做？  
> 再加一层外循环，内部跑三数之和（即双指针），时间 O(n³)。

---

### Q39: ⭐🔴 N 皇后问题如何用回溯法解决？如何剪枝？

A: N 皇后是经典回溯题，核心是高效判断位置是否合法：

```cpp
class NQueens {
    int n;
    vector<vector<string>> results;
    vector<bool> col, diag1, diag2;  // 列、左斜线、右斜线

public:
    vector<vector<string>> solveNQueens(int n) {
        this->n = n;
        col.assign(n, false);
        diag1.assign(2*n-1, false);  // 左斜线（row-col+n-1）
        diag2.assign(2*n-1, false);  // 右斜线（row+col）
        vector<int> queens(n, -1);
        backtrack(queens, 0);
        return results;
    }

    void backtrack(vector<int>& queens, int row) {
        if (row == n) {
            // 构建棋盘
            vector<string> board(n, string(n, '.'));
            for (int r = 0; r < n; r++) board[r][queens[r]] = 'Q';
            results.push_back(board);
            return;
        }

        for (int c = 0; c < n; c++) {
            if (col[c] || diag1[row-c+n-1] || diag2[row+c]) continue;
            // 放置皇后
            queens[row] = c;
            col[c] = diag1[row-c+n-1] = diag2[row+c] = true;
            backtrack(queens, row + 1);
            // 撤销
            col[c] = diag1[row-c+n-1] = diag2[row+c] = false;
        }
    }
};

// 位运算优化版（极速）
int totalNQueens(int n) {
    int ans = 0;
    function<void(int,int,int,int)> bt = [&](int row, int cols, int d1, int d2) {
        if (row == n) { ans++; return; }
        int available = ((1<<n)-1) & ~(cols|d1|d2);
        while (available) {
            int bit = available & (-available);  // 取最低位
            available &= available - 1;
            bt(row+1, cols|bit, (d1|bit)<<1, (d2|bit)>>1);
        }
    };
    bt(0, 0, 0, 0);
    return ans;
}
```

**回溯剪枝策略：**
1. 用 bool 数组 O(1) 判断列/斜线冲突（不需每次遍历已放皇后）
2. 位运算版：用整数的位来表示可用列，`lowbit` 取最低位，极速
3. 利用对称性：只搜索第一行皇后放在前 n/2 列的情况，结果×2

**时间复杂度**：O(n!)（上界），实际剪枝后远小于此

> 💡 面试追问：N 皇后的解的数量是多少？  
> N=8 时有 92 个解，N=12 时 14200 个，随 N 增长极快（无封闭公式）。
