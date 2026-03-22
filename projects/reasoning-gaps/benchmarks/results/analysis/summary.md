# ReasonGap Analysis Summary

## Dataset Overview

- **Instances**: 176,477
- **Tasks**: 9
- **Models**: 12
- **Conditions**: 9
- **Models evaluated**: claude-haiku-4-5-20251001, claude-opus-4-6, claude-sonnet-4-20250514, gpt-4o, gpt-4o-mini, meta-llama/llama-3.1-70b-instruct, meta-llama/llama-3.1-8b-instruct, mistralai/ministral-8b-2512, mistralai/mistral-small-24b-instruct-2501, o3, qwen/qwen-2.5-72b-instruct, qwen/qwen-2.5-7b-instruct

## Overall Accuracy by Condition

- **budget_cot**: 0.637
- **budget_cot_0.25x**: 0.278
- **budget_cot_0.5x**: 0.395
- **budget_cot_1.0x**: 0.496
- **budget_cot_2.0x**: 0.739
- **budget_cot_4.0x**: 0.788
- **direct**: 0.519
- **short_cot**: 0.739
- **tool_use**: 0.832

## Results by Gap Type

### Type 1: Sensitivity

- budget_cot: 0.606
- direct: 0.605
- short_cot: 0.737
- CoT lift (budget_cot): +0.001
- CoT lift (short_cot): +0.132

### Type 2: Depth

- budget_cot: 0.749
- budget_cot_0.25x: 0.444
- budget_cot_0.5x: 0.665
- budget_cot_1.0x: 0.861
- budget_cot_2.0x: 0.929
- budget_cot_4.0x: 0.937
- direct: 0.641
- short_cot: 0.840
- tool_use: 0.784
- CoT lift (budget_cot): +0.109
- CoT lift (budget_cot_0.25x): -0.197
- CoT lift (budget_cot_0.5x): +0.024
- CoT lift (budget_cot_1.0x): +0.221
- CoT lift (budget_cot_2.0x): +0.288
- CoT lift (budget_cot_4.0x): +0.296
- CoT lift (short_cot): +0.199
- CoT lift (tool_use): +0.144

### Type 3: Serial

- budget_cot: 0.670
- budget_cot_0.25x: 0.111
- budget_cot_0.5x: 0.124
- budget_cot_1.0x: 0.130
- budget_cot_2.0x: 0.549
- budget_cot_4.0x: 0.640
- direct: 0.280
- short_cot: 0.782
- CoT lift (budget_cot): +0.390
- CoT lift (budget_cot_0.25x): -0.169
- CoT lift (budget_cot_0.5x): -0.156
- CoT lift (budget_cot_1.0x): -0.150
- CoT lift (budget_cot_2.0x): +0.269
- CoT lift (budget_cot_4.0x): +0.359
- CoT lift (short_cot): +0.502

### Type 4: Algorithmic

- budget_cot: 0.296
- direct: 0.252
- short_cot: 0.400
- tool_use: 0.879
- CoT lift (budget_cot): +0.043
- CoT lift (short_cot): +0.148
- CoT lift (tool_use): +0.626

### Type 5: Intractability

- budget_cot: 0.390
- direct: 0.510
- short_cot: 0.514
- CoT lift (budget_cot): -0.120
- CoT lift (short_cot): +0.003

### Type 6: Architectural

- budget_cot: 0.788
- direct: 0.720
- short_cot: 0.864
- CoT lift (budget_cot): +0.068
- CoT lift (short_cot): +0.144

## Key Predictions Check

- **Types 2,3 (should benefit from CoT)**: CoT lift = +0.351
- **Types 5,6 (should NOT benefit from CoT)**: CoT lift = +0.094
