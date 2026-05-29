# post-index tikv-only distinct-pushdown 3eps 60s

## Test Shape

- Duration: 60 seconds
- Read rate: 3.0 events/sec
- Hot-key mix target: 5.0%
- Scripted warmup: 0 seconds; skip initial preflight: True
- Read max_execution_time: 500 ms
- Pre-agg mode: hybrid
- Reads completed: 181 events (175 normal, 6 hot-key)
- Writes completed: 0 insert attempts
- Group C join key: p.parsed_interaction_id = d.interaction_id
- Group C timestamp filter: v15 applies both p.event_date >= cutoff and d.jms_timestamp >= cutoff on runtime Group C joins

## Binding Reuse / Test Realism

This run used 137 unique event IDs, and the full 8-ID binding set was unique for 137/181 events. We were not replaying one warmed event repeatedly.

| Field | Distinct values / 181 events | Max repeat |
| --- | --- | --- |
| check_bank_routing_number | 129 | 4 |
| merchant_account_number | 136 | 3 |
| card_holder_number_sha512 | 137 | 3 |
| check_bank_account_number_sha512 | 137 | 3 |
| exact_id | 137 | 3 |
| smart_id | 137 | 3 |
| input_ip | 137 | 3 |
| true_ip | 137 | 3 |

## Pre-Aggregation Scope

| Group | Keys / paths | Windows | Logical paths |
| --- | --- | --- | --- |
| Group A | routing, merchant | 30d / 90d / 180d | 6 |
| Group B | exact_id, smart_id, input_ip, true_ip | 30d / 90d / 180d | 12 |
| Group C | catalog long-window joined bundles 015-025 | 30d / 180d paths in catalog | 11 |

Pre-agg bundle IDs: group_a_bundle_017, group_a_bundle_018, group_a_bundle_019, group_a_bundle_020, group_b_bundle_017, group_b_bundle_018, group_b_bundle_019, group_b_bundle_020, group_c_bundle_022, group_c_bundle_023, group_c_bundle_024, group_c_bundle_025

## Runtime vs Pre-Agg Bundle Counts

Across 181 events: runtime bundle executions=9,593; pre-agg bundle executions=2,172.

| Group | Runtime bundles | Pre-agg bundles | Total bundles |
| --- | --- | --- | --- |
| Group A | 16 | 4 | 20 |
| Group B | 16 | 4 | 20 |
| Group C | 21 | 4 | 25 |
| Total | 53 | 12 | 65 |

## Hot-Key Values Used

| Field | Source | Hot value | Rows |
| --- | --- | --- | --- |
| merchant_account_number | payment | 5247719989330882 | 83,239 |
| card_holder_number_sha512 | payment | 298c861ec0265f1aa8d60ea899887ffd22039280e2f98bfe3819a360239ed2a9 | 5 |
| check_bank_routing_number | payment | 322271627 | 665,417 |
| check_bank_account_number_sha512 | payment | 09ee61f5a8d8259df1170dcc1a390dc74b0d2b724d311d231457ab994b68ee1d | 851 |
| exact_id | device | 31e04c7aac0e47059f0342b27108e7e4 | 46,913 |
| smart_id | device | 2222fa4682e8429498969e3568a2941a | 390,326 |
| input_ip | device | 72.153.231.69 | 803,112 |
| true_ip | device | 74.179.68.52 | 748,059 |

## Event Latency

| Scope | n | p50 | p95 | p99 | max | >350ms | >500ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| All | 181 | 204.5 ms | 582.9 ms | 783.9 ms | 1063.8 ms | 34 | 28 |
| Normal | 175 | 203.4 ms | 583.9 ms | 786.9 ms | 1063.8 ms | 28 | 22 |
| Hot-key | 6 | 557.9 ms | 576.4 ms | 576.4 ms | 576.4 ms | 6 | 6 |

## Bundle Coverage Scorecard

Henry's 60/65 rule: can the event proceed?

- By 350ms: 179/181 events passed (98.9%)
- By 500ms: 181/181 events passed (100.0%)

Andrew's 65/65 view: did we get every feature?

- By 350ms: 147/181 events were complete (81.2%)
- By 500ms: 153/181 events were complete (84.5%)

Average bundle coverage across all events:

- By 350ms: 64.2/65 bundles back on average
- By 500ms: 64.7/65 bundles back on average

## Coverage Detail by Event Type

| Scope | events | >=60/65 by 350ms | >=60/65 by 500ms | 65/65 by 350ms | 65/65 by 500ms | median by 350 | median by 500 | median errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| All | 181 | 179/181 | 181/181 | 147/181 | 153/181 | 65 | 65 | 0 |
| Normal | 175 | 173/175 | 175/175 | 147/175 | 153/175 | 65 | 65 | 0 |
| Hot-key | 6 | 6/6 | 6/6 | 0/6 | 0/6 | 62 | 64 | 2 |

## Bundle Return-Time Drop-Off

This shows how many additional bundle results land in each time window.

```text
Window      Avg bundles/event  Total bundle executions
0-50ms      10.8               1,953                  
50-100ms    28.2               5,110                  
100-150ms   15.3               2,778                  
150-200ms   7.1                1,290                  
200-350ms   2.7                484                    
350-500ms   0.6                104                    
>500/error  0.25               46                     
```

## Bundle Return-Time CDF

This shows how quickly bundle results become available across events.

```text
Cutoff           Avg bundles returned  Median returned  Events >=60/65  Events 65/65  Bundle executions
<=50ms           10.8/65               10               0/181           0/181         1953             
<=100ms          39.0/65               52               20/181          0/181         7063             
<=150ms          54.4/65               61               101/181         17/181        9841             
<=200ms          61.5/65               65               156/181         91/181        11131            
<=250ms          62.8/65               65               169/181         126/181       11367            
<=300ms          63.7/65               65               175/181         141/181       11523            
<=350ms          64.2/65               65               179/181         147/181       11615            
<=400ms          64.5/65               65               180/181         147/181       11666            
<=450ms          64.6/65               65               180/181         151/181       11698            
<=500ms          64.7/65               65               181/181         153/181       11719            
>500ms or error                                                                       46               
```

## Slow Bundles (>350ms)

Bundles with at least one run over 350ms: 65

| Bundle | Group | Window | Filter | Preagg | >350 | >500 | Errors | p95 | max | Kinds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| group_a_bundle_010 | A | 30 | p.check_bank_routing_number = %s | False | 12 | 5 | 11 | 432.3 ms | 661.8 ms | normal:12 |
| group_c_bundle_025 | C | 180 | p.merchant_account_number = %s | True | 4 | 2 | 4 | 283.0 ms | 592.3 ms | normal:4 |
| group_a_bundle_006 | A | 7 | p.check_bank_routing_number = %s | False | 8 | 1 | 0 | 346.8 ms | 505.5 ms | normal:7; hot_check_bank_routing_number:1 |
| group_a_bundle_014 | A | 90 | p.check_bank_routing_number = %s | False | 6 | 0 | 0 | 274.2 ms | 487.7 ms | normal:3; hot_check_bank_routing_number:3 |
| group_b_bundle_006 | B | 7 | d.input_ip = %s | False | 4 | 0 | 0 | 188.7 ms | 472.9 ms | normal:4 |
| group_b_bundle_020 | B | 180 | d.true_ip = %s | True | 2 | 0 | 2 | 195.2 ms | 432.5 ms | normal:2 |
| group_b_bundle_018 | B | 180 | d.input_ip = %s | True | 1 | 0 | 3 | 173.8 ms | 431.1 ms | normal:1 |
| group_b_bundle_010 | B | 30 | d.input_ip = %s | False | 1 | 0 | 3 | 168.2 ms | 408.0 ms | normal:1 |
| group_c_bundle_016 | C | 30 | d.input_ip = %s | False | 2 | 0 | 2 | 157.4 ms | 401.1 ms | normal:2 |
| group_b_bundle_008 | B | 7 | d.true_ip = %s | False | 2 | 1 | 1 | 173.7 ms | 516.6 ms | normal:2 |
| group_c_bundle_022 | C | 180 | d.exact_id = %s | True | 2 | 0 | 1 | 261.7 ms | 474.2 ms | normal:2 |
| group_c_bundle_024 | C | 180 | p.card_holder_number_sha512 = %s | True | 3 | 0 | 0 | 267.8 ms | 471.3 ms | normal:3 |
| group_c_bundle_023 | C | 180 | d.smart_id = %s | True | 3 | 0 | 0 | 260.5 ms | 466.8 ms | normal:3 |
| group_c_bundle_021 | C | 30 | p.merchant_account_number = %s | False | 1 | 0 | 2 | 185.0 ms | 450.1 ms | normal:1 |
| group_c_bundle_018 | C | 30 | d.true_ip = %s | False | 1 | 0 | 2 | 155.1 ms | 403.6 ms | normal:1 |
| group_b_bundle_012 | B | 30 | d.true_ip = %s | False | 1 | 0 | 2 | 167.3 ms | 398.2 ms | normal:1 |
| group_a_bundle_001 | A | 1 | p.card_holder_number_sha512 = %s | False | 2 | 1 | 0 | 213.1 ms | 506.1 ms | normal:2 |
| group_a_bundle_009 | A | 30 | p.card_holder_number_sha512 = %s | False | 2 | 0 | 0 | 212.5 ms | 498.3 ms | normal:2 |
| group_a_bundle_012 | A | 30 | p.merchant_account_number = %s | False | 2 | 0 | 0 | 206.7 ms | 495.8 ms | normal:2 |
| group_a_bundle_005 | A | 7 | p.card_holder_number_sha512 = %s | False | 2 | 0 | 0 | 217.5 ms | 495.4 ms | normal:2 |
| group_a_bundle_004 | A | 1 | p.merchant_account_number = %s | False | 2 | 0 | 0 | 199.7 ms | 493.8 ms | normal:2 |
| group_a_bundle_002 | A | 1 | p.check_bank_routing_number = %s | False | 2 | 0 | 0 | 204.5 ms | 487.4 ms | normal:2 |
| group_a_bundle_003 | A | 1 | p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s | False | 2 | 0 | 0 | 189.7 ms | 478.5 ms | normal:2 |
| group_a_bundle_008 | A | 7 | p.merchant_account_number = %s | False | 2 | 0 | 0 | 203.2 ms | 476.1 ms | normal:2 |
| group_a_bundle_016 | A | 90 | p.merchant_account_number = %s | False | 2 | 0 | 0 | 189.7 ms | 468.7 ms | normal:2 |
| group_a_bundle_007 | A | 7 | p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s | False | 2 | 0 | 0 | 189.3 ms | 465.3 ms | normal:2 |
| group_c_bundle_007 | C | 1 | p.merchant_account_number = %s | False | 1 | 0 | 1 | 178.5 ms | 456.3 ms | normal:1 |
| group_c_bundle_014 | C | 7 | p.merchant_account_number = %s | False | 1 | 0 | 1 | 178.5 ms | 432.6 ms | normal:1 |
| group_c_bundle_001 | C | 1 | d.exact_id = %s | False | 2 | 0 | 0 | 168.6 ms | 419.9 ms | hot_merchant_account_number:1; normal:1 |
| group_b_bundle_009 | B | 30 | d.exact_id = %s | False | 2 | 0 | 0 | 182.6 ms | 415.5 ms | normal:2 |
| group_c_bundle_011 | C | 7 | d.true_ip = %s | False | 1 | 0 | 1 | 151.5 ms | 382.2 ms | normal:1 |
| group_b_bundle_017 | B | 180 | d.exact_id = %s | True | 1 | 0 | 0 | 198.0 ms | 443.0 ms | normal:1 |
| group_a_bundle_011 | A | 30 | p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s | False | 1 | 0 | 0 | 182.5 ms | 440.6 ms | normal:1 |
| group_b_bundle_003 | B | 1 | d.smart_id = %s | False | 1 | 0 | 0 | 178.1 ms | 439.8 ms | normal:1 |
| group_b_bundle_007 | B | 7 | d.smart_id = %s | False | 1 | 0 | 0 | 173.2 ms | 435.6 ms | normal:1 |
| group_b_bundle_001 | B | 1 | d.exact_id = %s | False | 1 | 0 | 0 | 175.1 ms | 428.6 ms | normal:1 |
| group_b_bundle_019 | B | 180 | d.smart_id = %s | True | 1 | 0 | 0 | 189.3 ms | 426.5 ms | normal:1 |
| group_b_bundle_011 | B | 30 | d.smart_id = %s | False | 1 | 0 | 0 | 171.5 ms | 424.0 ms | normal:1 |
| group_c_bundle_015 | C | 30 | d.exact_id = %s | False | 1 | 0 | 0 | 172.2 ms | 422.5 ms | normal:1 |
| group_b_bundle_005 | B | 7 | d.exact_id = %s | False | 1 | 0 | 0 | 173.6 ms | 422.0 ms | normal:1 |
| group_c_bundle_019 | C | 30 | p.card_holder_number_sha512 = %s | False | 1 | 0 | 0 | 170.0 ms | 419.2 ms | normal:1 |
| group_b_bundle_004 | B | 1 | d.true_ip = %s | False | 1 | 0 | 0 | 169.2 ms | 408.9 ms | normal:1 |
| group_b_bundle_002 | B | 1 | d.input_ip = %s | False | 1 | 0 | 0 | 171.6 ms | 408.8 ms | normal:1 |
| group_a_bundle_019 | A | 180 | p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s | True | 1 | 0 | 0 | 155.4 ms | 402.5 ms | normal:1 |
| group_a_bundle_020 | A | 180 | p.merchant_account_number = %s | True | 1 | 0 | 0 | 154.3 ms | 401.8 ms | normal:1 |
| group_a_bundle_017 | A | 180 | p.card_holder_number_sha512 = %s | True | 1 | 0 | 0 | 150.4 ms | 397.3 ms | normal:1 |
| group_c_bundle_017 | C | 30 | d.smart_id = %s | False | 1 | 0 | 0 | 154.5 ms | 396.8 ms | normal:1 |
| group_a_bundle_018 | A | 180 | p.check_bank_routing_number = %s | True | 1 | 0 | 0 | 165.5 ms | 396.6 ms | normal:1 |
| group_c_bundle_010 | C | 7 | d.smart_id = %s | False | 1 | 0 | 0 | 158.8 ms | 394.5 ms | normal:1 |
| group_c_bundle_012 | C | 7 | p.card_holder_number_sha512 = %s | False | 1 | 0 | 0 | 159.5 ms | 392.8 ms | normal:1 |
| group_b_bundle_015 | B | 90 | d.smart_id = %s | False | 1 | 0 | 0 | 148.9 ms | 392.6 ms | normal:1 |
| group_c_bundle_005 | C | 1 | p.card_holder_number_sha512 = %s | False | 1 | 0 | 0 | 162.9 ms | 392.0 ms | normal:1 |
| group_c_bundle_008 | C | 7 | d.exact_id = %s | False | 1 | 0 | 0 | 168.0 ms | 391.4 ms | normal:1 |
| group_c_bundle_020 | C | 30 | p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s | False | 1 | 0 | 0 | 150.5 ms | 389.6 ms | normal:1 |
| group_b_bundle_013 | B | 90 | d.exact_id = %s | False | 1 | 0 | 0 | 154.0 ms | 387.7 ms | normal:1 |
| group_a_bundle_013 | A | 90 | p.card_holder_number_sha512 = %s | False | 1 | 0 | 0 | 144.2 ms | 387.5 ms | normal:1 |
| group_c_bundle_003 | C | 1 | d.smart_id = %s | False | 1 | 0 | 0 | 154.6 ms | 387.4 ms | normal:1 |
| group_b_bundle_014 | B | 90 | d.input_ip = %s | False | 1 | 0 | 0 | 149.2 ms | 387.1 ms | normal:1 |
| group_c_bundle_013 | C | 7 | p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s | False | 1 | 0 | 0 | 144.4 ms | 386.2 ms | normal:1 |
| group_c_bundle_006 | C | 1 | p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s | False | 1 | 0 | 0 | 149.7 ms | 386.1 ms | normal:1 |
| group_c_bundle_002 | C | 1 | d.input_ip = %s | False | 1 | 0 | 0 | 149.3 ms | 385.4 ms | normal:1 |
| group_c_bundle_009 | C | 7 | d.input_ip = %s | False | 1 | 0 | 0 | 152.1 ms | 385.1 ms | normal:1 |
| group_c_bundle_004 | C | 1 | d.true_ip = %s | False | 1 | 0 | 0 | 146.7 ms | 385.0 ms | normal:1 |
| group_a_bundle_015 | A | 90 | p.check_bank_routing_number = %s AND p.check_bank_account_number_sha512 = %s | False | 1 | 0 | 0 | 146.5 ms | 382.1 ms | normal:1 |
| group_b_bundle_016 | B | 90 | d.true_ip = %s | False | 1 | 0 | 0 | 149.1 ms | 380.3 ms | normal:1 |
