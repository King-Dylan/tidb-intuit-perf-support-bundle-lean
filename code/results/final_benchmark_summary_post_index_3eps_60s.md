# post-index read-only 3eps 60s

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
| All | 181 | 181.0 ms | 631.3 ms | 1075.3 ms | 3354.2 ms | 21 | 19 |
| Normal | 175 | 174.6 ms | 577.8 ms | 1075.7 ms | 3354.2 ms | 15 | 14 |
| Hot-key | 6 | 621.8 ms | 679.2 ms | 691.9 ms | 695.0 ms | 6 | 5 |

## Bundle Coverage Scorecard

Henry's 60/65 rule: can the event proceed?

- By 350ms: 181/181 events passed (100.0%)
- By 500ms: 181/181 events passed (100.0%)

Andrew's 65/65 view: did we get every feature?

- By 350ms: 156/181 events were complete (86.2%)
- By 500ms: 156/181 events were complete (86.2%)

Average bundle coverage across all events:

- By 350ms: 64.8/65 bundles back on average
- By 500ms: 64.8/65 bundles back on average

## Coverage Detail by Event Type

| Scope | events | >=60/65 by 350ms | >=60/65 by 500ms | 65/65 by 350ms | 65/65 by 500ms | median by 350 | median by 500 | median errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| All | 181 | 181/181 | 181/181 | 156/181 | 156/181 | 65 | 65 | 0 |
| Normal | 175 | 175/175 | 175/175 | 156/175 | 156/175 | 65 | 65 | 0 |
| Hot-key | 6 | 6/6 | 6/6 | 0/6 | 0/6 | 62 | 63 | 2 |

## Bundle Return-Time Drop-Off

This shows how many additional bundle results land in each time window.

```text
Window      Avg bundles/event  Total bundle executions
0-50ms      14.8               2,683                  
50-100ms    31.8               5,760                  
100-150ms   12.7               2,302                  
150-200ms   4.8                862                    
200-350ms   0.6                114                    
350-500ms   0.0                5                      
>500/error  0.22               39                     
```

## Bundle Return-Time CDF

This shows how quickly bundle results become available across events.

```text
Cutoff           Avg bundles returned  Median returned  Events >=60/65  Events 65/65  Bundle executions
<=50ms           14.8/65               18               0/181           0/181         2683             
<=100ms          46.6/65               57               56/181          0/181         8443             
<=150ms          59.4/65               64               133/181         76/181        10745            
<=200ms          64.1/65               65               177/181         122/181       11607            
<=250ms          64.6/65               65               181/181         151/181       11701            
<=300ms          64.7/65               65               181/181         156/181       11716            
<=350ms          64.8/65               65               181/181         156/181       11721            
<=400ms          64.8/65               65               181/181         156/181       11724            
<=450ms          64.8/65               65               181/181         156/181       11725            
<=500ms          64.8/65               65               181/181         156/181       11726            
>500ms or error                                                                       39               
```

## Slow Bundles (>350ms)

Bundles with at least one run over 350ms: 15

| Bundle | Group | Window | Filter | Preagg | >350 | >500 | Errors | p95 | max | Kinds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| group_a_bundle_010 | A | 30 | p.check_bank_routing_number = %s | False | 0 | 0 | 15 | 206.9 ms | 287.9 ms | normal:12; hot_check_bank_routing_number:3 |
| group_a_bundle_006 | A | 7 | p.check_bank_routing_number = %s | False | 0 | 0 | 8 | 190.8 ms | 222.9 ms | normal:5; hot_check_bank_routing_number:3 |
| group_c_bundle_025 | C | 180 | p.merchant_account_number = %s | True | 0 | 0 | 4 | 216.4 ms | 236.2 ms | hot_merchant_account_number:2; normal:2 |
| group_b_bundle_018 | B | 180 | d.input_ip = %s | True | 0 | 0 | 3 | 150.2 ms | 193.3 ms | normal:3 |
| group_c_bundle_018 | C | 30 | d.true_ip = %s | False | 1 | 0 | 1 | 135.7 ms | 452.6 ms | normal:1 |
| group_c_bundle_021 | C | 30 | p.merchant_account_number = %s | False | 0 | 0 | 2 | 156.9 ms | 201.4 ms | hot_merchant_account_number:2 |
| group_b_bundle_020 | B | 180 | d.true_ip = %s | True | 0 | 0 | 2 | 154.0 ms | 191.2 ms | hot_true_ip:1; normal:1 |
| group_b_bundle_012 | B | 30 | d.true_ip = %s | False | 1 | 1 | 0 | 151.0 ms | 515.3 ms | hot_true_ip:1 |
| group_a_bundle_008 | A | 7 | p.merchant_account_number = %s | False | 1 | 0 | 0 | 192.2 ms | 439.1 ms | hot_merchant_account_number:1 |
| group_a_bundle_014 | A | 90 | p.check_bank_routing_number = %s | False | 1 | 0 | 0 | 256.4 ms | 393.6 ms | hot_check_bank_routing_number:1 |
| group_b_bundle_008 | B | 7 | d.true_ip = %s | False | 1 | 0 | 0 | 147.0 ms | 380.9 ms | normal:1 |
| group_c_bundle_011 | C | 7 | d.true_ip = %s | False | 1 | 0 | 0 | 137.3 ms | 359.2 ms | normal:1 |
| group_c_bundle_014 | C | 7 | p.merchant_account_number = %s | False | 0 | 0 | 1 | 159.1 ms | 271.9 ms | hot_merchant_account_number:1 |
| group_c_bundle_022 | C | 180 | d.exact_id = %s | True | 0 | 0 | 1 | 187.8 ms | 227.2 ms | normal:1 |
| group_c_bundle_007 | C | 1 | p.merchant_account_number = %s | False | 0 | 0 | 1 | 158.9 ms | 194.3 ms | hot_merchant_account_number:1 |
