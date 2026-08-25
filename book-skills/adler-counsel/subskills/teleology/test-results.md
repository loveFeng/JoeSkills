# teleology — 压力测试报告 (test-results)

- 测试框架: 跨 skill 盲测路由（中文 bigram 重叠 + 触发短语加权）
- 用例总数: 6 = 3 should_trigger / 2 should_not_trigger / 1 edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: should-not-trigger-01
- 结论: **PASS**

## 用例明细

| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 我控制不住自己发火，都是小时候我爸脾气暴、家庭教育害的。 | teleology | PASS |
| should-trigger-02 | should_trigger | 为什么我总是拖延，可能是天生ADHD吧，改不了的。 | teleology | PASS |
| should-trigger-03 | should_trigger | 我焦虑得睡不着，这又不是我能选的，是环境逼的。 | teleology | PASS |
| should-not-trigger-01 | should_not_trigger | 我怕老板不高兴，所以从来不敢拒绝他。 | courage-to-be-disliked | PASS |
| should-not-trigger-02 | should_not_trigger | 帮我写一段 Python 读取 CSV 并画图的代码。 | community-feeling | PASS |
| edge-01 | edge_case | 我同事刚经历车祸，现在有创伤后应激，一直走不出来。 | teleology | PASS |

## 备注
- should_not_trigger 为 0 容忍：任一误激活即 FAIL；其中至少 1 条为兄弟 skill 混淆诱饵。
- edge_case 验证 skill 文档 B 段（边界/护栏）是否被路由层识别，需人工结合预期行为复核。
- 跨 skill 混淆测试：每条 prompt 与全部 12 个 skill 的 trigger 签名打分，确认目标 skill 为最优归属。