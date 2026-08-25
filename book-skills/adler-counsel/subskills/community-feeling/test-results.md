# community-feeling — 压力测试报告 (test-results)

- 测试框架: 跨 skill 盲测路由（中文 bigram 重叠 + 触发短语加权）
- 用例总数: 6 = 3 should_trigger / 2 should_not_trigger / 1 edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: should-not-trigger-01
- 结论: **PASS**

## 用例明细

| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 我没有归属，融不进去任何圈子，好孤独。 | community-feeling | PASS |
| should-trigger-02 | should_trigger | 别人都是竞争者，世界对我充满了敌意，没人帮我。 | community-feeling | PASS |
| should-trigger-03 | should_trigger | 我是世界中心，大家都该围着我转，凭什么都不顺着我。 | community-feeling | PASS |
| should-not-trigger-01 | should_not_trigger | 我想有意义地活，但找不到人生目标，不知道活着为了什么。 | contribution-happiness | PASS |
| should-not-trigger-02 | should_not_trigger | 帮我推荐几部讲心理学的电影。 | courage-to-be-ordinary | PASS |
| edge-01 | edge_case | 我在公司被排挤霸凌，每天上班都怕，是不是我共同体感觉不够、没融入好？ | community-feeling | PASS |

## 备注
- should_not_trigger 为 0 容忍：任一误激活即 FAIL；其中至少 1 条为兄弟 skill 混淆诱饵。
- edge_case 验证 skill 文档 B 段（边界/护栏）是否被路由层识别，需人工结合预期行为复核。
- 跨 skill 混淆测试：每条 prompt 与全部 12 个 skill 的 trigger 签名打分，确认目标 skill 为最优归属。