# 从地产 485 到 Home Assistant 全屋联动：我做了什么，以及如何落地

这篇文档面向想把类似精装房智能家居系统接入 Home Assistant 的业主。

这里不会提供真实账号、网关序列号、MQTT topic、抓包 payload 或完整家庭配置。它讲的是一套可复用的落地思路：如何把一个原本封闭的地产 485 系统，接到 Home Assistant，再和米家、美的、Apple Home / Siri 等生态组合成日常可用的系统。

如果你想先理解上游作者拓扑里 OpenWrt、DNS 重定向、本地 MQTT bridge 的作用，可以先看 [`upstream-topology-notes.zh-CN.md`](upstream-topology-notes.zh-CN.md)。

## 我实际做了什么

这个项目不是单纯安装一个插件。实际落地里做了几层事情：

1. **接入地产 485 系统**
   使用上游 `origintree/hyqw_adapter` 作为 adapter，把地产交付的灯光、空调、地暖、窗帘、新风等设备实体化到 Home Assistant。

2. **搭建本地承载环境**
   使用 Mac mini 作为家里的常在线主机，把 Home Assistant 和周边服务放在 Docker 里运行，方便长期运行、重启、备份和迁移。

3. **修正真实部署中遇到的问题**
   在实际 Home Assistant 环境里发现 adapter 存在一些兼容性问题，例如硬编码校验值、`paho-mqtt` 2.x 兼容、MQTT 连接循环过早退出、HAR/base URL 假设等，并把问题反馈给上游。

4. **把米家设备纳入同一个控制平面**
   将米家 / Xiaomi Miot / Xiaomi Home 设备接入 Home Assistant，并用影子对比、历史观察和 fallback 的方式逐步迁移，不一次性替换所有实体。

5. **把美的等家电纳入可见状态**
   对美的 / 东芝等家电，不假设云端状态永远可靠，而是把 `unavailable`、状态延迟和完成提醒这些问题显性化。

6. **打通 Apple Home / Siri**
   通过 HomeKit Bridge 把适合日常控制的设备暴露给 Apple Home 和 Siri，但不暴露管理开关、重复实体、危险电源回路和调试开关。

7. **建立自动化和控制边界**
   区分“地产 485 主回路”和“下游智能灯”的控制权，避免 Home Assistant、米家、墙面开关、Siri 互相打架。

8. **做恢复和验证**
   对断电恢复、设备重连、HA 启动、服务调用后状态确认等场景做防护。关键动作不只相信 API 返回成功，而是读回状态再判断。

## 总体架构思路

推荐把系统分成四层：

```text
承载层
  Mac mini / Docker / 持久化目录 / 备份

设备接入层
  HYQW adapter / 米家 / 美的 / MQTT / 其他集成

状态归一层
  Home Assistant 实体、Area、命名、历史记录

运维自动化层
  场景、恢复检查、状态验证、通知、fallback

用户入口层
  HA Dashboard / Apple Home / Siri / 物理开关 / 原厂 App
```

关键不是“所有设备都能在 HA 里看到”，而是每一层的职责要清楚：

- 哪个系统负责协议接入；
- 哪个系统负责日常控制；
- 哪个系统只做状态观察；
- 哪些设备可以给语音助手；
- 哪些设备必须留在后台，不给误触入口。

## 推荐落地顺序

### 1. 先确定承载方式

参考部署使用 Mac mini 作为常在线主机，并用 Docker 运行 Home Assistant 和周边服务。这样做的好处是服务边界清楚，配置和数据目录更容易备份，后续迁移到其他主机也更可控。

落地时建议先想清楚：

- Home Assistant 的配置目录放在哪里；
- 哪些服务必须随 HA 长期运行；
- 哪些服务只是监控、通知或辅助工具；
- 容器重启策略如何设置；
- 如何备份配置、数据库和关键持久化目录；
- 断电重启后，哪些服务需要自动恢复。

不建议一开始就把所有东西都放进来。先让 HA 稳定运行，再逐步加 MQTT、监控、通知、辅助脚本等周边服务。

### 2. 先接入，不急着自动化

先把地产 485 设备、米家设备、美的家电接入 Home Assistant，确认实体存在、状态能更新、控制不会误触发。

这个阶段不要急着写复杂自动化。先观察几天，记录哪些实体稳定、哪些状态经常延迟、哪些设备会 `unavailable`。

如果采用上游那种 OpenWrt / DNS / MQTT bridge 拓扑，建议先验证三件事：

- 485 网关确实连到了本地 MQTT；
- 本地 MQTT bridge 能继续透传到开发商服务；
- 原厂 App 和中控屏没有因为接管而失效。

### 3. 先做命名和分组

把实体按房间、用途和控制风险分类：

- 日常控制：灯、窗帘、空气净化器；
- 状态观察：温湿度、空气质量、家电运行状态；
- 基础设施：主回路、网关、MQTT、路由器相关开关；
- 高风险设备：门锁、摄像头、安防、总电源。

后续是否暴露给 Siri、是否进入 dashboard、是否参与自动化，都从这个分类出发。

### 4. 处理控制边界

精装系统里经常会出现这种情况：

```text
地产 485 主回路
  -> 给某一路灯具供电
  -> 下游其实是米家智能灯或其他智能灯
```

这种情况下，不要把主回路和灯具当成同一个东西。

推荐做法：

- 主回路负责供电；
- 智能灯负责亮度、色温、开关体验；
- HA 场景先确保主回路有电，再控制下游灯；
- 自动化不要强行覆盖用户通过墙面开关或米家 App 做的选择。

相关模板：

- [`templates/home-assistant/kitchen-main-switch.yaml`](../templates/home-assistant/kitchen-main-switch.yaml)
- [`templates/home-assistant/lighting-scene-boundary.yaml`](../templates/home-assistant/lighting-scene-boundary.yaml)

### 5. 米家迁移要小步走

如果同一个设备同时出现在 Xiaomi Miot 和 Xiaomi Home，不要立刻全量替换。

推荐顺序：

1. 先导出实体清单；
2. 选一个低风险设备族，例如空气质量传感器；
3. 新旧实体并行观察；
4. 先改 dashboard，再改通知；
5. 最后才改控制自动化；
6. 旧实体保留一段时间作为 fallback。

相关文档和模板：

- [`docs/xiaomi-home-migration.md`](xiaomi-home-migration.md)
- [`templates/home-assistant/xiaomi-shadow-compare.yaml`](../templates/home-assistant/xiaomi-shadow-compare.yaml)

### 6. 美的等家电先做可观测性

家电集成最容易踩的坑是：实体还在，但状态不一定可靠；服务调用成功，也不代表设备真的执行成功。

推荐先做：

- `unavailable` 持续时间提醒；
- 运行完成后的二次确认；
- 连接不稳定时的降级说明；
- dashboard 上明确显示“集成不可用”和“设备状态”是两件事。

相关文档和模板：

- [`docs/midea-appliance-reliability.md`](midea-appliance-reliability.md)
- [`templates/home-assistant/midea-availability-watch.yaml`](../templates/home-assistant/midea-availability-watch.yaml)

### 7. Siri 只暴露日常设备

Apple Home / Siri 很方便，但不适合暴露所有 HA 实体。

适合暴露：

- 常用灯；
- 窗帘；
- 空气净化器；
- 少量场景；
- 只读空气质量或温湿度传感器。

不建议暴露：

- 网关管理开关；
- 主回路或总电源；
- 重复实体；
- 调试脚本；
- 路由器、MQTT、Wi-Fi 等基础设施控制；
- 未审查安全边界的门锁、摄像头和安防实体。

相关文档：

- [`docs/apple-home-siri-exposure.md`](apple-home-siri-exposure.md)

## 可以开源什么

适合公开：

- 架构图和分层思路；
- 去敏后的自动化模板；
- 实体命名规范；
- 迁移检查表；
- 稳定性监控思路；
- bug 复现描述和通用修复建议；
- 不包含真实设备信息的辅助脚本。

不适合公开：

- 真实 HAR 文件；
- 真实网关 SN；
- MQTT topic、账号、密码；
- replay payload；
- Home Assistant `.storage`；
- HomeKit 配对码；
- 精确户型、房间布局和家庭作息。

## 给其他业主的落地检查表

开始之前先确认：

- 你能恢复 Home Assistant 配置；
- 你知道哪些设备属于固定基础设施；
- 你知道哪些实体可能会影响安全或断电；
- 你不会把真实抓包和密钥提交到 GitHub；
- 你愿意先观察，再自动化。

第一批建议只做：

- 在 Mac mini / Docker 上稳定运行 HA；
- 接入 adapter；
- 接入米家和家电；
- 整理实体命名；
- 做一个只读 dashboard；
- 做 1-2 个低风险提醒；
- 暴露少量灯光或窗帘给 Apple Home。

等系统稳定后，再逐步加入场景、恢复检查、语音控制和跨生态联动。

## 核心经验

真实家庭自动化不是把所有东西都接进一个 App 就结束了。更重要的是：

- 保留家人已经习惯的控制方式；
- 不让自动化覆盖人的选择；
- 不把基础设施控制暴露到误触入口；
- 对不稳定集成保持可见性；
- 对关键动作做读回验证；
- 把私有信息和可复用经验分开。

这也是本仓库的定位：不发布完整家庭配置，而是发布可以被其他业主安全复用的思路、边界和模板。
