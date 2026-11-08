# Skills 总库

这里是我的专属 skill 总库，各大 AI 共用同一套，改一次、推一次，所有 AI 都用新版。

## 怎么用

- Muse / Claude：直接读这里的文件。
- Gemini / ChatGPT / 其他 AI：把下面链接发给它，加一句“按这个 skill 出提示词”，它就能读。
- 生成视频时只粘提示词文件里的英文提示词，不用把整个 skill 粘过去。

## 现有 skill

- `ancient-cctv-idiom/` — 中国古代监控视角成语故事：每个视频一个成语，Gemini Pro 3x8 秒 + 剪映硬切拼接，成品 25-30 秒。
  - 主文件：`ancient-cctv-idiom/SKILL.md`
  - 第一集提示词：`ancient-cctv-idiom/prompts/yan-er-dao-ling.md`

## 改动规则

- 改通用规则只改 `SKILL.md`，改某一集只改 `prompts/` 里那一集。
- 每次大改在 `SKILL.md` 文末版本记录加一行。
- 本地改完推到 GitHub 后，各 AI 用的才是新版，不要只改本地不推。
