# museai

慕斯为亲爱的写的脚本统一仓库。所有脚本只放这里，青龙面板和 QuantumultX 都从这个仓库订阅拉取，改脚本只需要改这里一处。

## 目录

- `qinglong/` — 青龙面板运行的 Python 脚本，按任务分子文件夹
- `quantumultx/` — QuantumultX 用的 JS 脚本和重写配置
- `common/` — 所有任务共用的工具（Bark 通知、随机延时、状态检查等）

## 硬规矩

- token、cookie、密码等密钥永远不写进仓库，只放在青龙的环境变量里
- 每个任务在下表登记：名称、目录、定时周期、需要的环境变量名（只写名字，不写值）

## 任务清单

| 任务 | 目录 | 运行方式 | 需要的环境变量 |
| --- | --- | --- | --- |
| 喜马拉雅金币 | qinglong/xmly/ | 青龙订阅拉取 / Windows 本地跑均可 | XMLY_DEVICE（可选，设备号）；token 用 import-session 写入本地 session.json，不进仓库 |
| （学习中）B站每日任务 | qinglong/bilibili/ | 青龙 | 待抓包后确定 |
