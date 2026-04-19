# 19. CMake 构建系统


↑ 回到目录


### Q1: ⭐🟢 CMake 是什么？它和 Make 有什么关系？


A: 结论：CMake 是跨平台构建生成工具，不直接编译代码，而是根据 `CMakeLists.txt` 生成 Makefiles、Ninja、Visual Studio 工程等。Make 是它可能生成的后端之一。


详细解释：


- CMake 负责描述项目结构、依赖、目标、选项。
- 生成器可以是 `Unix Makefiles`、`Ninja`、`Visual Studio`。
- 现代 CMake 更强调 target-based 用法。


常见坑/追问：


- 不要说“CMake 就是 make 的升级版”，它们不是同层工具。
- 追问：为什么很多项目更推荐 Ninja？速度快、增量构建体验好。


### Q2: ⭐🟡 add_executable、add_library、target_link_libraries 各干什么？


A: 结论：`add_executable` 定义可执行目标，`add_library` 定义库目标，`target_link_libraries` 声明链接依赖。现代 CMake 的核心思路是围绕 target 组织属性。


详细解释：


- target 是现代 CMake 的中心。
- 编译选项、包含目录、宏定义都应该尽量绑到 target 上。
- 这样依赖传播更明确，可维护性更高。


代码示例：


```cmake
add_library(core STATIC core.cpp)
add_executable(app main.cpp)
target_link_libraries(app PRIVATE core)
```


常见坑/追问：


- 别再到处堆全局 `include_directories()`、`link_libraries()` 了。
- 追问：`PRIVATE/PUBLIC/INTERFACE` 是什么？见下一题。


### Q3: ⭐🔴 PRIVATE、PUBLIC、INTERFACE 怎么理解？


A: 结论：它们描述的是“这个属性对自己生效，还是也传播给依赖者”。这是现代 CMake 高频必问点。


详细解释：


- `PRIVATE`：只当前 target 使用。
- `PUBLIC`：当前 target 使用，同时传播给依赖它的 target。
- `INTERFACE`：当前 target 自己不用，只传播给使用者。
- 适用于 include dirs、compile defs、compile options、link libs 等。


代码示例：


```cmake
target_include_directories(core
    PUBLIC include
    PRIVATE src
)
```


常见坑/追问：


- 搞反传播范围会导致下游编译不过或意外污染编译环境。
- 追问：头文件里暴露的依赖应该怎么标？通常是 PUBLIC。


### Q4: ⭐🟡 为什么推荐 out-of-source build？


A: 结论：因为把构建产物和源码分离，可以保持源码目录干净，便于多配置并存、清理构建、IDE 集成和 CI 管理。


详细解释：


- 常见目录：`cmake -S . -B build`。
- 可同时存在 `build-debug`、`build-release`。
- 避免把生成文件污染仓库。


代码示例：


```bash
cmake -S . -B build -G Ninja
cmake --build build
```


常见坑/追问：


- in-source build 容易把缓存、对象文件、自动生成文件混进源码树。
- 追问：怎么彻底清理？删整个 build 目录通常最干净。


### Q5: ⭐🟡 find_package 是怎么工作的？


A: 结论：`find_package` 用来查找外部依赖包，优先使用 package config 模式，找到后通常提供导入目标（imported targets）供链接使用。


详细解释：


- 两种常见模式：Module mode、Config mode。
- 现代生态更推荐 `&lt;Pkg&gt;Config.cmake`。
- 找到包后常见用法：`target_link_libraries(app PRIVATE Qt6::Core)`。


代码示例：


```cmake
find_package(Qt6 REQUIRED COMPONENTS Core Widgets)
target_link_libraries(app PRIVATE Qt6::Core Qt6::Widgets)
```


常见坑/追问：


- 找不到包时要查 `CMAKE_PREFIX_PATH`、安装位置、版本是否匹配。
- 追问：为什么 imported target 比手写 include/lib 路径好？因为它自带依赖和属性传播。


### Q6: 🟡 target_include_directories 和 include_directories 有什么差别？


A: 结论：前者是 target-based、范围明确、可传播；后者是目录级全局设置，容易造成污染。现代 CMake 优先前者。


详细解释：


- `include_directories()` 会影响当前目录及子目录目标。
- `target_include_directories()` 只影响指定 target，控制粒度更好。
- 大项目里全局 include 非常容易制造头文件冲突。


常见坑/追问：


- 面试官如果问“现代 CMake”和“旧式 CMake”区别，这就是核心点之一。
- 追问：宏定义和编译选项也一样吗？对，优先 `target_compile_definitions`、`target_compile_options`。


### Q7: ⭐🟡 Debug/Release 构建一般怎么控制？


A: 结论：单配置生成器常通过 `CMAKE_BUILD_TYPE` 控制；多配置生成器如 Visual Studio、Xcode 则在构建时选择配置。不要混着理解。


详细解释：


- 单配置：`-DCMAKE_BUILD_TYPE=Debug`。
- 多配置：生成阶段不固定，构建时 `--config Release`。
- 不同配置下优化级别、宏、符号信息都可能不同。


代码示例：


```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build
```


常见坑/追问：


- Ninja Multi-Config 是个例外，需要看生成器。
- 追问：为什么 release 崩溃 debug 不崩？优化、未定义行为、时序都会放大差异。


### Q8: ⭐🔴 Qt 项目用 CMake 时 AUTOMOC/AUTOUIC/AUTORCC 是什么？


A: 结论：它们是 CMake 对 Qt 元对象、UI 文件、资源文件自动处理的机制。启用后不用手动写大量 MOC/UIC/RCC 规则。


详细解释：


- `AUTOMOC` 处理 `Q_OBJECT` 等需要 moc 的文件。
- `AUTOUIC` 处理 `.ui`。
- `AUTORCC` 处理 `.qrc`。
- Qt6 通常还有更现代的 `qt_add_executable`、`qt_add_library` 帮你收敛这些细节。


代码示例：


```cmake
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)
```


常见坑/追问：


- 新增带 `Q_OBJECT` 的头文件后没被 CMake 纳入源列表，仍可能导致链接找不到 vtable。
- 追问：为什么会报 undefined reference to vtable？通常是 moc 没跑到或实现缺失。


### Q9: 🟡 安装（install）和导出（export/package）怎么理解？


A: 结论：`install()` 定义构建产物如何安装到目标目录；导出/打包则是让别的项目能通过 `find_package` 使用你的库。工程化项目里这很重要。


详细解释：


- 安装内容可能包括 bin、lib、include、config 文件。
- 若想给别人复用，应生成 `&lt;Pkg&gt;Config.cmake` 和 targets 文件。
- 这能让下游项目无脑 `find_package(YourLib)`。


常见坑/追问：


- 只会本地编译，不会安装/导出，在库项目面试里会扣分。
- 追问：为什么大公司内部基础库很看重这个？因为依赖复用和 CI/CD 分发都靠它。


### Q10: ⭐🔴 CMake 最重要的实践原则是什么？


A: 结论：最重要原则是 target-based、声明式、少写全局变量黑魔法。越现代的 CMake，越像“给目标声明属性”，而不是“拼命操作字符串变量”。


详细解释：


- 围绕 target 写：include、lib、defs、options 都挂 target。
- 优先 imported targets 而非手写路径。
- 少用 directory-scope/global-scope 污染。
- 把构建逻辑写清楚，不要塞复杂 shell 魔法。


常见坑/追问：


- CMake 最大痛点往往不是它差，而是项目里保留了十年前的写法。
- 追问：怎么看一个 CMakeLists 是否现代？看它是不是以 target 为中心组织。


### Q11: ⭐⭐🟡 CPack 打包是什么？怎么用它生成安装包？


A: 结论：CPack 是 CMake 内置的打包工具，能根据平台生成 DEB/RPM/NSIS/ZIP 等安装包，只需在 CMakeLists 里配置即可，是 Qt 桌面应用常见的部署方式。


详细解释：


- 在 `install()` 规则定义好后，通过 `include(CPack)` 启用打包。
- 常用生成器：`DEB`、`RPM`、`NSIS`（Windows 安装向导）、`ZIP`。


代码示例：


```cmake
set(CPACK_PACKAGE_NAME "MyApp")
set(CPACK_PACKAGE_VERSION "1.2.0")
set(CPACK_GENERATOR "DEB;ZIP")
include(CPack)
```


```bash
cmake --build build
cpack --config build/CPackConfig.cmake
```


常见坑/追问：


- NSIS 打包需要安装 NSIS 工具；DEB 打包要注意依赖声明。
- 追问：Qt 程序打包还需要打包哪些 Qt 共享库？可用 `windeployqt` / `linuxdeployqt` 辅助收集依赖。


### Q12: ⭐⭐🟡 CMake 中如何管理第三方依赖（FetchContent vs submodule）？


A: 结论：`FetchContent` 在构建期自动拉取依赖，更自动化；git submodule 更显式可控。现代项目倾向 FetchContent 或 vcpkg/conan 包管理器。


代码示例：


```cmake
include(FetchContent)
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.2
)
FetchContent_MakeAvailable(nlohmann_json)
target_link_libraries(app PRIVATE nlohmann_json::nlohmann_json)
```


常见坑/追问：


- 需要网络访问，CI 环境要预热缓存或用 mirror。
- 追问：offline 环境怎么办？用 `SOURCE_DIR` 指向本地已有代码，或用 vcpkg local port。
