# Marketable R&D: FlowBond And Receipt-Native Trust

## Brutal Thesis

The market does not need another agent, wallet, identity layer, RAG memory, or agent marketplace.

The missing primitive is **proof-carrying economic memory**: portable, user-controlled receipts of what agents actually did with money, so users can earn from useful history, control disclosure, prove safe execution, unlock better automation, and privately carry trust between agents.

FlowMemory should own:

```text
receipt-native memory for autonomous money
```

## Best Primitive

### FlowBond

FlowBond turns an agent promise into a bonded, FlowPulse-settled action.

Generic agents give advice.

FlowMemory agents leave bonded receipts.

## Why This Is More Marketable

Most AI-agent systems sell capability:

- the agent can trade;
- the agent can pay;
- the agent can call tools;
- the agent has a wallet;
- the agent has reputation;
- the agent has private execution.

FlowBond sells recourse:

```text
This agent will put money behind this action policy.
```

That is easier for users to understand than memory conformance.

## MVP

Build one bonded swap assistant:

1. User chooses a deterministic policy:
   - pair;
   - max spend;
   - min output;
   - max slippage;
   - expiry;
   - agent ID.
2. Agent posts a small bond against the policy.
3. Swap executes.
4. A FlowPulse-style receipt records:
   - policy hash;
   - agent ID;
   - amount bucket;
   - slippage bucket;
   - pass/fail;
   - outcome hash.
5. If the policy passed, the bond releases to the agent.
6. If the policy failed, the bond pays the user.

## Local Demo

```powershell
python -m flowmemory_compiler.cli flowbond-demo --pretty
```

Expected shape:

```text
FlowBond R&D Demo

Thesis:
  Generic agents give advice. FlowMemory agents can leave bonded receipts.

FB-OK-001  bonded_swap_policy_passed       PASSED RELEASE_BOND_TO_AGENT
FB-BAD-001 bonded_swap_policy_violated     FAILED PAY_BOND_TO_USER

Result:
  A deterministic policy turns an agent promise into a FlowPulse-settled warranty.
```

## Incentive Loop

Users prefer bonded agents because automation has recourse.

Agents bond actions to win users, charge higher fees, and unlock larger spend limits.

Developers compete on policies they are willing to warranty.

FlowMemory becomes the memory layer for agent promises.

## Privacy And Decentralization

The public chain only needs:

- policy hash;
- bond amount;
- settlement result;
- FlowPulse receipt hash.

The user keeps the full policy and history in a local or encrypted FlowMemory vault.

Later versions can add:

- selective disclosure;
- zero-knowledge predicates;
- TEE adjudication;
- ERC-8004 identity attachment;
- x402 payment linkage.

## Top Product Primitives

| Rank | Primitive | One-liner |
| --- | --- | --- |
| 1 | FlowBond | Agents with money on the line. |
| 2 | PulsePass | Your private receipt passport for autonomous money. |
| 3 | PulseRoyalties | Get paid when your past actions make future agents smarter. |
| 4 | SpendSafe Memory | Bigger agent limits earned by proven safe execution. |
| 5 | Receipt-Gated Deals | Perks unlocked by proof, not profiles. |
| 6 | Private Quote Passport | Better quotes without exposing the whole wallet. |
| 7 | PolicyCards | Your rules travel with every agent. |
| 8 | x402 Outcome Receipts | Paid tool calls linked to useful downstream outcomes. |
| 9 | PulseBounties | Protocols buy verified behavior, not scraped data. |
| 10 | Pulse Clean Rooms | Private computation over receipt vaults. |

## What Not To Claim

Do not claim:

- profit guarantee;
- custody;
- fund protection;
- swap control;
- every agent action is adjudicable;
- full privacy in the MVP;
- production bond adjudication;
- token yield or passive income;
- that users sell full data histories.

Claim this:

```text
Specific agent actions can be warrantied, carried, proven, and monetized through FlowPulse memory.
```

