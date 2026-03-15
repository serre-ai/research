# ReasonGap Analysis Summary

## Dataset Overview

- **Instances**: 139,573
- **Tasks**: 10
- **Models**: 10
- **Conditions**: 3
- **Models evaluated**: claude-haiku-4-5-20251001, gpt-4o, gpt-4o-mini, meta-llama/llama-3.1-70b-instruct, meta-llama/llama-3.1-8b-instruct, mistralai/ministral-8b-2512, mistralai/mistral-small-24b-instruct-2501, o3, qwen/qwen-2.5-72b-instruct, qwen/qwen-2.5-7b-instruct

## Overall Accuracy by Condition

- **budget_cot**: 0.640
- **direct**: 0.510
- **short_cot**: 0.707

## Results by Gap Type

### Type 1: Sensitivity

- budget_cot: 0.612
- direct: 0.602
- short_cot: 0.715
- CoT lift (budget_cot): +0.010
- CoT lift (short_cot): +0.114

### Type 2: Depth

- budget_cot: 0.777
- direct: 0.667
- short_cot: 0.814
- CoT lift (budget_cot): +0.110
- CoT lift (short_cot): +0.147

### Type 3: Serial

- budget_cot: 0.645
- direct: 0.266
- short_cot: 0.750
- CoT lift (budget_cot): +0.380
- CoT lift (short_cot): +0.484

### Type 4: Algorithmic

- budget_cot: 0.245
- direct: 0.227
- short_cot: 0.364
- CoT lift (budget_cot): +0.017
- CoT lift (short_cot): +0.137

### Type 5: Intractability

- budget_cot: 0.407
- direct: 0.477
- short_cot: 0.474
- CoT lift (budget_cot): -0.070
- CoT lift (short_cot): -0.004

### Type 6: Architectural

- budget_cot: 0.758
- direct: 0.712
- short_cot: 0.840
- CoT lift (budget_cot): +0.047
- CoT lift (short_cot): +0.129

## Key Predictions Check

- **Types 2,3 (should benefit from CoT)**: CoT lift = +0.316
- **Types 5,6 (should NOT benefit from CoT)**: CoT lift = +0.085
