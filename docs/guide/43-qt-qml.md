# 43. Qt Quick / QML 开发


↑ 回到目录


### Q1: ⭐🟢 QML 和 Qt Widgets 的核心区别是什么？


A: 结论：QML 是声明式 UI 语言，适合流畅动画和现代界面；Qt Widgets 是命令式，适合传统桌面工具软件。两者可以在同一项目中混用。


详细解释：


- QML 基于 JavaScript，语法简洁，支持属性绑定和动画。
- Qt Widgets 原生外观、控件丰富、文档成熟，更适合企业内部工具。
- 混用方式：通过 `QQuickWidget` 把 QML 嵌入 Widgets，或用 `QWidget::createWindowContainer` 把 Widgets 嵌入 QML。


常见坑/追问：


- QML 不是"更高级"——场景不对，反而带来更高复杂度和调试成本。
- QML 动画流畅依赖 GPU，低端嵌入式设备未必能流畅运行。


---


### Q2: ⭐🟢 QML 属性绑定是怎么工作的？有什么陷阱？


A: 结论：属性绑定是 QML 最核心的机制，一旦右侧表达式依赖的属性改变，左侧属性自动更新。陷阱是绑定被赋值破坏（binding broken）。


详细解释：


```qml
// 绑定：width 随 parent.width 变化
width: parent.width * 0.5

// 一旦这样写，绑定就断了：
Component.onCompleted: {
    width = 200  // 绑定被覆盖，之后 parent 变化不再更新 width
}

// 想恢复绑定，必须用 Qt.binding()
Component.onCompleted: {
    width = Qt.binding(function() { return parent.width * 0.5; })
}
```


常见坑/追问：


- 属性绑定中加 JS 逻辑越复杂，性能越差，应尽量保持绑定表达式简单。
- `Binding` 元素可以条件性地切换绑定。


---


### Q3: ⭐🟡 Qt Quick 的渲染架构是什么？Scene Graph 是什么？


A: 结论：Qt Quick 使用 Scene Graph（场景图）进行渲染，把 QML 元素转换为 GPU 可以直接渲染的节点树，在独立的渲染线程上运行。


详细解释：


- Scene Graph 节点树和 QML 对象树是两棵不同的树，前者供 GPU 渲染。
- Qt Quick 渲染默认在独立线程（Render Thread），主线程只负责逻辑。
- 自定义渲染用 `QSGNode` 子类或 `QQuickPaintedItem`（软件渲染，性能低）。
- Qt 6 引入 RHI（Rendering Hardware Interface），统一 OpenGL/Metal/Vulkan/D3D11 后端。


常见坑/追问：


- 在 Render Thread 上不能访问主线程 QObject，需要通过信号槽或 `QMetaObject::invokeMethod`。
- `QQuickPaintedItem` 用 QPainter 绘制，不走 GPU，性能明显低于 `QSGNode`。


---


### Q4: ⭐🟡 QML 中 C++ 对象怎么暴露给 QML 使用？


A: 结论：有三种主流方式：注册类型、设置上下文属性、单例注册。


详细解释：


```cpp
// 方式 1：注册 QML 类型（推荐，类型安全）
qmlRegisterType<MyClass>("com.example", 1, 0, "MyClass");
// QML 中：import com.example 1.0; MyClass { ... }

// 方式 2：上下文属性（全局对象，快速但不类型安全）
engine.rootContext()->setContextProperty("myObj", &obj);
// QML 中直接用 myObj.someMethod()

// 方式 3：单例（Qt 5.14+）
qmlRegisterSingletonInstance("com.example", 1, 0, "MySingleton", &obj);
```


常见坑/追问：


- 上下文属性没有类型信息，QML 工具链无法做代码补全和静态检查。
- Qt 6 推荐用 `QML_ELEMENT` / `QML_SINGLETON` 宏配合 CMake 自动注册。


---


### Q5: ⭐🟡 QML 中的 `Component.onCompleted` 和 `onDestruction` 有什么用？


A: 结论：`Component.onCompleted` 是对象完全创建后的初始化钩子；`Component.onDestruction` 是对象销毁前的清理钩子。


详细解释：


```qml
Rectangle {
    Component.onCompleted: {
        console.log("Rectangle 创建完成，可以安全访问子对象")
        myTimer.start()
    }
    Component.onDestruction: {
        console.log("即将销毁，清理资源")
        myTimer.stop()
    }
}
```


常见坑/追问：


- 在构造函数（`onCompleted` 之前）访问子对象是不安全的，子对象可能还没初始化。
- 动态创建的组件（`Loader`、`createObject`）也有独立的 `onCompleted`。


---


### Q6: ⭐🟡 Loader 是什么？什么场景用它？


A: 结论：`Loader` 用于动态加载/卸载 QML 组件，实现按需加载，减少启动开销。


详细解释：


```qml
Loader {
    id: myLoader
    source: showDetail ? "DetailView.qml" : ""
    asynchronous: true  // 异步加载，不阻塞 UI

    onLoaded: {
        item.someProperty = value  // 访问加载后的对象
    }
}
```


常见坑/追问：


- `asynchronous: true` 时，`item` 在 `onLoaded` 之前为 null，不能直接访问。
- `Loader` 卸载时（`source: ""`），被加载的对象会被销毁，注意信号连接失效。
- 频繁切换 source 性能差，可以用 `visible` 配合 `active` 控制显隐而不销毁。


---


### Q7: ⭐🟡 QML 中怎么做动画？主要有哪几种方式？


A: 结论：QML 提供 `NumberAnimation`、`Behavior`、`Transition`、`SequentialAnimation`、`ParallelAnimation` 等，分别适合不同场景。


详细解释：


```qml
// 1. 直接动画
NumberAnimation on x {
    to: 200; duration: 500; easing.type: Easing.OutBounce
}

// 2. Behavior（属性变化时自动触发）
Behavior on opacity {
    NumberAnimation { duration: 300 }
}

// 3. State + Transition（状态机）
states: State { name: "expanded"; PropertyChanges { target: rect; height: 200 } }
transitions: Transition {
    to: "expanded"
    NumberAnimation { properties: "height"; duration: 300 }
}
```


常见坑/追问：


- `Behavior` 会拦截所有属性赋值，包括初始化，有时会导致意外动画。
- 动画过多会占用 GPU，低端设备注意 `smooth: false` 或减少同时运行的动画数。


---


### Q8: ⭐🟡 QML 的内存管理机制是什么？什么时候会内存泄漏？


A: 结论：QML 对象遵循 Qt 父子内存管理，同时有 JavaScript 引擎的 GC。泄漏常见原因是循环引用或 JS 对象持有 QML 对象引用阻止 GC。


详细解释：


- 有父对象的 QML 元素（`parent` 属性），父销毁时子自动销毁。
- 用 `Qt.createComponent` / `createObject` 动态创建、没有父的对象，需手动 `destroy()`。
- JS 闭包持有 QML 对象引用，会阻止 GC 回收。


常见坑/追问：


- `Repeater`、`ListView` 等列表控件会自动管理委托对象的生命周期，不要手动 destroy 委托。
- 动态创建对象时给 `parent` 参数，避免孤儿对象。


---


### Q9: ⭐🟡 ListView 和 GridView 的 delegate 生命周期是怎样的？


A: 结论：ListView 采用虚拟化（virtualization），只创建可见区域的 delegate，滚出可视范围的 delegate 会被回收复用。


详细解释：


- `cacheBuffer`：额外预创建视口外的 delegate 数量，提升滚动流畅度。
- delegate 被回收时不销毁（放入缓存池），再次进入视口时重新赋值 `model` 数据。
- delegate 内部不要保存不属于 model 的状态，因为回收后状态会乱。


```qml
ListView {
    model: myModel
    cacheBuffer: 200  // 预缓存 200px 范围的 delegate
    delegate: Rectangle {
        // 不要在这里存 local state，应写回 model
        color: model.selected ? "blue" : "white"
    }
}
```


常见坑/追问：


- `model.index` 在复用时会变，别用它做唯一标识。
- 大量 delegate 使用复杂 JS 逻辑，会导致滚动卡顿。


---


### Q10: ⭐🔴 如何在 Qt Quick 中自定义 QSGNode 实现高性能自定义渲染？


A: 结论：继承 `QQuickItem`，重写 `updatePaintNode()`，在其中构建/更新 `QSGNode` 子树，直接与 GPU 交互，性能远高于 `QQuickPaintedItem`。


详细解释：


```cpp
class MyItem : public QQuickItem {
    Q_OBJECT
public:
    MyItem(QQuickItem *parent = nullptr) : QQuickItem(parent) {
        setFlag(ItemHasContents, true);  // 必须设置
    }

protected:
    QSGNode *updatePaintNode(QSGNode *old, UpdatePaintNodeData *) override {
        QSGGeometryNode *node = static_cast<QSGGeometryNode *>(old);
        if (!node) {
            node = new QSGGeometryNode;
            auto *geometry = new QSGGeometry(QSGGeometry::defaultAttributes_Point2D(), 3);
            geometry->setDrawingMode(QSGGeometry::DrawTriangles);
            node->setGeometry(geometry);
            node->setFlag(QSGNode::OwnsGeometry);

            auto *material = new QSGFlatColorMaterial;
            material->setColor(Qt::red);
            node->setMaterial(material);
            node->setFlag(QSGNode::OwnsMaterial);
        }
        // 更新几何数据...
        return node;
    }
};
```


常见坑/追问：


- `updatePaintNode` 在 Render Thread 执行，不能访问主线程数据，需在 `updatePaintNode` 调用前从主线程拷贝数据（通过成员变量）。
- 调用 `update()` 触发重绘，不要频繁调用，只在数据真正变化时调用。


---


### Q11: ⭐🟡 QML 中的 Model/View 架构是怎么用的？


A: 结论：QML 提供 `ListModel`（纯 QML 数据）和 C++ 的 `QAbstractItemModel` 子类（复杂数据），View 通过 `model` 属性绑定，用 `delegate` 描述每项渲染。


详细解释：


```qml
// 简单场景：ListModel
ListModel {
    id: fruitModel
    ListElement { name: "Apple"; cost: 2.45 }
    ListElement { name: "Banana"; cost: 1.95 }
}
ListView {
    model: fruitModel
    delegate: Text { text: name + " - " + cost }
}

// 复杂场景：C++ Model（推荐）
// C++ 继承 QAbstractListModel，重写 rowCount/data/roleNames
engine.rootContext()->setContextProperty("myModel", &cppModel);
```


常见坑/追问：


- `ListModel` 没有类型安全，字段名拼错不报错，适合原型。
- C++ Model 通过 `roleNames()` 映射角色名到 QML 属性名，`data()` 通过 `role` 返回对应数据。
- 数据更新要调用 `beginInsertRows`/`endInsertRows` 等方法，否则 View 不刷新。


---


### Q12: ⭐🟡 QML 的信号和 C++ 的信号槽怎么互通？


A: 结论：QML 信号可以连接到 C++ 槽，C++ 信号也可以连接到 QML 函数，两者通过元对象系统打通。


详细解释：


```qml
// QML 信号 → C++ 槽（在 C++ 中连接）
QObject::connect(rootObject, SIGNAL(qmlSignal(QString)),
                 &cppObj, SLOT(onQmlSignal(QString)));

// C++ 信号 → QML 函数（在 QML 中连接）
Connections {
    target: cppObj  // 通过 context property 暴露的对象
    function onDataChanged(value) {
        console.log("C++ 发来:", value)
    }
}
```


常见坑/追问：


- `Connections` 的目标必须是 QObject，且信号名大小写必须和 C++ 一致。
- Qt 6 中 `Connections` 语法变为 `function on<SignalName>()` 形式，旧的 `on<SignalName>: handler` 仍有效但不推荐。


---


### Q13: ⭐🟢 QML 中 `id` 和 `objectName` 有什么区别？


A: 结论：`id` 是 QML 作用域内的局部引用，只在 QML 文件内有效；`objectName` 是字符串属性，供 C++ 通过 `findChild` 查找用。


详细解释：


```qml
Rectangle {
    id: myRect        // QML 内部引用，JS 里直接用 myRect.xxx
    objectName: "mainRect"  // C++ 可以 findChild<QObject*>("mainRect")
}
```


常见坑/追问：


- `id` 不能重复，编译时报错；`objectName` 可以重复，`findChild` 返回第一个匹配的。
- 不要把 `id` 暴露给 C++ 使用，正确方式是 `objectName` 或直接通过属性绑定通信。


---


### Q14: ⭐🟡 Qt Quick Controls 2 和 Qt Quick Controls 1 的区别是什么？


A: 结论：Qt Quick Controls 2（QQC2）完全重写，性能更高、更适合移动和嵌入式，支持样式切换；Controls 1 已在 Qt 6 中移除。


详细解释：


- QQC2 每个控件极简，样式（style）与逻辑分离，切换主题只改 style。
- 内置样式：`Material`、`Universal`、`Fusion`、`Imagine`、`Basic`。
- 嵌入式设备推荐 `Basic` 或自定义 style，减少渲染开销。


常见坑/追问：


- QQC2 的 `ApplicationWindow` 必须是根对象，否则菜单、对话框定位会出问题。
- 自定义 Button 样式不是继承，而是通过 `background`/`contentItem`/`indicator` 等 attached 属性替换。


---


### Q15: ⭐🔴 QML 性能优化有哪些常见手段？


A: 结论：减少绑定复杂度、用 `visible` 代替 `opacity: 0`、懒加载、避免过度 anchors 嵌套、用 `TableView` 代替大量 `Repeater`。


详细解释：


| 优化点 | 说明 |
|--------|------|
| 简化绑定表达式 | 绑定中 JS 越少越好，复杂逻辑移到 C++ |
| `visible: false` vs `opacity: 0` | `visible: false` 跳过渲染；`opacity: 0` 仍然占用渲染资源 |
| Loader + `asynchronous` | 按需懒加载，避免启动时全量创建 |
| 减少 anchors 嵌套层级 | 深层 anchors 触发大量布局计算 |
| `clip: false`（默认） | 开启 clip 会强制 Scene Graph 做额外裁剪，能不开就不开 |
| `layer.enabled: true` | 把子树缓存为纹理，适合复杂静态 UI，但增加显存 |
| `TableView` 代替 `Column + Repeater` | 大列表必须虚拟化，Repeater 不虚拟化 |


常见坑/追问：


- `layer.enabled` 在动画时反而有额外开销（纹理合成），只在子树静态时使用。
- 用 Qt Quick Profiler（Qt Creator 内置）定位渲染瓶颈，不要靠猜。
