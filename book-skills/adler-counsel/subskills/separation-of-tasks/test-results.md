# separation-of-tasks — 压力测试报告 (test-results)

- 测试框架: 跨 skill 盲测路由（中文 bigram 重叠 + 触发短语加权）
- 用例总数: 6 = 3 should_trigger / 2 should_not_trigger / 1 edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: should-not-trigger-01
- 结论: **PASS**

## 用例明细

| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 孩子不写作业，我每天吼他也没用，该怎么让他写？ | separation-of-tasks | PASS |
| should-trigger-02 | should_trigger | 父母强烈反对我辞职创业，我好痛苦，要不要听他们的。 | separation-of-tasks | PASS |
| should-trigger-03 | should_trigger | 我该怎么让我老公少打游戏多陪孩子？ | separation-of-tasks | PASS |
| should-not-trigger-01 | should_not_trigger | 我总怀疑对象不专一，天天翻他手机查岗。 | self-acceptance | PASS |
| should-not-trigger-02 | should_not_trigger | 企业规章制度中奖惩与考核条款应该怎么拟定才合法？ | horizontal-relations | PASS |
| edge-01 | edge_case | 我闺蜜男朋友动手打她，她还说想帮他改好。 | separation-of-tasks | PASS |

## 备注
- should_not_trigger 为 0 容忍：任一误激活即 FAIL；其中至少 1 条为兄弟 skill 混淆诱饵。
- edge_case 验证 skill 文档 B 段（边界/护栏）是否被路由层识别，需人工结合预期行为复核。
- 跨 skill 混淆测试：每条 prompt 与全部 12 个 skill 的 trigger 签名打分，确认目标 skill 为最优归属。