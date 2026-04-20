# 30. Git 与版本控制


↑ 回到目录


### Q1: ⭐🟢 git merge 和 git rebase 的核心区别是什么？


A: 结论：`merge` 保留分叉历史并产生合并提交；`rebase` 重写提交基线，让历史更线性。二者没有绝对优劣，关键看团队协作规则。


详细解释：


- `merge` 更保真，适合保留真实分支演进。
- `rebase` 更清爽，适合整理本地分支历史后再提交。
- 公开分支慎用 rebase，因为会改写历史。


常见坑/追问：


- 高频追问：什么时候不能 rebase 已共享分支？因为别人历史会被打乱。


### Q2: ⭐🟢 git reset、git revert、git restore 怎么区分？


A: 结论：`reset` 偏本地历史/指针回退，`revert` 是新增一个反向提交，`restore` 偏工作区/暂存区文件恢复。


详细解释：


- 回滚已发布提交，优先考虑 `revert`。
- `reset --hard` 破坏性强，要非常谨慎。


常见坑/追问：


- 面试里若能主动说“线上共享历史优先 revert”会很稳。


### Q3: ⭐🟡 冲突解决时你一般怎么做？


A: 结论：先理解两边改动意图，再决定保留、合并还是重构，不能机械地选 ours/theirs。


详细解释：


- 先看文件级上下文和测试影响。
- 冲突解决后要跑编译/测试，而不是只看 Git 不报错。


常见坑/追问：


- 大项目里很多冲突不是文本冲突，而是语义冲突。


### Q4: ⭐🟡 为什么团队常要求“小步提交”？


A: 结论：小步提交更便于 review、定位问题、回滚和 cherry-pick，也能保留更清晰的设计演进轨迹。


详细解释：


- 一个 commit 最好表达一个逻辑完整改动。
- 这对 bisect 排障也很友好。


常见坑/追问：


- 不要把“改了三天的一堆杂活”塞成一个巨型提交。


### Q5: 🟡 git stash 适合什么场景？


A: 结论：适合临时切换上下文时保存未完成修改，但不应拿它当长期存储或任务管理工具。


详细解释：


- 修紧急 bug、切分支排障时很好用。
- 用完要及时清理或恢复，避免 stash 黑洞。


常见坑/追问：


- stash 太多说明工作流可能有问题。


### Q6: 🟡 cherry-pick 的典型使用场景是什么？


A: 结论：把某个特定修复从一个分支摘到另一个分支，比如 hotfix 回灌、多版本线同步。


详细解释：


- 它适合“只要这一个 commit，不要整段历史”的场景。
- 但过度 cherry-pick 会让分支关系变复杂。


常见坑/追问：


- 需要关注依赖提交是否一起带过去。


### Q7: 🔴 如何理解“干净历史”和“真实历史”的权衡？


A: 结论：干净历史便于阅读和回溯，真实历史保留协作过程；团队要根据 review、审计、故障排查需求选平衡点。


详细解释：


- 有些团队偏好 squash merge，提交历史像整理后的笔记。
- 有些团队保留 merge commit，更像完整施工记录。


常见坑/追问：


- 重点不是工具站队，而是团队约定一致。


### Q8: 🟢 你会如何向面试官解释一个规范的 Git 工作流？


A: 结论：基于主干/发布分支建立功能分支开发，提交前自测，PR review，通过后合并，并对 release/hotfix 有明确策略。


详细解释：


- 功能开发走 feature branch。
- 紧急问题有 hotfix 流程。
- 合并策略、命名规范、CI 门禁要统一。


常见坑/追问：


- 工具不重要，关键是“可追溯、可回滚、少冲突”。


### Q9: ⭐🟡 git stash 的用途和常见操作有哪些？


A: 结论：`git stash` 将工作区和暂存区的未提交变更临时保存起来，让你能切换分支或处理紧急任务，之后用 `stash pop` 恢复。


详细解释：


- `git stash`：保存当前脏工作区，栈结构，支持多次保存。
- `git stash list`：查看所有暂存快照。
- `git stash pop`：恢复最近一次并删除记录，`apply` 则保留记录。
- `git stash push -m "描述"`：给 stash 加备注，便于识别。


代码示例：


```bash
git stash push -m "feat: 半完成的协议解析"
git checkout main       # 切去修紧急 bug
# ... 修完提交后 ...
git checkout feature/protocol
git stash pop
```


常见坑/追问：


- 追问：untracked 文件默认不会被 stash，需要加 `-u` 参数。
- stash pop 遇到冲突需手动解决，解决后 `git stash drop` 删除旧记录。


### Q10: ⭐🟡 git cherry-pick 是什么？什么时候用？


A: 结论：`cherry-pick` 将指定提交复制到当前分支，适合把一个分支上的某个独立修复"摘"到另一个分支，而不想合并全部历史。


详细解释：


- 常见场景：hotfix 分支上修了一个 bug，需要同步到 develop 分支，但不想 merge 全部 hotfix 内容。
- 可以指定单个或多个提交：`git cherry-pick <sha1> <sha2>`。
- cherry-pick 会生成新的提交 sha，与原提交内容相同但 id 不同。


代码示例：


```bash
git checkout develop
git cherry-pick a1b2c3d    # 把 hotfix 的修复摘过来
# 遇到冲突
git cherry-pick --continue
```


常见坑/追问：


- 追问：cherry-pick 的提交依赖其他提交时容易产生冲突，需要理解依赖链。
- 频繁 cherry-pick 同一内容到多个分支是维护成本信号，考虑是否需要重新设计分支策略。


### Q11: ⭐🟡 什么是 git submodule？使用中有哪些注意点？


A: 结论：submodule 让一个 Git 仓库内嵌另一个仓库，用于依赖第三方库或共享内部组件，但操作比普通 repo 更繁琐，团队需要统一使用姿势。


详细解释：


- 添加：`git submodule add <url> <path>`，在 `.gitmodules` 记录映射。
- 克隆含 submodule 的仓库：`git clone --recurse-submodules <url>` 或之后 `git submodule update --init --recursive`。
- 更新子模块：进入子模块目录 pull，再在父仓库 `git add` + commit。


代码示例：


```bash
# 添加第三方库
git submodule add https://github.com/nlohmann/json.git third_party/json

# 克隆并初始化
git clone --recurse-submodules https://repo.git

# 更新子模块到最新
git submodule update --remote --merge
```


常见坑/追问：


- 最常见坑：clone 后忘记 `--recurse-submodules`，子模块目录是空的。
- submodule 指向固定 commit，不会自动跟随上游更新，需手动升级。


### Q12: 🟡 如何用 git bisect 快速定位引入 bug 的提交？


A: 结论：`git bisect` 用二分查找自动在提交历史中定位第一个引入问题的提交，适合"某版本之后出 bug 但不知道哪次提交引入"的场景。


详细解释：


- 流程：标记一个好版本和一个坏版本，git 自动 checkout 中间版本，你测试后标记 good/bad，不断二分直到定位目标提交。
- 可配合脚本自动化：`git bisect run ./test.sh`，脚本退出码 0 = good，非 0 = bad。


代码示例：


```bash
git bisect start
git bisect bad HEAD            # 当前版本有问题
git bisect good v1.2.0         # v1.2.0 是好的
# git 自动 checkout 中间提交
# 测试后标记
git bisect good                # 或 git bisect bad
# 找到后会输出第一个坏提交
git bisect reset               # 还原 HEAD
```


常见坑/追问：


- 追问：如果"好版本"选得太旧，二分次数多但不影响正确性，只是慢一些。


### Q13: 🟡 tag 的作用是什么？轻量 tag 和注释 tag 有什么区别？


A: 结论：tag 是对某个提交的稳定引用，常用于标记版本发布；轻量 tag 只是个指针别名，注释 tag 是独立 Git 对象，包含作者、时间和签名信息。


详细解释：


- 轻量 tag：`git tag v1.0.0`，就是一个指向 commit 的引用，不附带额外信息。
- 注释 tag：`git tag -a v1.0.0 -m "Release 1.0.0"`，创建 tag 对象，可包含签名，适合正式发版。
- tag 不会随 push 自动推送，需要显式 `git push origin v1.0.0` 或 `git push --tags`。


代码示例：


```bash
git tag -a v2.1.0 -m "Fix OTA state machine crash"
git push origin v2.1.0

# 查看 tag 详情
git show v2.1.0
```


常见坑/追问：


- 追问：如何删除已推送的远程 tag？`git push origin :refs/tags/v1.0.0`（注意：会影响已拉取此 tag 的其他人）。


### Q14: ⭐🔴 如何设计一个适合 C++/Qt 上位机项目的 Git 分支策略？


A: 结论：根据团队规模和发布节奏选合适策略，小团队可用简化 GitFlow（main + develop + feature/hotfix），核心原则是主干稳定、功能隔离、发布有标记。


详细解释：


- `main`：只存稳定发布版本，每次发版打 tag。
- `develop`：日常集成分支，feature 分支从这里拉，合并回这里。
- `feature/*`：功能开发，完成后 PR/MR 合并到 develop，review 通过再合。
- `hotfix/*`：紧急修复，从 main 拉出，修完同时合到 main 和 develop。
- CI/CD：develop 自动跑编译+单元测试，main 触发打包和版本发布。


常见坑/追问：


- 追问：Trunk-Based Development 是什么？小团队短周期发布可直接基于 main 开发，频繁合并，用 feature flag 控制功能开关。
- 上位机项目要注意版本与设备固件版本的对应关系，分支/tag 要能还原任意历史版本。


### Q15: ⭐🔴 如何处理 git 历史中的敏感信息泄露（如密码、密钥）？


A: 结论：一旦敏感信息进入提交历史，必须从历史中彻底清除（`git filter-repo`），并立刻轮换泄露的凭证，不能仅靠删除文件了事。


详细解释：


- 仅删除文件并 commit：历史中仍可 `git show <old-sha>` 看到内容，等于没删。
- 正确清除：用 `git filter-repo --path <file> --invert-paths` 重写全部历史，或 BFG Repo Cleaner。
- 清除后所有人必须重新 clone，不能 pull（因为历史已改写）。
- 更重要：立刻轮换泄露的 API key、数据库密码等。


代码示例：


```bash
# 安装 git-filter-repo
pip install git-filter-repo

# 从所有历史中删除含密钥的文件
git filter-repo --path config/secrets.json --invert-paths

# 强制推送（需要 bypass 保护规则）
git push origin --force --all
```


常见坑/追问：


- 预防手段：`.gitignore` 忽略配置文件、使用 `.env` + 环境变量、pre-commit hook 扫描敏感字符串（如 `detect-secrets`）。
- 追问：GitHub 自动扫描推送的 commit 是否含已知格式的 token，发现会通知开发者，但仍需主动处理。
