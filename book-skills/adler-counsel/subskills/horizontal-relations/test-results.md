# horizontal-relations — 压力测试报告 (test-results)

- 测试框架: 跨 skill 盲测路由（中文 bigram 重叠 + 触发短语加权）
- 用例总数: 6 = 3 should_trigger / 2 should_not_trigger / 1 edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: should-not-trigger-01
- 结论: **PASS**

## 用例明细

| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 怎么鼓励孩子写作业，是表扬还是批评好？ | horizontal-relations | PASS |
| should-trigger-02 | should_trigger | 下属总出错，我是不是该骂他一顿立威？ | horizontal-relations | PASS |
| should-trigger-03 | should_trigger | 我妈来带娃我总忍不住指挥她这不对那不对。 | horizontal-relations | PASS |
| should-not-trigger-01 | should_not_trigger | 我的人生我自己说了算，凭什么要按别人给的剧本活。 | separation-of-tasks | PASS |
| should-not-trigger-02 | should_not_trigger | 高速上前车突然急刹，我该怎么避免追尾？ | separation-of-tasks | PASS |
| edge-01 | edge_case | 孩子突然冲到马路中间，我大喊一声'站住'冲过去拉住他。 | community-feeling | PASS |

## 备注
- should_not_trigger 为 0 容忍：任一误激活即 FAIL；其中至少 1 条为兄弟 skill 混淆诱饵。
- edge_case 验证 skill 文档 B 段（边界/护栏）是否被路由层识别，需人工结合预期行为复核。
- 跨 skill 混淆测试：每条 prompt 与全部 12 个 skill 的 trigger 签名打分，确认目标 skill 为最优归属。