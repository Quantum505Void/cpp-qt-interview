# 36. GIS 基础与组件集成


↑ 回到目录


### Q1: ⭐🟢 GIS 中常见的坐标系有哪些？WGS84 和 CGCS2000 有什么区别？


A: 结论：WGS84 是 GPS 系统使用的全球地心坐标系，CGCS2000 是中国国家大地坐标系。两者椭球参数极为接近（差异在厘米级），日常工程中可近似等同，但高精度测绘必须区分。


详细解释：


- WGS84（World Geodetic System 1984）：美国国防部维护，GPS 卫星直接输出的坐标就是 WGS84。
- CGCS2000（China Geodetic Coordinate System 2000）：中国 2008 年启用，椭球长半轴 a=6378137m，扁率 1/298.257222101，与 WGS84 的扁率差异约 1e-9。
- 投影坐标系：将三维椭球面映射到二维平面，常见有 UTM（全球通用）、高斯-克吕格（中国测绘常用）。
- EPSG 编码：WGS84 地理坐标 = EPSG:4326，WGS84 Web 墨卡托 = EPSG:3857（地图瓦片标准）。


常见坑/追问：


- 百度/高德坐标是加密偏移后的（GCJ-02/BD-09），不能直接当 WGS84 用，需要纠偏。


### Q2: ⭐🟢 矢量数据和栅格数据的区别是什么？各自适合什么场景？


A: 结论：矢量数据用点/线/面几何对象表示空间要素，适合精确边界和属性查询；栅格数据用像素网格表示连续表面，适合遥感影像和地形分析。


详细解释：


- 矢量：Shapefile、GeoJSON、KML、PostGIS geometry。优点是缩放不失真、属性丰富、存储高效。
- 栅格：GeoTIFF、DEM、卫星影像。优点是表达连续场（高程、温度）自然，叠加分析方便。
- 实际项目中常混合使用：底图用栅格瓦片，业务图层用矢量叠加。


常见坑/追问：


- 矢量转栅格叫栅格化（rasterize），栅格转矢量叫矢量化（vectorize），两者都有信息损失。


### Q3: ⭐🟢 什么是地图瓦片？瓦片金字塔是怎么回事？


A: 结论：地图瓦片是将地图按固定大小（通常 256×256 像素）切割成小图片，按缩放级别组织成金字塔结构，实现快速加载和渲染。


详细解释：


- 金字塔：zoom=0 时整个世界 1 张瓦片，zoom=n 时有 4^n 张瓦片。
- 编址方式：TMS（{z}/{x}/{y}）或 Google/OSM 方案（y 轴方向相反）。
- 加载策略：视口范围计算需要的瓦片编号，异步请求，LRU 缓存已加载瓦片。
- 矢量瓦片（MVT/PBF）：传输矢量数据而非图片，客户端渲染，支持动态样式。


常见坑/追问：


- 瓦片缓存要考虑磁盘空间和过期策略，离线场景需要预下载瓦片包。


### Q4: ⭐🟡 GDAL/OGR 是什么？在 C++ 项目中怎么用？


A: 结论：GDAL 是处理栅格数据的开源库，OGR 是处理矢量数据的库，两者合并在 GDAL 项目中，是 GIS 领域的瑞士军刀。C++ 项目通过链接 libgdal 直接调用 C/C++ API。


详细解释：


- 栅格操作：`GDALOpen()` 打开 GeoTIFF → `GetRasterBand()` 获取波段 → `RasterIO()` 读写像素。
- 矢量操作：`GDALOpenEx()` 打开 Shapefile → `GetLayer()` → `GetNextFeature()` 遍历要素 → `GetGeometryRef()` 获取几何。
- 坐标转换：`OGRCoordinateTransformation` 配合 PROJ 库实现投影变换。
- CMake 集成：`find_package(GDAL REQUIRED)` + `target_link_libraries(... GDAL::GDAL)`。


常见坑/追问：


- GDAL 的数据集和要素对象需要手动释放（`GDALClose`/`OGRFeature::DestroyFeature`），或用 RAII 封装。


### Q5: ⭐🟡 在 Qt 应用中如何实现地图显示？有哪些技术方案？


A: 结论：主要三种方案——QGraphicsView 自绘矢量地图、QWebEngineView 嵌入 Web 地图（Leaflet/OpenLayers）、第三方 Qt 地图组件（如 QGeoView、osgEarth Qt 集成）。


详细解释：


- QGraphicsView 方案：将矢量要素转为 QGraphicsItem，支持缩放/平移/选择，性能好但开发量大。
- WebEngine 方案：嵌入 Leaflet/OpenLayers 网页，通过 `QWebChannel` 实现 C++ ↔ JS 双向通信，开发快但内存占用高。
- osgEarth：基于 OpenSceneGraph 的三维地球引擎，适合三维地形可视化。
- Qt Location 模块：Qt 自带的地图组件（QML MapView），但 Qt6 中功能有限。


常见坑/追问：


- WebEngine 方案要注意离线部署时瓦片源的替换，以及 JS 与 C++ 通信的异步性。


### Q6: ⭐🟡 空间索引是什么？R-Tree 和四叉树有什么区别？


A: 结论：空间索引是加速空间查询（范围查询、最近邻）的数据结构。R-Tree 用最小外接矩形（MBR）层层包围，适合动态数据；四叉树递归四分空间，适合均匀分布数据。


详细解释：


- R-Tree：每个节点存一组 MBR，查询时从根节点剪枝。变体有 R*-Tree（优化插入分裂策略）。PostGIS、SQLite/SpatiaLite 默认用 R-Tree。
- 四叉树：将二维空间递归分为四个象限，点数据效率高，但对长条形几何体不友好。
- 网格索引：最简单，按固定网格分桶，适合数据分布均匀且范围已知的场景。
- C++ 实现：Boost.Geometry 提供 R-Tree，libspatialindex 提供多种空间索引。


常见坑/追问：


- 空间索引只加速粗筛（候选集），精确判断（如多边形包含）仍需几何计算。


### Q7: ⭐🟡 NMEA 协议是什么？如何在 C++ 中解析 GPS 数据？


A: 结论：NMEA 0183 是 GPS 接收器输出定位数据的文本协议，每行以 `$` 开头，逗号分隔字段，`*` 后跟校验和。C++ 中按行读取串口数据，解析 `$GPGGA`/`$GPRMC` 等语句即可。


详细解释：


- `$GPGGA`：定位信息，含时间、纬度、经度、定位质量、卫星数、海拔。
- `$GPRMC`：推荐最小定位信息，含日期、速度、航向。
- 解析步骤：校验 checksum → 按逗号 split → 按字段位置提取 → 经纬度从 ddmm.mmmm 格式转十进制度。
- 校验和计算：`$` 和 `*` 之间所有字符异或。


常见坑/追问：


- 串口数据可能断帧，需要缓冲区拼接完整行；经纬度注意南纬/西经的负号处理。


### Q8: ⭐🟡 坐标转换在 C++ 中怎么实现？PROJ 库怎么用？


A: 结论：PROJ 是地理坐标转换的标准开源库，支持几千种坐标系互转。C++ 中通过 `proj_create_crs_to_crs()` 创建转换器，`proj_trans()` 执行转换。


详细解释：


- 基本流程：`PJ_CONTEXT ctx = proj_context_create()` → `PJ P = proj_create_crs_to_crs(ctx, "EPSG:4326", "EPSG:3857", NULL)` → `proj_trans(P, PJ_FWD, coord)`。
- 注意 PROJ 6+ 的 API 变化：废弃了 `pj_init_plus()` 等旧接口。
- 批量转换用 `proj_trans_array()` 效率更高。
- CMake：`find_package(PROJ REQUIRED)` + `target_link_libraries(... PROJ::proj)`。


常见坑/追问：


- PROJ 默认经纬度顺序可能是 lat/lon 而非 lon/lat，需要 `proj_normalize_for_visualization()` 调整。


### Q9: 🟡 如何在 Qt 应用中实现轨迹绘制和回放？


A: 结论：将 GPS 轨迹点按时间排序，在地图上用折线连接，回放时用定时器逐点推进标记位置，配合插值实现平滑动画。


详细解释：


- 数据结构：`QVector&lt;TrackPoint&gt;`，每个点含经纬度、时间戳、速度、航向。
- QGraphicsView 方案：轨迹用 `QGraphicsPathItem`，当前位置用可旋转的箭头 item。
- WebEngine 方案：JS 端用 Leaflet.Polyline + Leaflet.Marker，C++ 通过 WebChannel 推送坐标。
- 性能优化：轨迹点多时用 Douglas-Peucker 算法简化，或按缩放级别分层显示。


常见坑/追问：


- 回放速度控制要基于实际时间差而非固定间隔，否则匀速段和停留段体验不一致。


### Q10: 🟡 GIS 项目中如何处理海量空间数据的性能问题？


A: 结论：从数据分层分级、空间索引、视口裁剪、异步加载、缓存策略五个维度优化。


详细解释：


- 分层分级：不同缩放级别显示不同精度的数据（LOD），小比例尺只显示概要。
- 视口裁剪：只加载和渲染当前视口范围内的数据，用空间索引快速筛选。
- 异步加载：数据读取和解析放后台线程，主线程只负责渲染。
- 缓存：内存 LRU 缓存 + 磁盘持久缓存，瓦片和矢量数据分别缓存。
- 简化：大量多边形用 Visvalingam 或 Douglas-Peucker 简化后再渲染。


常见坑/追问：


- 简化算法要保证拓扑一致性，否则相邻多边形会出现缝隙。


### Q11: 🔴 如何设计一个支持离线地图的 Qt 桌面 GIS 应用？


A: 结论：核心是离线瓦片包 + 本地矢量数据 + 嵌入式空间数据库，配合在线/离线模式切换和增量同步机制。


详细解释：


- 瓦片离线：预下载目标区域指定层级的瓦片，存为 MBTiles（SQLite 格式）或文件目录。
- 矢量离线：Shapefile/GeoPackage 本地存储，GeoPackage 基于 SQLite 支持空间索引。
- 数据库：SpatiaLite（SQLite + 空间扩展）适合嵌入式场景，无需独立服务。
- 同步策略：在线时增量下载变更区域数据，离线编辑记录变更日志，上线后合并。
- 坐标转换：PROJ 的 grid shift 文件也需要离线打包。


常见坑/追问：


- 离线瓦片包体积可能很大（一个城市 zoom 0-16 可达数 GB），需要按需求裁剪范围和层级。


### Q12: 🔴 在 C++/Qt 中如何实现地理围栏（Geofence）功能？


A: 结论：地理围栏是判断移动目标是否进入/离开指定区域的功能。核心是点在多边形内判断算法（射线法/绕数法）+ 实时位置流 + 事件触发机制。


详细解释：


- 射线法（Ray Casting）：从目标点向任意方向发射线，与多边形边界交点为奇数则在内部，时间复杂度 O(n)。
- 绕数法（Winding Number）：计算多边形绕目标点的圈数，非零则在内部，对复杂多边形更准确。
- 优化：围栏多时先用 MBR 粗筛，再精确判断；围栏区域用空间索引组织。
- 事件模型：维护上一次状态（inside/outside），状态变化时触发 enter/exit 信号。
- GEOS 库：提供 `contains()`、`intersects()` 等空间关系判断，C++ 接口成熟。


常见坑/追问：


- GPS 漂移可能导致围栏边界附近频繁触发进出事件，需要加滞回（hysteresis）或时间窗口过滤。


### Q13: 🔴 如何将 GIS 功能与实时数据采集系统集成？


A: 结论：架构上分为数据采集层（串口/网络接收 GPS/传感器数据）、处理层（解析/滤波/坐标转换）、存储层（时序数据库/空间数据库）、展示层（地图可视化），各层通过消息队列解耦。


详细解释：


- 采集层：串口读 NMEA 或 TCP 接收设备数据，独立线程，生产者模式。
- 处理层：卡尔曼滤波平滑 GPS 跳变，坐标系转换，异常值剔除。
- 存储层：实时数据写 Redis（最新位置快速查询），历史轨迹写 PostgreSQL/PostGIS。
- 展示层：Qt 地图组件订阅位置更新信号，节流刷新（如 1Hz）。
- 告警：地理围栏 + 速度/状态异常检测，触发后通过信号槽或消息队列通知 UI。


常见坑/追问：


- 采集频率高时（10Hz+），地图渲染要做降采样，否则 UI 线程会被拖慢。


---


---


### Q14: 🟡 地图坐标系有哪些？WGS84、GCJ02、BD09 有什么区别？


A: 结论：WGS84 是国际标准 GPS 坐标系；GCJ02（国测局坐标/火星坐标）是中国官方加密坐标系，在 WGS84 基础上做了非线性偏移；BD09 是百度在 GCJ02 基础上再次加密的坐标系。三者在中国境内存在几十到几百米偏差，不同场景必须做坐标转换。


详细解释：


- WGS84：GPS 硬件直接输出，全球通用，OpenStreetMap、Google Maps（境外）使用。
- GCJ02：中国法规要求境内地图必须使用，高德地图、腾讯地图、Google Maps（境内）使用。
- BD09：百度地图专用，BD09 → GCJ02 → WGS84 逐层转换。
- 偏移量：因地区不同约 100m~500m，沿海和边境地区偏差更大。
- 坐标转换：开源算法 `coordtransform` 可实现三种坐标系互转，精度在 1 米以内。


代码示例（如有）：


```cpp
// WGS84 -> GCJ02 核心（简化示意）
// 真实算法见 coordtransform 开源库
struct LatLng { double lat, lng; };

LatLng wgs84ToGcj02(LatLng wgs) {
    if (isOutOfChina(wgs.lat, wgs.lng)) return wgs;
    double dLat = transformLat(wgs.lng - 105.0, wgs.lat - 35.0);
    double dLng = transformLng(wgs.lng - 105.0, wgs.lat - 35.0);
    // ... 椭球体修正计算
    return { wgs.lat + dLat, wgs.lng + dLng };
}
```


常见坑/追问：


- GPS 设备输出 WGS84，直接叠加到高德/腾讯底图会有偏移，必须先转 GCJ02。
- 追问：EPSG 编码是什么？是空间参考系统的国际标准编号，WGS84 = EPSG:4326，Web 墨卡托 = EPSG:3857。


### Q15: 🟡 什么是空间索引？R 树在 GIS 中如何应用？


A: 结论：空间索引是针对地理数据的加速查询结构，解决"哪些要素在给定区域内"的问题。R 树（R-tree）是最常用的空间索引，将空间对象按最小外接矩形（MBR）层次组织，支持范围查询、最近邻查询，PostGIS、SpatiaLite、GEOS 等都内置了 R 树实现。


详细解释：


- R 树结构：类似 B 树，每个节点存一组 MBR，子节点的 MBR 被父节点 MBR 包含。
- 范围查询：递归检查 MBR 与查询框是否重叠，只进入重叠子树，大幅减少检查数量。
- 最近邻查询：用优先队列按距离排序遍历节点，可高效找到 K 个最近对象。
- 变体：R* 树（更优的插入策略）、STR 打包（批量加载，适合只读数据集）。
- Qt/C++ 中的选择：可用 Boost.Geometry 的 `bgi::rtree`，或通过 GDAL/SpatiaLite 间接使用。


代码示例（如有）：


```cpp
// Boost.Geometry R 树示例
#include <boost/geometry/index/rtree.hpp>
namespace bgi = boost::geometry::index;
namespace bg  = boost::geometry;

using Point = bg::model::point<double, 2, bg::cs::cartesian>;
using Box   = bg::model::box<Point>;
using Value = std::pair<Box, int>; // MBR + 对象ID

bgi::rtree<Value, bgi::rstar<16>> rtree;

// 插入
Box mbr(Point(116.3, 39.9), Point(116.4, 40.0));
rtree.insert({mbr, 1001});

// 范围查询
Box queryBox(Point(116.0, 39.8), Point(116.5, 40.1));
std::vector<Value> results;
rtree.query(bgi::intersects(queryBox), std::back_inserter(results));
```


常见坑/追问：


- 频繁插入/删除会导致 R 树退化，需要定期重建（rebuild）。
- 追问：空间索引和普通 B 树索引的核心区别？普通 B 树处理一维有序数据；空间索引处理多维、无全序的空间对象，需要用 MBR 近似。
