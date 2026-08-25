# trust-others — 压力测试报告 (test-results)

- 测试框架: 跨 skill 盲测路由（中文 bigram 重叠 + 触发短语加权）
- 用例总数: 6 = 3 should_trigger / 2 should_not_trigger / 1 edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: should-not-trigger-01
- 结论: **PASS**

## 用例明细

| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 我不敢信他，上次被坑了，所以现在谁都不敢信。 | trust-others | PASS |
| should-trigger-02 | should_trigger | 他靠谱吗？我到底该怎么建立对他的信任？ | trust-others | PASS |
| should-trigger-03 | should_trigger | 我总是怀疑伴侣是不是在外面有人，天天查他手机。 | trust-others | PASS |
| should-not-trigger-01 | should_not_trigger | 同事把我负责的项目搞砸了，但那是他的事，我不该替他收拾烂摊子。 | courage-to-be-disliked | PASS |
| should-not-trigger-02 | should_not_trigger | 用 Python 怎么读取一个 JSON 文件并解析成字典？ | live-in-the-now | PASS |
| edge-01 | edge_case | 我朋友最近总找我借钱，我怀疑他在骗我钱，但我又怕伤感情不敢问。 | trust-others | PASS |

## 备注
- should_not_trigger 为 0 容忍：任一误激活即 FAIL；其中至少 1 条为兄弟 skill 混淆诱饵。
- edge_case 验证 skill 文档 B 段（边界/护栏）是否被路由层识别，需人工结合预期行为复核。
- 跨 skill 混淆测试：每条 prompt 与全部 12 个 skill 的 trigger 签名打分，确认目标 skill 为最优归属。