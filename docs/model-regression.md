# Model Regression

## Purpose

Regression testing checks whether scoring behavior changed unexpectedly after code, service, data, or model updates. In AstraScore QA, regression is based on synthetic baselines and tolerance rules.

## What Is a Baseline?

A baseline is a reviewed expected output for a synthetic input case. It usually includes:

- case id
- expected score
- allowed tolerance
- expected decision

Example:

```json
{
  "caseId": "baseline-low-risk-001",
  "expectedScore": 742,
  "tolerance": 5,
  "expectedDecision": "approved"
}
```

## Expected vs Actual Comparison

For each baseline case:

1. The test obtains an actual score and decision.
2. The comparator calculates score delta.
3. The delta must stay within tolerance.
4. The decision must match the expected decision.

If the score exceeds tolerance or the decision changes, the comparison fails.

## Tolerance

Tolerance is used because some scoring changes can be acceptable within a small range. It should not be arbitrary. A tolerance value should be reviewed by a model owner or domain expert before production use.

## Updating a Baseline

Baseline updates should happen when:

- a model change is intentional
- the expected behavior is reviewed
- test evidence is attached to the pull request
- affected decision and risk segments are understood

## False Positive and False Negative Risks

False positives can occur when a safe expected model change is not reflected in the baseline.

False negatives can occur when tolerance is too wide or when only a small number of synthetic cases are covered.

## Human Approval

A failed regression test should not automatically imply that a model is wrong. It should trigger review by engineering, QA, and model stakeholders.
