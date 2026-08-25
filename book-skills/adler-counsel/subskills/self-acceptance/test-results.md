# self-acceptance — 压力测试报告 (test-results)

- 测试框架: 跨 skill 盲测路由（中文 bigram 重叠 + 触发短语加权）
- 用例总数: 6 = 3 should_trigger / 2 should_not_trigger / 1 edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: should-not-trigger-01
- 结论: **PASS**

## 用例明细

| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 我太差了，什么都做不好，我接受不了这样的自己。 | self-acceptance | PASS |
| should-trigger-02 | should_trigger | 我天天给自己打气说'我能行'，但其实心里虚得很，越打气越累。 | self-acceptance | PASS |
| should-trigger-03 | should_trigger | 我卡在'接受现状'和'努力改变'之间，既不放过自己也不行动，好丧。 | self-acceptance | PASS |
| should-not-trigger-01 | should_not_trigger | 我不想平庸，我必须出人头地，平凡有什么意义？ | courage-to-be-ordinary | PASS |
| should-not-trigger-02 | should_not_trigger | 帮我写一段 Python 读取 CSV 并画图的代码。 | community-feeling | PASS |
| edge-01 | edge_case | 我重度抑郁，天天觉得自己一无是处，活着没意思，什么都不想做。 | contribution-happiness | PASS |

## 备注
- should_not_trigger 为 0 容忍：任一误激活即 FAIL；其中至少 1 条为兄弟 skill 混淆诱饵。
- edge_case 验证 skill 文档 B 段（边界/护栏）是否被路由层识别，需人工结合预期行为复核。
- 跨 skill 混淆测试：每条 prompt 与全部 12 个 skill 的 trigger 签名打分，确认目标 skill 为最优归属。