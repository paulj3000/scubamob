-- Drops the tables owned by the retired scuba.sitesettings app
-- (MODERNIZATION_ROADMAP.md, "Retire scuba.sitesettings", item 15).
--
-- scuba.sitesettings never had Django migrations (like most apps in this
-- project), so there is no `migrate` reversal path for these tables --
-- they must be dropped manually against any environment that has them
-- (any deployed SQLite or MySQL database populated via `migrate --run-syncdb`
-- before the app was removed from INSTALLED_APPS).
--
-- Not included here, because the models moved to other apps rather than
-- being dropped:
--   flag_option              -> now scuba.accounts.FlagOption (item 2)
--   sns_subscription_requests -> now scuba.aws.SNSSubscriptionRequest (item 10)
--
-- Child tables (FK to system_api) are dropped before their parent.
DROP TABLE IF EXISTS endpoint_param;
DROP TABLE IF EXISTS endpoint;
DROP TABLE IF EXISTS system_api;
DROP TABLE IF EXISTS system_setting;
DROP TABLE IF EXISTS alerting_api;
DROP TABLE IF EXISTS aws_api;
DROP TABLE IF EXISTS billing_api;
DROP TABLE IF EXISTS chat_api;
DROP TABLE IF EXISTS settings_api;
DROP TABLE IF EXISTS api_key;
