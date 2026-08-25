# courage-to-be-ordinary — 压力测试报告 (test-results)

- 测试框架: 跨 skill 盲测路由（中文 bigram 重叠 + 触发短语加权）
- 用例总数: 6 = 3 should_trigger / 2 should_not_trigger / 1 edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: should-not-trigger-01
- 结论: **PASS**

## 用例明细

| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 我不想平庸，我必须出人头地，平凡有什么意义？ | courage-to-be-ordinary | PASS |
| should-trigger-02 | should_trigger | 凭什么是个普通人，我不甘心，我就要做最特别的那个。 | courage-to-be-ordinary | PASS |
| should-trigger-03 | should_trigger | 既然优秀不了，那我就破罐破摔吧，反正也不是什么人物。 | courage-to-be-ordinary | PASS |
| should-not-trigger-01 | should_not_trigger | 我接受不了这样的自己，我怎么这么没用，什么都做不好。 | self-acceptance | PASS |
| should-not-trigger-02 | should_not_trigger | 帮我写个每周工作周报的 Markdown 模板。 | community-feeling | PASS |
| edge-01 | edge_case | 我是职业运动员，教练跟我说要甘于平凡、别老争冠军，我觉得他说得不对。 | courage-to-be-ordinary | PASS |

## 备注
- should_not_trigger 为 0 容忍：任一误激活即 FAIL；其中至少 1 条为兄弟 skill 混淆诱饵。
- edge_case 验证 skill 文档 B 段（边界/护栏）是否被路由层识别，需人工结合预期行为复核。
- 跨 skill 混淆测试：每条 prompt 与全部 12 个 skill 的 trigger 签名打分，确认目标 skill 为最优归属。