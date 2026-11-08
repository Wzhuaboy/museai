# Ancient CCTV Idiom Stories - 专属 Skill v0.1

> 目的：用中国古代监控视角讲成语，加深印象。每个视频一个成语。
> 工具：Gemini Pro（Gemini App，Veo 3.1）出画面，剪映手机版拼接。
> 状态：2026-11-08 立项，第一条：掩耳盗铃。以后改这里就行，不用每次重讲。

## 怎么改这个 Skill（给以后用的说明）

- 改通用规则：改下面“5 条死规矩”和“通用模板”。
- 改某一集：改 `prompts/` 里那一集的文件，不要动通用模板。
- 加新成语：复制 `prompts/yan-er-dao-ling.md` 的结构，新建一个文件，按“新成语模板”填。
- 版本记录：每次大改在文末“版本记录”加一行日期 + 改了什么。

## 5 条死规矩（比现有案例好的地方）

1. 监控逻辑即寓意：机位不是装饰，要参与讲故事。掩耳盗铃里，摄像头就是揭穿他的证人。
2. 不编精确日期：只写朝代 + 地点 + 机位号，例如“战国 · 深夜 · 钟楼 CAM2”，不写某年某月某日。
3. 一镜一个 CAM，机位全程不动：绝不推、拉、摇、跟拍。转场只用硬切，不用淡入淡出。
4. 每集结构固定：5 秒看懂故事，10 秒看到反转，3 秒背下成语。总长 25-30 秒。
5. 开拍前先核服化道：朝代、衣服、道具对不上就不生成。战国穿战国衣服，不出现现代物。

## 工具与规格（已核实，2026-11-08）

- Gemini App + Google AI Pro：单条最长 8 秒，Veo 3.1，支持 9:16 / 16:9，720p / 1080p / 4K，24fps。
- Pro 和 Ultra 差在数量，不差在时长，单条都是 8 秒。
- 一集 = 3 条 x 8 秒 = 24 秒故事 + 3 秒教学卡 = 27 秒成品。
- 拼接：剪映手机版，免费。按 1、2、3 顺序导入，硬切，统一加时间戳文字，最后加教学卡，导出 1080p / 30fps。
- Flow 不可用（2026-11-08 实测）：Flow 在中国不在支持名单，Pro 订阅也不行，截图提示“Flow 尚未在您所在的国家/地区推出”，放弃 Flow 路线，不要再试换节点。
- 时间戳不要让 Gemini 烧进画面里（容易出乱码字），在剪映里统一加文字。
- 提示词里不要留时间戳、字幕、水印，让 Veo 只出干净画面。

## 通用工作流

1. 选成语：单人、单场景、一个核心动作、有反转。避开已刷屏的司马光、荆轲、武松。
2. 写 3 条提示词：每条 1 个主动作，人物、场景、机位描述三条一字不动，只换动作。
3. Gemini 生成：先出第 1 条，满意后用第 1 条的末帧截图当参考图，再出第 2、3 条，防人物走形。
4. 剪映拼接：导入 1、2、3，硬切，加 CAM1 / CAM2 字样，加统一时间戳，加教学卡，导出。
5. 复盘进 Skill：哪条翻车了、哪句提示词改了才好，把结论写回对应文件。

## 通用模板（新成语直接套）

### 固定不变的部分（三条复制粘贴，一字不动）

```
Static fixed high-angle surveillance camera mounted in the top corner, no camera movement, no pan, no tilt, no zoom, no tracking.
Vertical 9:16, low-resolution CCTV footage, black-and-white with low saturation cold green tint, film grain, noise, scan lines, slight fisheye distortion.
Ancient China, [朝代], [地点], night, dim oil-lamp light, stone floor, wooden pillars.
One man only: [人物外貌 + 衣服，一句话写死，例如：thin middle-aged man in dark coarse cloth robe and black headscarf].
No text, no subtitles, no timestamp burned in, no watermark, no modern objects, no cinematic camera moves.
```

### 每条只换的部分

- 第 1 条：进场 + 观察，8 秒。
- 第 2 条：核心动作 + 出事，8 秒。
- 第 3 条：反转 + 定格，8 秒。

### 教学卡（剪映里加，不进提示词）

```
[成语] [拼音]
意思：[一句话]
记住一句话：[一句口语]
```

## 系列排期（已定）

1. 掩耳盗铃（第一条，已出提示词，见 prompts/yan-er-dao-ling.md）
2. 画蛇添足
3. 守株待兔
4. 刻舟求剑
5. 亡羊补牢

## 版本记录

- v0.1 2026-11-08：立项。定 5 条规矩、Gemini 3x8 秒 + 剪映拼接、第一条掩耳盗铃。
- v0.1 2026-11-08：推到 GitHub Wzhuaboy/museai/skills/ancient-cctv-idiom/ 当总库，各大 AI 共用同一套。
