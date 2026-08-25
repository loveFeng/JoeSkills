# courage-to-be-disliked — 压力测试报告 (test-results)

- 测试框架: 跨 skill 盲测路由（中文 bigram 重叠 + 触发短语加权）
- 用例总数: 6 = 3 should_trigger / 2 should_not_trigger / 1 edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: should-not-trigger-01
- 结论: **PASS**

## 用例明细

| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 我怕同事生气，所以从来不敢提不同意见。 | courage-to-be-disliked | PASS |
| should-trigger-02 | should_trigger | 为了不惹人厌我什么都忍了，好累。 | courage-to-be-disliked | PASS |
| should-trigger-03 | should_trigger | 大家都觉得我该考公务员，我不敢说不，怕被说闲话。 | courage-to-be-disliked | PASS |
| should-not-trigger-01 | should_not_trigger | 孩子不学习，我要不要管，怎么让他写？ | separation-of-tasks | PASS |
| should-not-trigger-02 | should_not_trigger | 邻居装修噪音扰民，沟通无果，能报警或投诉到哪个部门？ | courage-to-be-ordinary | PASS |
| edge-01 | edge_case | 上司暗示不跟他睡就给我穿小鞋、压我绩效。 | horizontal-relations | PASS |

## 备注
- should_not_trigger 为 0 容忍：任一误激活即 FAIL；其中至少 1 条为兄弟 skill 混淆诱饵。
- edge_case 验证 skill 文档 B 段（边界/护栏）是否被路由层识别，需人工结合预期行为复核。
- 跨 skill 混淆测试：每条 prompt 与全部 12 个 skill 的 trigger 签名打分，确认目标 skill 为最优归属。