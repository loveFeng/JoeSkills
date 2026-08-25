# life-lies — 压力测试报告 (test-results)

- 测试框架: 跨 skill 盲测路由（中文 bigram 重叠 + 触发短语加权）
- 用例总数: 6 = 3 should_trigger / 2 should_not_trigger / 1 edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: should-not-trigger-01
- 结论: **PASS**

## 用例明细

| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 要不是因为我社恐，我早就谈恋爱了。 | life-lies | PASS |
| should-trigger-02 | should_trigger | 我老板太烂了，所以工作干不好也怪不了我。 | life-lies | PASS |
| should-trigger-03 | should_trigger | 我这是没办法，身体不好所以没法出去工作。 | life-lies | PASS |
| should-not-trigger-01 | should_not_trigger | 孩子的作业到底该谁管，是我还是他自己的事？ | separation-of-tasks | PASS |
| should-not-trigger-02 | should_not_trigger | 帮我把这段英文翻译成中文。 | community-feeling | PASS |
| edge-01 | edge_case | 我腿有残疾，出门很不方便，所以没法去正常上班。 | life-lies | PASS |

## 备注
- should_not_trigger 为 0 容忍：任一误激活即 FAIL；其中至少 1 条为兄弟 skill 混淆诱饵。
- edge_case 验证 skill 文档 B 段（边界/护栏）是否被路由层识别，需人工结合预期行为复核。
- 跨 skill 混淆测试：每条 prompt 与全部 12 个 skill 的 trigger 签名打分，确认目标 skill 为最优归属。