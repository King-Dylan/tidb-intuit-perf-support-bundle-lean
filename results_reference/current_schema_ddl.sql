-- database/version: ('intuit_risk', '8.0.11-TiDB-v8.5.4-nextgen.202510.18')

-- ------------------------------------------------------------
-- pmt_txn_fact
-- ------------------------------------------------------------
CREATE TABLE `pmt_txn_fact` (
  `merchant_account_number` bigint DEFAULT NULL COMMENT 'PaymentTransactionSource.accountNumber',
  `authorization_date` datetime DEFAULT NULL COMMENT 'PaymentTransactionSource.authorizationDate',
  `batch_date` datetime DEFAULT NULL COMMENT 'PaymentTransactionSource.batchDate',
  `transaction_id` varchar(64) DEFAULT NULL COMMENT 'PaymentTransactionSource.transactionId',
  `realm_id` varchar(64) DEFAULT NULL COMMENT 'PaymentTransactionSource.realmId',
  `invoice_number` varchar(64) NOT NULL COMMENT 'PaymentTransactionSource.invoiceNumber',
  `mas_transaction_netted` int DEFAULT NULL COMMENT 'PaymentTransactionSource.masTransactionNetted',
  `transaction_status_id` int DEFAULT NULL COMMENT 'PaymentTransactionSource.transactionStatusId',
  `mt_result_code` int DEFAULT NULL COMMENT 'PaymentTransactionSource.mtResultCode',
  `amount` decimal(15,2) DEFAULT NULL COMMENT 'PaymentTransactionSource.amount',
  `authorization_code` varchar(64) DEFAULT NULL COMMENT 'PaymentTransactionSource.authorizationCode',
  `cutoff_date` datetime DEFAULT NULL COMMENT 'PaymentTransactionSource.cutoffDate',
  `transaction_type` varchar(64) DEFAULT NULL COMMENT 'PaymentTransactionSource.transactionType',
  `mt_invoice_id` varchar(128) DEFAULT NULL COMMENT 'PaymentTransactionSource.mtInvoiceId',
  `mt_gateway` varchar(64) DEFAULT NULL COMMENT 'PaymentTransactionSource.mtGateway',
  `entry_method` varchar(32) DEFAULT NULL COMMENT 'PaymentTransactionSource.entryMethod',
  `currency_code` varchar(16) DEFAULT NULL COMMENT 'PaymentTransactionSource.currencyCode',
  `number_type_code` varchar(32) DEFAULT NULL COMMENT 'PaymentTransactionSource.numberTypeCode',
  `deposit_id` varchar(128) DEFAULT NULL COMMENT 'PaymentTransactionSource.depositId',
  `is_ready_for_risk` datetime DEFAULT NULL COMMENT 'PaymentTransactionSource.isReadyForRisk',
  `transaction_date` datetime DEFAULT NULL COMMENT 'PaymentTransactionSource.transactionDate',
  `event_date` bigint NOT NULL COMMENT 'Query-facing event timestamp in epoch millis',
  `mt_avs_street_match` varchar(16) DEFAULT NULL COMMENT 'PaymentTransactionSource.mtAvsStreetMatch',
  `application_type` varchar(64) DEFAULT NULL COMMENT 'PaymentTransactionSource.applicationType',
  `pts_intuit_qual_code` varchar(64) DEFAULT NULL COMMENT 'PaymentTransactionSource.ptsIntuitQualCode',
  `hk_modified` datetime DEFAULT NULL COMMENT 'PaymentTransactionSource.hkModified',
  `pos_entry_mode_code` varchar(32) DEFAULT NULL COMMENT 'PaymentTransactionSource.posEntryMode',
  `mt_vendor_result_code` varchar(64) DEFAULT NULL COMMENT 'PaymentTransactionSource.mtVendorResultCode',
  `mt_response_message` varchar(256) DEFAULT NULL COMMENT 'PaymentTransactionSource.mtResponseMessage',
  `mt_card_country_code` varchar(16) DEFAULT NULL COMMENT 'PaymentTransactionSource.mtCardCountryCode',
  `mt_avs_zip_match` varchar(16) DEFAULT NULL COMMENT 'PaymentTransactionSource.mtAvsZipMatch',
  `mt_card_holder_name` varchar(128) DEFAULT NULL COMMENT 'PaymentTransactionSource.mtCardHolderName',
  `mt_ip_address` varchar(45) DEFAULT NULL COMMENT 'PaymentTransactionSource.mtIpAddress',
  `card_holder_number_sha512` varchar(128) DEFAULT NULL COMMENT 'PaymentTransactionSource.cardHolderNumberSha512',
  `card_number_left` varchar(32) DEFAULT NULL COMMENT 'PaymentTransactionSource.cardNumberLeft',
  `check_bank_routing_number` varchar(32) DEFAULT NULL COMMENT 'PaymentTransactionSource.checkBankRoutingNumber',
  `check_bank_account_number_sha512` varchar(128) DEFAULT NULL COMMENT 'PaymentTransactionSource.checkBankAccountNumberSha512',
  `card_type` varchar(32) DEFAULT NULL COMMENT 'PaymentTransactionSource.cardType',
  `risk_profile_token` varchar(128) DEFAULT NULL COMMENT 'PaymentTransactionSource.riskProfileToken',
  `parsed_interaction_id` varchar(64) DEFAULT NULL COMMENT 'Physical join key parsed from risk_profile_token suffix for Group C',
  `interaction_id` varchar(128) DEFAULT NULL COMMENT 'PaymentTransactionSource.interactionId',
  `session_id` varchar(128) DEFAULT NULL COMMENT 'PaymentTransactionSource.sessionId',
  `is_swiped` tinyint(1) DEFAULT NULL COMMENT 'PaymentTransactionSource.isSwiped',
  `orig_batch_date` datetime DEFAULT NULL COMMENT 'PaymentTransactionSource.origBatchDate',
  `hk_source_id` decimal(20,0) DEFAULT NULL COMMENT 'PaymentTransactionSource.hkSourceId',
  PRIMARY KEY (`invoice_number`,`event_date`) /*T![clustered_index] NONCLUSTERED */,
  KEY `idx_merchant_account_number_event_date` (`merchant_account_number`,`event_date`),
  KEY `idx_card_holder_number_sha512_event_date` (`card_holder_number_sha512`,`event_date`),
  KEY `idx_check_bank_routing_number_event_date` (`check_bank_routing_number`,`event_date`),
  KEY `idx_check_routing_account_event` (`check_bank_routing_number`,`check_bank_account_number_sha512`,`event_date`),
  KEY `idx_risk_profile_token` (`risk_profile_token`),
  KEY `idx_parsed_interaction_id_event_date` (`parsed_interaction_id`,`event_date`),
  KEY `idx_interaction_id` (`interaction_id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_event_date` (`event_date`),
  KEY `idx_pmt_merchant_runtime_cov` (`merchant_account_number`,`event_date`,`amount`,`mt_gateway`,`card_type`,`entry_method`,`transaction_type`),
  KEY `idx_pmt_card_runtime_cov` (`card_holder_number_sha512`,`event_date`,`amount`,`mt_gateway`,`card_type`,`entry_method`,`mt_avs_street_match`,`transaction_type`),
  KEY `idx_pmt_routing_runtime_cov` (`check_bank_routing_number`,`event_date`,`amount`,`mt_gateway`,`card_type`,`entry_method`,`transaction_type`),
  KEY `idx_pmt_routing_account_runtime_cov` (`check_bank_routing_number`,`check_bank_account_number_sha512`,`event_date`,`amount`,`mt_gateway`,`card_type`,`entry_method`),
  KEY `idx_pmt_join_runtime_cov` (`parsed_interaction_id`,`event_date`,`amount`,`merchant_account_number`,`card_holder_number_sha512`,`card_type`,`entry_method`,`mt_gateway`,`check_bank_routing_number`,`transaction_type`),
  KEY `idx_pmt_merchant_c_join_cov` (`merchant_account_number`,`event_date`,`parsed_interaction_id`,`transaction_type`),
  KEY `idx_pmt_card_c_join_cov` (`card_holder_number_sha512`,`event_date`,`parsed_interaction_id`,`transaction_type`),
  KEY `idx_pmt_routing_acct_c_join_cov` (`check_bank_routing_number`,`check_bank_account_number_sha512`,`event_date`,`parsed_interaction_id`,`transaction_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /*T! SHARD_ROW_ID_BITS=4 PRE_SPLIT_REGIONS=3 */
PARTITION BY RANGE (`event_date`)
(PARTITION `p20251101` VALUES LESS THAN (1761955200000),
 PARTITION `p20251201` VALUES LESS THAN (1764547200000),
 PARTITION `p20260101` VALUES LESS THAN (1767225600000),
 PARTITION `p20260201` VALUES LESS THAN (1769904000000),
 PARTITION `p20260301` VALUES LESS THAN (1772323200000),
 PARTITION `p20260401` VALUES LESS THAN (1775001600000),
 PARTITION `p20260501` VALUES LESS THAN (1777593600000),
 PARTITION `p20260601` VALUES LESS THAN (1780272000000),
 PARTITION `pmax` VALUES LESS THAN (MAXVALUE));

-- ------------------------------------------------------------
-- deviceprofile_fact
-- ------------------------------------------------------------
CREATE TABLE `deviceprofile_fact` (
  `intuit_tid` varchar(64) DEFAULT NULL COMMENT 'RssDeviceSource.intuitTid',
  `realm_id` varchar(64) DEFAULT NULL COMMENT 'RssDeviceSource.realmId',
  `message_id` varchar(64) DEFAULT NULL COMMENT 'RssDeviceSource.messageId',
  `request_id` varchar(64) DEFAULT NULL COMMENT 'RssDeviceSource.requestId',
  `event_type` varchar(64) DEFAULT NULL COMMENT 'RssDeviceSource.eventType',
  `app_id` varchar(64) DEFAULT NULL COMMENT 'RssDeviceSource.appId',
  `api_name` varchar(64) DEFAULT NULL COMMENT 'RssDeviceSource.apiName',
  `api_result` int DEFAULT NULL COMMENT 'RssDeviceSource.apiResult',
  `offering_id` varchar(128) DEFAULT NULL COMMENT 'RssDeviceSource.offeringId',
  `transaction_id` varchar(64) DEFAULT NULL COMMENT 'RssDeviceSource.transactionId',
  `org_id` varchar(64) DEFAULT NULL COMMENT 'RssDeviceSource.orgId',
  `user_session_id` varchar(128) DEFAULT NULL COMMENT 'RssDeviceSource.userSessionId',
  `request_duration` varchar(32) DEFAULT NULL COMMENT 'RssDeviceSource.requestDuration',
  `request_result` varchar(32) DEFAULT NULL COMMENT 'RssDeviceSource.requestResult',
  `business_transaction` varchar(64) DEFAULT NULL COMMENT 'RssDeviceSource.businessTransaction',
  `jms_timestamp` datetime DEFAULT NULL COMMENT 'RssDeviceSource.jmsTimestamp',
  `interaction_id` varchar(128) DEFAULT NULL COMMENT 'RssDeviceSource.interactionId',
  `session_id` varchar(128) DEFAULT NULL COMMENT 'Optional session component; Group C joins on parsed interaction_id per Henry',
  `intuit_jmsbodyapiname` varchar(64) DEFAULT NULL COMMENT 'RssDeviceSource.intuit_jmsbodyapiname',
  `exact_id` varchar(64) DEFAULT NULL COMMENT 'DeviceProfile.exactId',
  `smart_id` varchar(64) DEFAULT NULL COMMENT 'DeviceProfile.smartId',
  `input_ip` varchar(45) DEFAULT NULL COMMENT 'DeviceProfile.inputIp',
  `true_ip` varchar(45) DEFAULT NULL COMMENT 'DeviceProfile.trueIp',
  `proxy_ip` varchar(45) DEFAULT NULL COMMENT 'DeviceProfile.proxyIp',
  `agent_type` varchar(32) DEFAULT NULL COMMENT 'DeviceProfile.agentType',
  `agent_os` varchar(32) DEFAULT NULL COMMENT 'DeviceProfile.agentOs',
  `browser_language` varchar(64) DEFAULT NULL COMMENT 'DeviceProfile.browserLanguage',
  `browser_string` varchar(256) DEFAULT NULL COMMENT 'DeviceProfile.browserString',
  `device_match_result` varchar(32) DEFAULT NULL COMMENT 'DeviceProfile.deviceMatchResult',
  `dns_ip` varchar(45) DEFAULT NULL COMMENT 'DeviceProfile.dnsIp',
  `input_ip_geo` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.inputIpGeo',
  `input_ip_isp` varchar(64) DEFAULT NULL COMMENT 'DeviceProfile.inputIpIsp',
  `input_ip_score` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.inputIpScore',
  `true_ip_geo` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.trueIpGeo',
  `true_ip_isp` varchar(64) DEFAULT NULL COMMENT 'DeviceProfile.trueIpIsp',
  `true_ip_result` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.trueIpResult',
  `true_ip_score` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.trueIpScore',
  `proxy_ip_geo` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.proxyIpGeo',
  `proxy_ip_isp` varchar(64) DEFAULT NULL COMMENT 'DeviceProfile.proxyIpIsp',
  `proxy_type` varchar(32) DEFAULT NULL COMMENT 'DeviceProfile.proxyType',
  `proxy_ip_score` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.proxyIpScore',
  `device_score` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.deviceScore',
  `device_fingerprint_score` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.deviceFingerprintScore',
  `device_worst_score` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.deviceWorstScore',
  `fuzzy_device_score` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.fuzzyDeviceScore',
  `true_ip_worst_score` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.trueIpWorstScore',
  `proxy_ip_worst_score` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.proxyIpWorstScore',
  `device_fingerprint_result` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.deviceFingerprintResult',
  `device_result` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.deviceResult',
  `proxy_ip_result` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.proxyIpResult',
  `fuzzy_device_result` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.fuzzyDeviceResult',
  `dns_ip_hosting_facility` varchar(64) DEFAULT NULL COMMENT 'DeviceProfile.dnsIpHostingFacility',
  `proxy_ip_hosting_facility` varchar(64) DEFAULT NULL COMMENT 'DeviceProfile.proxyIpHostingFacility',
  `true_ip_hosting_facility` varchar(64) DEFAULT NULL COMMENT 'DeviceProfile.trueIpHostingFacility',
  `browser_anomaly` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.browserAnomaly',
  `screen_res_anomaly` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.screenResAnomaly',
  `os_anomaly` varchar(16) DEFAULT NULL COMMENT 'DeviceProfile.osAnomaly',
  `dns_ip_assert_history` varchar(64) DEFAULT NULL COMMENT 'DeviceProfile.dnsIpAssertHistory',
  KEY `idx_interaction_id_jms_timestamp` (`interaction_id`,`jms_timestamp`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_exact_id_jms_timestamp` (`exact_id`,`jms_timestamp`),
  KEY `idx_smart_id_jms_timestamp` (`smart_id`,`jms_timestamp`),
  KEY `idx_input_ip_jms_timestamp` (`input_ip`,`jms_timestamp`),
  KEY `idx_true_ip_jms_timestamp` (`true_ip`,`jms_timestamp`),
  KEY `idx_user_session_id_jms_timestamp` (`user_session_id`,`jms_timestamp`),
  KEY `idx_agent_type` (`agent_type`),
  KEY `idx_realm_id` (`realm_id`),
  KEY `idx_jms_timestamp` (`jms_timestamp`),
  KEY `idx_dev_exact_runtime_cov` (`exact_id`,`jms_timestamp`,`interaction_id`,`agent_type`,`agent_os`,`browser_language`,`device_fingerprint_score`,`device_score`,`device_worst_score`,`input_ip`,`input_ip_score`,`proxy_ip`,`smart_id`,`true_ip`,`true_ip_score`),
  KEY `idx_dev_smart_runtime_cov` (`smart_id`,`jms_timestamp`,`interaction_id`,`agent_type`,`agent_os`,`request_result`,`business_transaction`,`device_fingerprint_score`,`device_score`,`device_worst_score`,`exact_id`,`input_ip`,`input_ip_score`,`proxy_ip`,`true_ip`,`true_ip_score`),
  KEY `idx_dev_input_runtime_cov` (`input_ip`,`jms_timestamp`,`interaction_id`,`agent_type`,`device_fingerprint_score`,`device_score`,`device_worst_score`,`exact_id`,`input_ip_score`,`smart_id`,`true_ip`,`true_ip_score`),
  KEY `idx_dev_true_runtime_cov` (`true_ip`,`jms_timestamp`,`interaction_id`,`agent_type`,`device_fingerprint_score`,`device_score`,`device_worst_score`,`exact_id`,`input_ip`,`input_ip_score`,`proxy_ip`,`smart_id`,`true_ip_score`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /*T! SHARD_ROW_ID_BITS=4 PRE_SPLIT_REGIONS=3 */
PARTITION BY RANGE COLUMNS(`jms_timestamp`)
(PARTITION `p20251101` VALUES LESS THAN ('2025-11-01 00:00:00'),
 PARTITION `p20251201` VALUES LESS THAN ('2025-12-01 00:00:00'),
 PARTITION `p20260101` VALUES LESS THAN ('2026-01-01 00:00:00'),
 PARTITION `p20260201` VALUES LESS THAN ('2026-02-01 00:00:00'),
 PARTITION `p20260301` VALUES LESS THAN ('2026-03-01 00:00:00'),
 PARTITION `p20260401` VALUES LESS THAN ('2026-04-01 00:00:00'),
 PARTITION `p20260501` VALUES LESS THAN ('2026-05-01 00:00:00'),
 PARTITION `p20260601` VALUES LESS THAN ('2026-06-01 00:00:00'),
 PARTITION `pmax` VALUES LESS THAN (MAXVALUE));

-- ------------------------------------------------------------
-- group_a_180d_daily_rollup
-- ------------------------------------------------------------
CREATE TABLE `group_a_180d_daily_rollup` (
  `bundle_id` varchar(64) NOT NULL,
  `event_day` date NOT NULL,
  `key1` varchar(128) NOT NULL,
  `key2` varchar(128) NOT NULL DEFAULT '',
  `metric_placeholder` bigint DEFAULT NULL,
  PRIMARY KEY (`bundle_id`,`key1`,`key2`,`event_day`) /*T![clustered_index] NONCLUSTERED */,
  KEY `idx_event_day` (`event_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /*T! SHARD_ROW_ID_BITS=4 PRE_SPLIT_REGIONS=3 */;

-- ------------------------------------------------------------
-- group_a_180d_daily_distinct
-- ------------------------------------------------------------
CREATE TABLE `group_a_180d_daily_distinct` (
  `bundle_id` varchar(64) NOT NULL,
  `template_id` varchar(64) NOT NULL,
  `event_day` date NOT NULL,
  `key1` varchar(128) NOT NULL,
  `key2` varchar(128) NOT NULL DEFAULT '',
  `distinct_value` varchar(256) NOT NULL,
  PRIMARY KEY (`bundle_id`,`template_id`,`key1`,`key2`,`event_day`,`distinct_value`) /*T![clustered_index] NONCLUSTERED */,
  KEY `idx_event_day` (`event_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /*T! SHARD_ROW_ID_BITS=4 PRE_SPLIT_REGIONS=3 */;

-- ------------------------------------------------------------
-- group_b_180d_daily_rollup
-- ------------------------------------------------------------
CREATE TABLE `group_b_180d_daily_rollup` (
  `bundle_id` varchar(64) NOT NULL,
  `event_day` date NOT NULL,
  `key1` varchar(128) NOT NULL,
  `key2` varchar(128) NOT NULL DEFAULT '',
  `present__b_0018` decimal(38,6) DEFAULT NULL,
  PRIMARY KEY (`bundle_id`,`key1`,`key2`,`event_day`) /*T![clustered_index] NONCLUSTERED */,
  KEY `idx_event_day` (`event_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /*T! SHARD_ROW_ID_BITS=4 PRE_SPLIT_REGIONS=3 */;

-- ------------------------------------------------------------
-- group_b_180d_daily_distinct
-- ------------------------------------------------------------
CREATE TABLE `group_b_180d_daily_distinct` (
  `bundle_id` varchar(64) NOT NULL,
  `template_id` varchar(64) NOT NULL,
  `event_day` date NOT NULL,
  `key1` varchar(128) NOT NULL,
  `key2` varchar(128) NOT NULL DEFAULT '',
  `distinct_value` varchar(256) NOT NULL,
  PRIMARY KEY (`bundle_id`,`template_id`,`key1`,`key2`,`event_day`,`distinct_value`) /*T![clustered_index] NONCLUSTERED */,
  KEY `idx_event_day` (`event_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /*T! SHARD_ROW_ID_BITS=4 PRE_SPLIT_REGIONS=3 */;

-- ------------------------------------------------------------
-- group_c_180d_daily_rollup
-- ------------------------------------------------------------
CREATE TABLE `group_c_180d_daily_rollup` (
  `bundle_id` varchar(64) NOT NULL,
  `p_event_day` date NOT NULL,
  `d_event_day` date NOT NULL,
  `key1` varchar(128) NOT NULL,
  `key2` varchar(128) NOT NULL DEFAULT '',
  `metric__c_0031` decimal(38,6) DEFAULT NULL,
  `metric__c_0032` decimal(38,6) DEFAULT NULL,
  `metric__c_0033` decimal(38,6) DEFAULT NULL,
  `metric__c_0034` decimal(38,6) DEFAULT NULL,
  `metric__c_0065` decimal(38,6) DEFAULT NULL,
  `metric__c_0066` decimal(38,6) DEFAULT NULL,
  `metric__c_0067` decimal(38,6) DEFAULT NULL,
  `metric__c_0068` decimal(38,6) DEFAULT NULL,
  PRIMARY KEY (`bundle_id`,`key1`,`key2`,`p_event_day`,`d_event_day`) /*T![clustered_index] NONCLUSTERED */,
  KEY `idx_event_day` (`p_event_day`,`d_event_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /*T! SHARD_ROW_ID_BITS=4 PRE_SPLIT_REGIONS=3 */;

-- ------------------------------------------------------------
-- group_c_180d_daily_distinct
-- ------------------------------------------------------------
CREATE TABLE `group_c_180d_daily_distinct` (
  `bundle_id` varchar(64) NOT NULL,
  `template_id` varchar(64) NOT NULL,
  `p_event_day` date NOT NULL,
  `d_event_day` date NOT NULL,
  `key1` varchar(128) NOT NULL,
  `key2` varchar(128) NOT NULL DEFAULT '',
  `distinct_value` varchar(256) NOT NULL,
  PRIMARY KEY (`bundle_id`,`template_id`,`key1`,`key2`,`p_event_day`,`d_event_day`,`distinct_value`) /*T![clustered_index] NONCLUSTERED */,
  KEY `idx_event_day` (`p_event_day`,`d_event_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /*T! SHARD_ROW_ID_BITS=4 PRE_SPLIT_REGIONS=3 */;

-- TiFlash replicas
-- ('intuit_risk', 'deviceprofile_fact', 1, 1, 1.0)
-- ('intuit_risk', 'pmt_txn_fact', 1, 1, 1.0)
