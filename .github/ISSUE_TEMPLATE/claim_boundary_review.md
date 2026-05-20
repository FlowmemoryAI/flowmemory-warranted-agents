---
name: Claim boundary review
description: Flag public wording that may exceed the current local v0 evidence
title: "claim-boundary: "
labels: [documentation, claim-boundary]
body:
  - type: markdown
    attributes:
      value: |
        Use this when repo language appears to imply production custody, settlement, adjudication, verifier readiness, live deployment, semantic truth, or model correctness beyond the current local v0 package.
  - type: textarea
    id: location
    attributes:
      label: Location
      description: File, section, URL, or quote.
    validations:
      required: true
  - type: textarea
    id: concern
    attributes:
      label: Concern
      description: What does the wording appear to claim?
    validations:
      required: true
  - type: textarea
    id: suggested
    attributes:
      label: Suggested safer wording
      description: Optional replacement that keeps the claim bold but bounded.
---
