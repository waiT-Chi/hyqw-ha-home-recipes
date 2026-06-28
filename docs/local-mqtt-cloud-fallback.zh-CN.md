# 本地 MQTT 优先 + 云端保底实践

这篇记录一个比“把开发商 MQTT 域名永久指向本地”更稳妥的落地方式：

```text
正常状态：
  485 网关 -> 本地 MQTT broker -> Home Assistant / adapter
                         -> MQTT bridge -> 开发商云端

保底状态：
  485 网关 -> 开发商云端
```

核心目标是：**本地控制可以失败，但不能把原厂云端退路一起拖死。**

如果本地 broker、Home Assistant 主机、ShellCrash/Clash 内核或局域网链路异常，只要 WAN 仍然可用，系统应能自动撤掉本地覆盖，让 485 网关回到开发商云端。

## 为什么不只做永久 hosts 覆写

上游常见方案会让路由器或 OpenWrt 接管 DHCP/DNS，把开发商 MQTT 域名解析到本地 MQTT broker。这能实现本地控制，但也会带来一个风险：

- 如果本地 MQTT broker 挂了，485 网关仍然会被解析到本地；
- 如果路由器上的 DNS/透明代理挂死，网关可能既连不上本地，也回不到云端；
- 如果没有明确回退动作，原厂 App 和中控屏也可能一起失效。

因此，参考部署没有把“本地域名覆写”当成唯一方案，而是做成一个可撤销的本地覆盖层。

## 推荐状态机

建议把路由侧逻辑做成三个模式：

```text
cloud
  强制云端保底。适合安装后默认状态、排障、家里没人时保守运行。

local
  强制本地优先。只在本地 broker、路由器代理和主机都健康时启用；
  如果健康检查失败，应立即退回 cloud_safe。

auto
  自动模式。连续多次确认本地健康后切到 local_overlay；
  连续多次异常后切回 cloud_safe。
```

运行时可以再细分成两个实际状态：

```text
local_overlay
  本地覆盖已生效，485 网关的 MQTT 连接被导向本地 broker。

cloud_safe
  本地覆盖已撤销，485 网关回到开发商云端。
```

## 路由侧实现思路

参考部署使用 ShellCrash/Clash 类透明代理环境，不要求一定刷完整 OpenWrt。关键是路由器能做三件事：

1. 识别 485 网关的固定 IP；
2. 添加和删除 `iptables` NAT 规则；
3. 定时运行一个很小的健康检查脚本。

### 本地覆盖

本地覆盖只针对 485 网关和 MQTT 端口，不影响全屋其他设备：

```text
匹配：
  source = <485_GATEWAY_IP>
  destination = ShellCrash fake-ip 段或已缓存的开发商 MQTT IP
  tcp dport = 1883

动作：
  DNAT 到 <LOCAL_MQTT_BROKER_IP>:1883
  SNAT 回程到路由器 LAN IP
```

SNAT 很重要。没有它时，本地 broker 可能直接回包给 485 网关，导致连接路径不对称，连接看起来建立了但实际不稳定。

### 云端保底

云端保底要做两件事：

1. 删除本地 DNAT/SNAT 覆盖；
2. 让 485 网关绕过本地 DNS/fake-ip 链路，重新连开发商 MQTT。

在 ShellCrash/Clash fake-ip 环境里，可以使用组合保底：

```text
对 <485_GATEWAY_IP> 的 DNS 请求：
  临时绕过 ShellCrash DNS 透明劫持

对 <VENDOR_MQTT_HOST>：
  dnsmasq 返回当前开发商 MQTT 真实 IP

对仍然访问 fake-ip 的旧连接：
  临时 DNAT 回开发商 MQTT 真实 IP

最后：
  清理 485 网关旧的 MQTT conntrack
```

这样即使网关刚刚拿到过 fake-ip，或者连接缓存还没刷新，也能尽快回到云端路径。

## 健康检查

自动模式不应因为一次网络抖动就来回切换。建议使用连续计数：

```text
local_ok 连续 3 次：
  切到 local_overlay

local_failed 连续 3 次：
  切到 cloud_safe
```

健康检查至少包括：

- Home Assistant / MQTT broker 主机能 ping 通；
- 本地 MQTT `1883` 端口可连接；
- ShellCrash/Clash 核心和 DNS/透明代理端口健康；
- 开发商 MQTT 云端仍可连接，作为回退路径。

## 验证方法

### 1. 先默认云端

安装后先保持 `cloud`，确认原厂 App 和中控屏仍可控制。

路由器上应看到 485 网关直接连开发商 MQTT：

```text
<485_GATEWAY_IP> -> <VENDOR_MQTT_IP>:1883
```

这一步是保底线：如果后面本地方案异常，至少知道云端路径可恢复。

### 2. 再验证本地

切到 `local` 后，连接表应表现为：

```text
<485_GATEWAY_IP> -> ShellCrash fake-ip:1883
回程来自 <LOCAL_MQTT_BROKER_IP>:1883
```

同时，本地 MQTT broker 日志应看到 485 网关连入。

### 3. 最后切自动

进入 `auto` 后，脚本先预热健康检查，再自动切到本地覆盖。后续如果本地 broker 或主机异常，连续失败后会回到 `cloud_safe`。

## 手动控制接口

参考部署给守护脚本保留了四个手动入口：

```sh
/bin/sh /data/<GUARD_SCRIPT>.sh status
/bin/sh /data/<GUARD_SCRIPT>.sh cloud
/bin/sh /data/<GUARD_SCRIPT>.sh local
/bin/sh /data/<GUARD_SCRIPT>.sh auto
```

其中 `cloud` 是最重要的紧急入口。无论本地规则当前是什么状态，它都应撤销本地覆盖，并让 485 网关回到开发商云端。

## 不建议公开的内容

这类脚本会直接影响固定家居基础设施，不建议公开完整可复制版本。公开文档时应去掉：

- 真实家庭 IP 拓扑；
- 真实 MQTT topic；
- 设备序列号；
- 开发商账号、token、HAR；
- 抓包 payload；
- 可被直接复用来控制别人设备的完整脚本。

适合公开的是状态机、健康检查思路、回退策略和验证方法。

## 核心经验

本地控制不是目的本身，**可恢复的控制权**才是目的。

对真实家庭来说，最好的状态不是“所有流量永远走本地”，而是：

- 本地健康时，HA 走局域网控制，响应快、WAN 断开也能用；
- 本地不健康时，自动撤销本地覆盖，保留原厂云端；
- 家人日常使用的 App、中控屏和物理控制方式不被破坏；
- 排障时可以一条命令回云端。
