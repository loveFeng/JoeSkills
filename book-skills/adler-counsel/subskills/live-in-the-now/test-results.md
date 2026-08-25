# live-in-the-now — 压力测试报告 (test-results)

- 测试框架: 跨 skill 盲测路由（中文 bigram 重叠 + 触发短语加权）
- 用例总数: 6 = 3 should_trigger / 2 should_not_trigger / 1 edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: should-not-trigger-01
- 结论: **PASS**

## 用例明细

| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 等以后我存够钱了，就好好生活、好好陪家人。 | live-in-the-now | PASS |
| should-trigger-02 | should_trigger | 如果当初我选了别的行业就好了，现在这一切都晚了。 | live-in-the-now | PASS |
| should-trigger-03 | should_trigger | 我还没准备好，等时机成熟再开始做这件事吧。 | live-in-the-now | PASS |
| should-not-trigger-01 | should_not_trigger | 我找不到人生意义，怎么才能找到人生的目标？ | contribution-happiness | PASS |
| should-not-trigger-02 | should_not_trigger | 用 JavaScript 怎么给搜索框做输入防抖？ | contribution-happiness | PASS |
| edge-01 | edge_case | 我马上要做一个重大的职业转型，需要规划未来五年的路径，这跟活在当下矛盾吗？ | live-in-the-now | PASS |

## 备注
- should_not_trigger 为 0 容忍：任一误激活即 FAIL；其中至少 1 条为兄弟 skill 混淆诱饵。
- edge_case 验证 skill 文档 B 段（边界/护栏）是否被路由层识别，需人工结合预期行为复核。
- 跨 skill 混淆测试：每条 prompt 与全部 12 个 skill 的 trigger 签名打分，确认目标 skill 为最优归属。