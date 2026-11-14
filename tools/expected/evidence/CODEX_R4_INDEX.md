# Codex 第四轮验收 · 证据索引（F17 / F18）

整理：2026-11-14 · 状态：本地文件，未提交，随 F19 第一阶段一并提交（须批准）

## 1. 冻结基线

| 项 | 值 |
|---|---|
| 冻结技术基线 | `8cc7f9469009fff1806997efcdaf97d2cb25f630`（短 `8cc7f94`） |
| 父提交 | `b75f88a0039df58f85ce47449eeae07768daab78` |
| 提交时间 | 2026-11-14 12:42:41 +0100 |
| 远端核对 | 2026-11-14 `git ls-remote origin refs/heads/main` = `8cc7f94…25f630` |
| 本地标签 | `f17-f18-accepted-8cc7f94`（附注标签，仅本地，推送须批准） |
| 运行代码改动 | `curs/player.js`（5 行）、`curs/relacio.js`（3 行） |

## 2. 四轮验收链

| 轮次 | 被验版本 | Codex 结论 | 处理提交 |
|---|---|---|---|
| 第 1 轮 | `e981b8a` | 提出 F17、F18 | `6a1dfdd` |
| 第 2 轮 | `6a1dfdd` | F17 FAIL（l10 滑块空闲定时器） | `b75f88a` |
| 第 3 轮 | `b75f88a` | F17 FAIL（仅 S1：过期序列报告“完成”） | `8cc7f94` |
| 第 4 轮 | `8cc7f94` | F17 PASS、F18 PASS，冻结 `8cc7f94` | — |

## 3. Codex 第四轮报告原文

**缺失。** 本会话未收到报告原文。上表第 4 轮结论只来自用户 2026-11-14 13:03 的消息，
不是从报告原文核对得出。待补：报告全文、Codex 执行的命令与输出、执行时间。
建议放在 `tools/expected/evidence/codex_r4_report.md`，补入后在本表登记 SHA-256。

## 4. 仓库内证据（随 `8cc7f94` 提交，SHA-256）

### 第 3 轮修复（P1，已合并）与对照

| 文件 | 用途 | SHA-256（前 16 位） |
|---|---|---|
| `f17c_s1review_base_b75f88a.txt` | S1 复查，修复前 | `26ca0f34c256d23d` |
| `f17c_s1review_P1_fixed.txt` | S1 复查，修复后 | `eb5cf48b612e4194` |
| `f17c_s1review_P2_codex_caller_checks.txt` | Codex 方案对照（未合并） | `694516a2cc30e80e` |
| `f17c_s1_order_evidence.txt` | 事件顺序证据 | `368ca8c9bda646a0` |
| `f17c_s1_probe_three_leave_modes_base.jsonl` | 三种离开方式探针 | `d7dc36fefd967eb4` |
| `f17c_race_final_on_base_b75f88a.txt` | 竞态全集，修复前 | `4f35886ed4a408e2` |
| `f17c_race_final_on_P1_fixed.txt` | 竞态全集，修复后 | `ea6532adf7e3a18d` |
| `f17c_race_intermediate_on_base_S8flake.txt` | 中间结果（测试缺陷，已修测试） | `51537ca989cbb581` |
| `f17c_race_intermediate_on_P1_S8flake.txt` | 同上 | `07ad502400790a02` |
| `f17c_race_intermediate_on_P1_S9timing.txt` | 同上（S9 上限） | `ba6df5464445f61a` |
| `f17c_curs_l01/l02/l07/l10/l11/l12_P1.txt` | 课程回归 | 见 `sha256sum` |
| `f17c_b_scenarios_P1.txt`、`f17c_probe_P1.txt`、`f17c_geo_probe_P1.txt`、`f17c_selftest_P1.txt` | 其他回归 | 见 `sha256sum` |
| `f17c_P1_plus_leg_hardening_NOT_MERGED.diff` | 未合并方案 | `778a7289d68311f3` |
| `f17c_P2_codex_caller_checks_NOT_MERGED.diff` | 未合并方案 | `501c3bb42ac6eccf` |
| `tools/f17_review/F17_S1_review_report_zh.md` | S1 复查报告 | `0cf5ea9659793c34` |

### 第 2 轮（`b75f88a`）

`curs_l10_f17b.txt`、`f17b_race_before_6a1dfdd_run1/2.txt`、`f17b_race_after_run1/2.txt`、
`f17b_race_after_run3_with_S9.txt`、`probe_f17b.txt`

### 第 1 轮修复（`6a1dfdd`，含 F18）

`f17_race_before_e981b8a_run1/2.txt`、`f17_race_after_run1/2.txt`、`curs_l01/l02/l07/l10/l11_F17F18.txt`、
`b_scenarios_F17F18.txt`、`probe_F17F18.txt`、`geo_probe_F17F18.txt`、`regression_F17F18.txt`

## 5. 复现命令

```
git checkout 8cc7f94
python3 -m http.server 8772 --bind 127.0.0.1
python3 tools/f17_s1_review.py OUTDIR 3   # S1，每例 3 次
python3 tools/f17_race.py OUTDIR          # S1–S9 竞态
python3 tools/curs_test.py lXX OUTDIR     # 课程回归
sha256sum tools/expected/evidence/f17c_*
```

## 6. 范围说明

“已关闭”只表示 F17、F18 的技术与功能整改通过独立验收，**不等于教学产品验收通过**。
真机测试、Emily 试学、加泰罗尼亚语审校仍待人工验收；l13–l19 延期。
