# qinglong

青龙面板运行的脚本，每个任务一个子文件夹，例如：

- `xmly/` — 喜马拉雅金币任务（已入库，含 Windows 验证过的两个修复：session 读写路径一致、accounts.py 的 fcntl 兼容）
- `bilibili/` — B站每日任务（待建）

青龙里新建订阅拉取本仓库后，在任务里引用对应脚本路径即可。需要的 token、cookie 在青龙面板的环境变量里配置，不写进脚本文件。
