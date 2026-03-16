# ReasonGap Analysis Summary

## Dataset Overview

- **Instances**: 148,068
- **Tasks**: 9
- **Models**: 11
- **Conditions**: 3
- **Models evaluated**: claude-haiku-4-5-20251001, claude-sonnet-4-20250514, gpt-4o, gpt-4o-mini, meta-llama/llama-3.1-70b-instruct, meta-llama/llama-3.1-8b-instruct, mistralai/ministral-8b-2512, mistralai/mistral-small-24b-instruct-2501, o3, qwen/qwen-2.5-72b-instruct, qwen/qwen-2.5-7b-instruct

## Overall Accuracy by Condition

- **budget_cot**: 0.618
- **direct**: 0.503
- **short_cot**: 0.720

## Results by Gap Type

### Type 1: Sensitivity

- budget_cot: 0.603
- direct: 0.603
- short_cot: 0.726
- CoT lift (budget_cot): +0.000
- CoT lift (short_cot): +0.123

### Type 2: Depth

- budget_cot: 0.733
- direct: 0.644
- short_cot: 0.826
- CoT lift (budget_cot): +0.089
- CoT lift (short_cot): +0.182

### Type 3: Serial

- budget_cot: 0.645
- direct: 0.265
- short_cot: 0.763
- CoT lift (budget_cot): +0.380
- CoT lift (short_cot): +0.498

### Type 4: Algorithmic

- budget_cot: 0.254
- direct: 0.218
- short_cot: 0.379
- CoT lift (budget_cot): +0.036
- CoT lift (short_cot): +0.161

### Type 5: Intractability

- budget_cot: 0.401
- direct: 0.452
- short_cot: 0.490
- CoT lift (budget_cot): -0.051
- CoT lift (short_cot): +0.038

### Type 6: Architectural

- budget_cot: 0.770
- direct: 0.720
- short_cot: 0.854
- CoT lift (budget_cot): +0.050
- CoT lift (short_cot): +0.134

## Key Predictions Check

- **Types 2,3 (should benefit from CoT)**: CoT lift = +0.340
- **Types 5,6 (should NOT benefit from CoT)**: CoT lift = +0.102
