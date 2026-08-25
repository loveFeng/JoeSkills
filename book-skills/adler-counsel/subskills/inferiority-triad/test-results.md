# inferiority-triad — 压力测试报告 (test-results)

- 测试框架: 跨 skill 盲测路由（中文 bigram 重叠 + 触发短语加权）
- 用例总数: 6 = 3 should_trigger / 2 should_not_trigger / 1 edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: should-not-trigger-01
- 结论: **PASS**

## 用例明细

| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 我因为学历低，所以一直没法成功，这就是事实。 | inferiority-triad | PASS |
| should-trigger-02 | should_trigger | 他总炫耀自己有多惨多不容易，好像谁都欠他一份理解。 | inferiority-triad | PASS |
| should-trigger-03 | should_trigger | 我老觉得别人都比我强，一比较就焦虑，是不是我有病。 | inferiority-triad | PASS |
| should-not-trigger-01 | should_not_trigger | 我太差了，我接受不了这样的自己，我怎么这么没用。 | self-acceptance | PASS |
| should-not-trigger-02 | should_not_trigger | 周末附近有什么好玩的景点推荐？ | contribution-happiness | PASS |
| edge-01 | edge_case | 我儿子每天说'我什么都做不好'，我要不要骂醒他、逼他别这么矫情？ | self-acceptance | PASS |

## 备注
- should_not_trigger 为 0 容忍：任一误激活即 FAIL；其中至少 1 条为兄弟 skill 混淆诱饵。
- edge_case 验证 skill 文档 B 段（边界/护栏）是否被路由层识别，需人工结合预期行为复核。
- 跨 skill 混淆测试：每条 prompt 与全部 12 个 skill 的 trigger 签名打分，确认目标 skill 为最优归属。