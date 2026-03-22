# Between-Model Error Correlation Analysis

**Condition**: short_cot
**Models**: 12

## Results

| Task | VC Class | Error Rate | Correlation | Struct Hard | Model Dep |
|------|----------|-----------|-------------|-------------|----------|
| B1 | P | 26.3% | 0.218 | 2.0% | 47.0% |
| B2 | P | 13.9% | 0.223 | 0.4% | 25.4% |
| B3 | P | 21.4% | 0.316 | 0.4% | 29.8% |
| B4 | P | 22.3% | 0.216 | 1.6% | 39.2% |
| B5 | P | 18.9% | 0.114 | 0.0% | 39.4% |
| B6 | P | 63.3% | 0.417 | 41.4% | 49.2% |
| B7 | P/coNP | 49.6% | 0.064 | 5.6% | 92.2% |
| B8 | Arch | 1.1% | 0.146 | 0.0% | 1.0% |
| B9 | Arch | 28.1% | 0.071 | 0.0% | 65.4% |

## Key Finding

Error correlation is **highest** for algorithmic tasks (B6: 0.417) where all models
share a knowledge bottleneck, and **lowest** for NP-hard tasks (B7: 0.067) where
instance-level hardness is stochastic. Models use different heuristics for 3-SAT,
so they fail on different random instances.

This contradicts the naive prediction that hard-VC tasks have high error correlation.
The refined prediction: correlation tracks **shared structural bottlenecks** (algorithmic
knowledge, depth limits) rather than worst-case computational complexity.
