# Data Contracts

This document describes the synthetic scoring contract used by examples and validator tests. It is not a real bank or customer schema.

## Request Schema

Required fields:

| Field | Type | Rule |
| --- | --- | --- |
| `applicantId` | string | Non-empty synthetic identifier. |
| `age` | integer | Between 18 and 75. |
| `monthlyIncome` | number | Zero or greater. |
| `employmentStatus` | string | Supported enum value. |
| `requestedAmount` | number | Greater than zero. |
| `existingDebt` | number | Zero or greater. |
| `creditHistoryMonths` | integer | Zero or greater. |

Supported `employmentStatus` values:

```text
full_time
part_time
self_employed
retired
student
unemployed
```

## Response Schema

Required fields:

| Field | Type | Rule |
| --- | --- | --- |
| `applicantId` | string | Non-empty synthetic identifier. |
| `score` | integer | Between 0 and 1000. |
| `decision` | string | One of `approved`, `review`, `rejected`. |
| `riskBand` | string | One of `low`, `medium`, `high`. |
| `reasonCodes` | list[string] | Non-empty strings when present. |

## Optional Fields

Future implementations may add optional metadata such as:

- `modelVersion`
- `correlationId`
- `evaluatedAt`
- `featureSnapshotId`

Optional fields should not break existing consumers.

## Invalid Payload Examples

Invalid examples include:

- empty `applicantId`
- `age` below 18 or above 75
- negative `monthlyIncome`
- unsupported `employmentStatus`
- zero or negative `requestedAmount`
- negative `existingDebt`
- negative `creditHistoryMonths`

## Backward Compatibility Rules

- Do not remove required response fields without a major version change.
- Do not change decision enum values without explicit migration.
- Additive optional fields are usually backward compatible.
- Narrowing accepted input ranges is a breaking change.

## Contract Breaking Changes

Examples of breaking changes:

- `score` changes from integer to string.
- `decision` changes from `approved` to `APPROVE` without migration.
- `reasonCodes` changes from list to object.
- `applicantId` is renamed without adapter support.
