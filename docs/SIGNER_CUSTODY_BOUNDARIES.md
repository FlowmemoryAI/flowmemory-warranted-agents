# Signer And Custody Boundaries

FlowMemory Warranted Agents does not custody funds or control wallets.

This document defines what must remain outside the framework until a separate production integration is reviewed.

## The Framework May Sign

Local-only:

- release transcript hashes;
- launch packet hashes;
- local fixture receipts;
- adapter conformance outputs.

Production candidate:

- signed evidence attestations, only after signer policy is defined;
- signed adapter manifests, only after key management is defined.

## The Framework Must Not Sign

The framework must not sign:

- user wallet transactions;
- agent wallet transactions;
- bond transfers;
- payment settlements;
- custody withdrawals;
- production escrow actions;
- production x402 payments.

## Key Ownership

| Key type | Owner | Current repo status |
| --- | --- | --- |
| User wallet key | User or wallet provider | Out of scope |
| Agent wallet key | Agent operator | Out of scope |
| Bond/payment signer | Payment or settlement rail | Out of scope |
| Evidence signer | Future verifier operator | Not implemented |
| Release signer | Release operator | Local hash artifacts only |

## Before Any Real Settlement Path

Required evidence:

- external signer policy;
- key rotation procedure;
- emergency disable procedure;
- independent security review;
- production readiness packet with all gates satisfied;
- public claim gate still passing.

## Non-Claims

This repo does not claim custody, wallet enforcement, production settlement, escrow, fund protection, or production verifier infrastructure.
