# ReasonGap Analysis Summary

## Dataset Overview

- **Instances**: 176,477
- **Tasks**: 9
- **Models**: 12
- **Conditions**: 4 (direct, short_cot, budget_cot, tool_use)
- **Models evaluated**: claude-haiku-4-5-20251001, claude-opus-4-6, claude-sonnet-4-20250514, gpt-4o, gpt-4o-mini, meta-llama/llama-3.1-70b-instruct, meta-llama/llama-3.1-8b-instruct, mistralai/ministral-8b-2512, mistralai/mistral-small-24b-instruct-2501, o3, qwen/qwen-2.5-72b-instruct, qwen/qwen-2.5-7b-instruct

## Overall Accuracy by Condition

- **budget_cot**: 0.637
- **direct**: 0.519
- **short_cot**: 0.739

## Results by Gap Type

### Type 1: Sensitivity

- budget_cot: 0.606
- direct: 0.605
- short_cot: 0.737
- CoT lift (budget_cot): +0.001
- CoT lift (short_cot): +0.132

### Type 2: Depth

- budget_cot: 0.749
- direct: 0.641
- short_cot: 0.840
- CoT lift (budget_cot): +0.109
- CoT lift (short_cot): +0.199

### Type 3: Serial

- budget_cot: 0.670
- direct: 0.280
- short_cot: 0.782
- CoT lift (budget_cot): +0.390
- CoT lift (short_cot): +0.502

### Type 4: Algorithmic

- budget_cot: 0.296
- direct: 0.252
- short_cot: 0.400
- CoT lift (budget_cot): +0.043
- CoT lift (short_cot): +0.148

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
