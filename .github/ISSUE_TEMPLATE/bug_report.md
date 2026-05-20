---
name: Bug report
description: Report a reproducible problem in the local warranted-agent framework
title: "bug: "
labels: [bug]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for helping tighten FlowMemory Warranted Agents. Please do not include secrets, private keys, seed phrases, RPC credentials, or funded-wallet details.
  - type: textarea
    id: summary
    attributes:
      label: Summary
      description: What failed?
    validations:
      required: true
  - type: textarea
    id: reproduce
    attributes:
      label: Reproduction steps
      description: Include the exact local command or fixture path if possible.
      placeholder: |
        1. Run `python -m ...`
        2. Observe ...
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: Actual behavior
    validations:
      required: true
  - type: dropdown
    id: area
    attributes:
      label: Area
      options:
        - PolicyCard / FlowBond
        - PulsePass / scoped proof
        - FlowCompiler conformance
        - PulseRouter / PulsePods
        - Release transcript / launch packet
        - Documentation
        - Other
    validations:
      required: true
  - type: textarea
    id: checks
    attributes:
      label: Checks run
      description: Paste command names and pass/fail status only. Do not paste secrets.
---
