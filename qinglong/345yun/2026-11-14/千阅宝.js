// 当前脚本来自于 http://script.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cc 脚本库下载！
// 脚本库官方QQ群1群: 429274456
// 脚本库官方QQ群2群: 1077801222
// 脚本库官方QQ群3群: 433030897
// 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
// 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
// 您在使用脚本库下载的脚本时自行检查判断风险。
// 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。

/**
 * 千阅宝(掘金宝) 全任务自动化 - 青龙面板脚本 v3 (2026-11-14 全链路实测版)
 *
 * ⚠️ 运行时请确保手机上的千阅宝 App 完全退出
 *    (成语棋盘/视频会话都是独占的, App 在线会互相作废)
 *
 * 环境变量:
 *   QYB_TOKEN  必填, user_token(32位hex)。多账号用换行或 & 分隔
 *   QYB_NOTIFY 可选, "true" 时通过青龙通知推送结果
 *
 * 覆盖任务(全部真机/真接口实测):
 *   ✅ 每日抽奖x5 + 签到任务奖励
 *   ✅ 福利赚签到(预约+落账) + 原生每日签到
 *   ✅ 红包墙x10 / 砸金蛋(4h冷却) / 大礼包 / 刮刮卡x3
 *   ✅ 成语闯关(自动解题)
 *   ✅ 视频任务引擎: 观看视频赚金币(200/次x20) / 看视频开宝箱(5902+) /
 *      刷短视频红包(590) / 活跃度礼包 —— 实测服务器不校验广告播放,
 *      task_reward_pre 发会话 → task_reward 直接领取, 全程无广告
 *   ⏳ 走路赚: 步数来自手机传感器, 服务器脚本拿不到数据源
 *
 * ⚠️ 注意: 本脚本仅限自动化你自己的账号。视频奖励类接口依赖服务端
 *    不校验广告回调这一事实, 应用方随时可能加固, 被风控也属正常。
 *
 * cron 建议: 20 8,14,20 * * *
 */

const API_HOST = 'https://api.lehuidong.com';
const COMMON = {
  source_style: '7',
  pkg: 'com.juejinchain.qyb',
  vsn: '5.2.6.09',
  channel: 'yingyongbao',
};
const UA =
  'Mozilla/5.0 (Linux; Android 10; ONEPLUS A5010 Build/QKQ1.191014.012; wv) ' +
  'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36';
const HEADERS = {
  'User-Agent': UA,
  Accept: 'application/json, text/plain, */*',
  'X-Requested-With': 'com.juejinchain.qyb',
  Referer: 'https://jjlmobile.juejinchain.com/front/pro/fulizhuan/home/index.html',
};

// 视频任务引擎的任务清单(实测可领的 tag)
const VIDEO_TAGS = [
  { tag: 'view_ad_movie', name: '观看视频赚金币', max: 22 },
  { tag: 'watch_ad_chest_reward', name: '看视频开宝箱', max: 12 },
  { tag: 'kuaishou_chest_extra', name: '刷短视频红包', max: 12 },
  { tag: 'ad_activity', name: '活跃度礼包', max: 3 },
];

const TOKENS = (process.env.QYB_TOKEN || '')
  .split(/[\n&]/)
  .map((s) => s.trim())
  .filter(Boolean);

if (!TOKENS.length) {
  console.log('未配置 QYB_TOKEN, 退出。取值: 抓包 api.lehuidong.com 请求 URL 中 user_token 参数');
  process.exit(0);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function api(token, path, params = {}, opts = {}) {
  const q = new URLSearchParams({ ...COMMON, user_token: token, ...params });
  const cfg = { headers: HEADERS, method: opts.method || 'GET' };
  if (opts.body) {
    cfg.headers['Content-Type'] = 'application/json;charset=utf-8';
    cfg.body = JSON.stringify({ user_token: token, ...opts.body });
  }
  const res = await fetch(`${API_HOST}${path}?${q.toString()}`, cfg);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const body = await res.json();
  if (body.code !== 0) {
    const err = new Error(body.msg || `code=${body.code}`);
    err.code = body.code;
    throw err;
  }
  return body.data;
}

/** 成语闯关: 自动解题 */
async function idiomGame(token, say) {
  let earned = 0;
  let lastReward = null;
  for (let level = 1; level <= 15; level++) {
    let info;
    try {
      info = await api(token, '/v1/fulizhuan/idiom_info');
    } catch (e) {
      say(`  📖 成语: 状态获取失败 ${e.message}`);
      return earned;
    }
    const cd = info.chess_data || {};
    const questions = (cd.elements || []).filter((e) => e.type === 'question' && !e.char);
    if (!questions.length) {
      say(`  📖 成语闯关完成 ${info.current}/${info.count} 关`);
      if (lastReward) {
        try {
          const r = await api(token, '/v1/task/task_reward', {
            tag: lastReward.reward_tag,
            watch_video_id: lastReward.watch_video_id,
          });
          earned += Number(r.reward_value || 0);
          say(`  📖 闯关总奖励 +${r.reward_value}金币`);
        } catch (e) {
          say(`  📖 闯关总奖励: ${e.message}`);
        }
      }
      return earned;
    }
    const chessId = info.chess_id;
    let solvedAll = true;
    for (const q of questions) {
      let ok = false;
      for (const opt of cd.options || []) {
        let r;
        try {
          r = await api(token, '/v1/fulizhuan/idiom_answer', {}, {
            method: 'POST',
            body: { id: chessId, x: q.x, y: q.y, char: opt },
          });
        } catch (e) {
          continue; // 答案错误 → 换下一个候选字
        }
        if (r.success || r.completed) {
          ok = true;
          if (r.completed && r.reward_tag) lastReward = r;
          earned += Number(r.reward_value || 0);
          break;
        }
      }
      if (!ok) {
        say(`  📖 成语: 格(${q.x},${q.y})无匹配候选字, 跳过`);
        solvedAll = false;
        break;
      }
      await sleep(1200);
    }
    if (!solvedAll) return earned;
    say(`  📖 成语第${level}局完成`);
    await sleep(1500);
  }
  return earned;
}

/** 视频任务引擎: pre 发会话 → reward 领取, 循环到当日上限 */
async function videoTasks(token, say) {
  let earned = 0;
  for (const t of VIDEO_TAGS) {
    let got = 0;
    let total = 0;
    for (let i = 0; i < t.max; i++) {
      let pre;
      try {
        pre = await api(token, '/v1/task/task_reward_pre', { tag: t.tag, stage_tag: '' });
      } catch (e) {
        if (i === 0) say(`  📺 ${t.name}: 今日不可领(${e.message})`);
        else say(`  📺 ${t.name}: 第${got}次后结束(${e.message})`);
        break;
      }
      if (!pre.watch_video_id) {
        say(`  📺 ${t.name}: 会话未下发, 跳过`);
        break;
      }
      try {
        const r = await api(token, '/v1/task/task_reward', {
          tag: t.tag,
          watch_video_id: pre.watch_video_id,
          stage_tag: pre.stage_tag || '',
        });
        const v = Number(r.reward_value || 0);
        got++;
        total += v;
        earned += v;
        say(`  📺 ${t.name} 第${got}次: +${v}金币`);
      } catch (e) {
        say(`  📺 ${t.name} 领取失败: ${e.message}`);
        await sleep(5000);
      }
      await sleep(2800);
    }
    if (got > 0) say(`  📺 ${t.name} 小计 +${Math.round(total)}金币 (${got}次)`);
  }
  return earned;
}

/** 单账号完整流程 */
async function runAccount(token, idx) {
  const log = [];
  let earned = [];
  const say = (m) => {
    console.log(`  ${m}`);
    log.push(m);
  };
  const gain = (label, v) => {
    const n = Number(v);
    if (!isNaN(n) && n > 0) earned.push([label, n]);
  };

  // 1. 金币总览
  try {
    const list = await api(token, '/v1/task/task_list');
    const wallet = list.find((x) => x.tag === 'wallet');
    if (wallet) say(`💰 金币: 总${wallet.vcoin_total} | 昨日${wallet.coin_yesterday} | 今日${wallet.coin_today}`);
  } catch (e) {
    say(`⚠️ 任务列表失败: ${e.message}`);
  }

  // 2. 每日抽奖 x5 + 签到任务奖
  try {
    const info = await api(token, '/v1/fulizhuan/task_info');
    const lot = (info.signin_task?.list || []).find((t) => t.tag === 'choujiang');
    const total = Number(lot?.progress?.total ?? 5);
    const done = Number(lot?.progress?.current ?? 0);
    for (let i = done; i < total; i++) {
      try {
        const d = await api(token, '/v1/fulizhuan/choujiang_lottery', { from: 'welfare_task' });
        gain('抽奖', d.reward_value);
        say(`🎰 抽奖${i + 1}/${total}: +${d.reward_value}`);
      } catch (e) {
        say(`🎰 抽奖中止: ${e.message}`);
        break;
      }
      await sleep(2000);
    }
    if (done >= total) say(`🎰 抽奖已完成 ${done}/${total}`);
    try {
      const r = await api(token, '/v1/task/task_reward', {
        tag: 'fulizhuan_home_signin_task_choujiang',
        stage_tag: '',
      });
      gain('签到任务奖', r.reward_value);
      say(`📋 签到任务奖 +${r.reward_value}`);
    } catch (e) {
      say(`📋 签到任务奖: ${e.message}(已领过属正常)`);
    }
  } catch (e) {
    say(`⚠️ 抽奖环节异常: ${e.message}`);
  }

  // 3. 福利赚签到
  try {
    const info = await api(token, '/v1/fulizhuan/task_info');
    const si = info.signin_info || {};
    if (si.signed) {
      say(`✅ 福利赚签到: 今日已签(连续${si.signed_day}天)`);
    } else {
      const next = (si.list || []).find((d) => !d.signed);
      if (!next) throw new Error('无可签档位');
      const stage = next.reward_stage;
      const r1 = await api(token, '/v1/fulizhuan/reserve_sign_in', { reward_stage: stage });
      gain('福利签到', r1.reward_value);
      try {
        await api(token, '/v1/task/task_reward', {
          tag: 'fulizhuan_home_signin',
          stage_tag: stage,
        });
      } catch (_) {}
      say(`✅ 福利赚签到成功(${next.day}) +${r1.reward_value}`);
    }
  } catch (e) {
    say(`❌ 福利赚签到: ${e.message}`);
  }

  // 4. 红包墙 x10
  let redCount = 0;
  for (let stage = 0; stage <= 9; stage++) {
    try {
      const r = await api(token, '/v1/fulizhuan/reserve_red_packet', { reward_stage: stage });
      gain(`红包${stage + 1}`, r.reward_value);
      redCount++;
      say(`🧧 红包${stage + 1}: +${r.reward_value}`);
      await sleep(1000);
    } catch (_) {}
  }
  if (!redCount) say('🧧 红包墙: 暂无可领');

  // 5. 砸金蛋
  try {
    const t = await api(token, '/v1/task/get_treasure_box_time');
    if (Number(t) === 0) {
      const r = await api(token, '/v1/task/treasure_box_save');
      gain('砸金蛋', r.coin);
      say(`🥚 砸金蛋 +${r.coin}金币`);
    } else {
      say(`🥚 砸金蛋冷却中(还需${Math.round(Number(t) / 60)}分钟)`);
    }
  } catch (e) {
    say(`🥚 砸金蛋: ${e.message}`);
  }

  // 6. 原生签到
  try {
    const r = await api(token, '/v1/task/sign_in');
    gain('每日签到', r.coin);
    say(`📅 每日签到: +${r.coin}金币 (累计${r.value})`);
  } catch (e) {
    say(`📅 每日签到: ${e.message}(已签属正常)`);
  }

  // 7. 大礼包
  try {
    const r = await api(token, '/v1/task/gift_bag');
    gain('大礼包', r.reward_value ?? r.value);
    say(`🎁 大礼包 +${r.reward_value ?? r.value ?? '?'}`);
  } catch (e) {
    say(`🎁 大礼包: ${e.message}(已领属正常)`);
  }

  // 8. 刮刮卡
  try {
    const info = await api(token, '/v1/fulizhuan/drawCardInfo');
    const cards = Number(info.normal_card_count || 0) + Number(info.gold_card_count || 0);
    if (cards > 0) {
      for (let i = 0; i < cards; i++) {
        try {
          const r = await api(token, '/v1/fulizhuan/drawCard');
          if (Number(r.reward_value) > 0) {
            gain('刮刮卡', r.reward_value);
            say(`🎫 刮卡${i + 1}: 中奖 +${r.reward_value} (${r.title})`);
          } else {
            say(`🎫 刮卡${i + 1}: 未中奖`);
          }
        } catch (e) {
          say(`🎫 刮卡中止: ${e.message}`);
          break;
        }
        await sleep(1500);
      }
    } else {
      say('🎫 刮刮卡: 今日卡已用完');
    }
  } catch (e) {
    say(`🎫 刮刮卡: ${e.message}`);
  }

  // 9. 成语闯关
  try {
    const got = await idiomGame(token, say);
    if (got > 0) {
      earned.push(['成语闯关', got]);
      say(`📖 成语闯关小计 +${got}金币`);
    }
  } catch (e) {
    say(`📖 成语闯关异常: ${e.message}`);
  }

  // 10. 视频任务引擎
  try {
    const got = await videoTasks(token, say);
    if (got > 0) {
      earned.push(['视频任务', got]);
      say(`📺 视频任务小计 +${Math.round(got)}金币`);
    }
  } catch (e) {
    say(`📺 视频任务异常: ${e.message}`);
  }

  // 11. 汇总
  if (earned.length) {
    const total = earned.reduce((s, x) => s + x[1], 0);
    say(`📦 本次合计 +${Math.round(total)}金币 (${earned.length}项)`);
  } else {
    say('📦 本次无新入账(任务都已完成)');
  }
  return log.join('\n');
}

(async () => {
  const all = [];
  for (let i = 0; i < TOKENS.length; i++) {
    console.log(`\n===== 账号${i + 1} =====`);
    try {
      all.push(`账号${i + 1}:\n${await runAccount(TOKENS[i], i)}`);
    } catch (e) {
      const msg = `账号${i + 1} 异常: ${e.message}`;
      console.log(msg);
      all.push(msg);
    }
    if (i < TOKENS.length - 1) await sleep(3000);
  }
  const summary = all.join('\n\n');
  if (String(process.env.QYB_NOTIFY).toLowerCase() === 'true') {
    try {
      const { sendNotify } = require('./sendNotify');
      await sendNotify('千阅宝全任务', summary);
    } catch (e) {
      console.log('通知失败(不影响执行):', e.message);
    }
  }
})();


// 当前脚本来自于 http://script.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cc 脚本库下载！
// 脚本库官方QQ群1群: 429274456
// 脚本库官方QQ群2群: 1077801222
// 脚本库官方QQ群3群: 433030897
// 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
// 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
// 您在使用脚本库下载的脚本时自行检查判断风险。
// 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。