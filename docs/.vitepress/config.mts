import { defineConfig } from 'vitepress'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  vite: {
    plugins: [
      VitePWA({
        registerType: 'autoUpdate',
        outDir: '.vitepress/dist',
        includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'pwa-192x192.png', 'pwa-512x512.png'],
        manifest: {
          name: 'C++ / Qt 面试题库',
          short_name: 'CppQt面试',
          description: '覆盖 C++11~20 / Qt5&6 / Linux / 通信 / 工程化，600+ 题目',
          theme_color: '#646cff',
          background_color: '#ffffff',
          display: 'standalone',
          lang: 'zh-CN',
          icons: [
            { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
            { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
            { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' }
          ]
        },
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
          navigateFallback: null,
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'google-fonts-cache',
                expiration: { maxEntries: 10, maxAgeSeconds: 31536000 },
                cacheableResponse: { statuses: [0, 200] }
              }
            }
          ]
        }
      })
    ]
  },
  title: 'C++ / Qt 面试题库',
  description: '覆盖 C++11~20 / Qt5&6 / Linux / 通信 / 工程化',
  base: '/cpp-qt-interview/',

  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '学习路线', link: '/guide/00-roadmap' },
      { text: 'C++ 核心', link: '/guide/02-cpp11-14-17' },
      { text: 'Qt 框架', link: '/guide/01-qt-basics' },
      { text: '并发/线程', link: '/guide/07-concurrency' },
    ],

    sidebar: [
      {
        text: '🗺️ 学习路线',
        items: [{ text: '如何使用本题库', link: '/guide/00-roadmap' }]
      },
      {
        text: 'C++ 核心',
        collapsed: false,
        items: [
          { text: '2. C++11/14/17 新特性', link: '/guide/02-cpp11-14-17' },
          { text: '3. C++ 核心基础', link: '/guide/03-cpp-core' },
          { text: '4. 多态与虚函数', link: '/guide/04-polymorphism' },
          { text: '5. virtual 关键字', link: '/guide/05-virtual' },
          { text: '15. 智能指针深入', link: '/guide/15-smart-pointers' },
          { text: '20. 模板与泛型', link: '/guide/20-templates' },
          { text: '21. C++20 新特性', link: '/guide/21-cpp20' },
          { text: '22. STL 深入', link: '/guide/22-stl' },
          { text: '23. 移动语义', link: '/guide/23-move-semantics' },
          { text: '24. 异常处理', link: '/guide/24-exceptions' },
          { text: '25. 内存模型与原子操作', link: '/guide/25-memory-model' },
          { text: '26. 编译链接与 ABI', link: '/guide/26-compile-link-abi' },
        ]
      },
      {
        text: 'Qt 框架',
        collapsed: false,
        items: [
          { text: '1. Qt 框架基础', link: '/guide/01-qt-basics' },
          { text: '6. Qt 核心机制', link: '/guide/06-qt-core' },
          { text: '9. Qt5 与 Qt6 区别', link: '/guide/09-qt5-qt6' },
          { text: '43. Qt Quick / QML', link: '/guide/43-qt-qml' },
        ]
      },
      {
        text: '并发/线程',
        collapsed: false,
        items: [
          { text: '7. 并发与并行', link: '/guide/07-concurrency' },
          { text: '8. 消息队列', link: '/guide/08-message-queue' },
          { text: '10. 线程池', link: '/guide/10-thread-pool' },
        ]
      },
      {
        text: '通信/协议',
        collapsed: false,
        items: [
          { text: '12. C++ 消息与通信', link: '/guide/12-messaging' },
          { text: '13. CRC 校验', link: '/guide/13-crc' },
          { text: '18. 串口与 USB/HID', link: '/guide/18-serial-usb-hid' },
          { text: '42. 嵌入式通信协议', link: '/guide/42-embedded-protocol' },
        ]
      },
      {
        text: 'Linux/工程化',
        collapsed: false,
        items: [
          { text: '16. Linux 系统编程', link: '/guide/16-linux-programming' },
          { text: '17. Linux 命令与调试', link: '/guide/17-linux-commands' },
          { text: '19. CMake 构建系统', link: '/guide/19-cmake' },
          { text: '30. Git 与版本控制', link: '/guide/30-git' },
        ]
      },
      {
        text: '系统设计',
        collapsed: false,
        items: [
          { text: '14. 设计模式', link: '/guide/14-design-patterns' },
          { text: '31. 软件工程与设计原则', link: '/guide/31-software-engineering' },
          { text: '32. 场景设计题', link: '/guide/32-scenario-design' },
        ]
      },
      {
        text: '项目/面试',
        collapsed: false,
        items: [
          { text: '33. 项目经验问答', link: '/guide/33-project-experience' },
          { text: '34. 面试实战技巧', link: '/guide/34-interview-skills' },
          { text: '35. 高频综合题', link: '/guide/35-comprehensive' },
        ]
      },
      {
        text: '扩展领域',
        collapsed: false,
        items: [
          { text: '11. C++ 加密体系', link: '/guide/11-crypto' },
          { text: '27. 性能优化', link: '/guide/27-performance' },
          { text: '28. 网络编程', link: '/guide/28-networking' },
          { text: '29. 数据库基础', link: '/guide/29-database' },
          { text: '36. GIS 基础', link: '/guide/36-gis' },
          { text: '37. Redis 原理', link: '/guide/37-redis' },
          { text: '38. 卡尔曼滤波', link: '/guide/38-kalman' },
          { text: '39. PID 控制', link: '/guide/39-pid' },
          { text: '40. C++ 与 C# 对比', link: '/guide/40-cpp-csharp' },
          { text: '41. Electron 跨平台对比', link: '/guide/41-electron' },
          { text: '44. 调试与性能分析', link: '/guide/44-debugging-profiling' },
          { text: '45. 跨平台桌面开发实践', link: '/guide/45-cross-platform' },
        ]
      },
    ],

    search: {
      provider: 'local'
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/Quantum505Void/cpp-qt-interview' }
    ],

    footer: {
      message: 'C++ / Qt 桌面开发工程师面试题库',
    }
  },
})
