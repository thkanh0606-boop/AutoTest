# AutoTest Contract

This contract defines shared data structures for Test Case, Test Suite, Runner, History, and Report integrations.

## Status

All modules must use one of these statuses:

- `PENDING`
- `RUNNING`
- `PASSED`
- `FAILED`
- `ERROR`
- `SKIPPED`

## TestCase

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `case_id` | string | yes | Stable unique ID, for example `DASH-001`. |
| `module` | string | yes | Functional module, for example `dashboard`, `label`, `table`. |
| `name` | string | yes | Human-readable test name. |
| `steps` | string | yes | Ordered execution steps. |
| `expected_result` | string | yes | Expected result displayed in reports. |
| `page_key` | string | no | Page under test, for example `plt_dashboard`. |
| `page_name` | string | no | Human-readable page name. |
| `element_key` | string | no | Stable element key. |
| `locator_type` | string | no | `css`, `xpath`, `id`, `name`, `class`, `tag`, or `service`. |
| `locator_value` | string | no | Locator expression or service object name. |
| `action_type` | string | no | Assertion/action mode such as `text_equals`, `contains_all_has_number`, `click_url_contains`, or `deep_link_url_contains`. |
| `target_path` | string | no | Expected navigation path for click/deep-link cases. |

## TestRun

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `run_id` | string | yes | Unique ID for every run. Never reuse for a new execution. |
| `module` | string | yes | Module being executed. |
| `status` | enum | yes | Starts as `RUNNING`; ends as `PASSED`, `FAILED`, or `ERROR`. |
| `total` | integer | yes | Number of test cases scheduled. |
| `passed` | integer | yes | Count of passed tests. |
| `failed` | integer | yes | Count of failed assertions. |
| `error` | integer | yes | Count of execution errors. |
| `skipped` | integer | yes | Count of skipped tests. |
| `started_at` | ISO datetime | yes | Start time. |
| `finished_at` | ISO datetime | no | Finish time. |
| `message` | string | no | Runner summary or blocking error. |

## TestResult

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `run_id` | string | yes | References `TestRun.run_id`. |
| `case_id` | string | yes | References `TestCase.case_id`. |
| `module` | string | yes | Module being tested. |
| `name` | string | yes | Test case name. |
| `steps` | string | yes | Steps used for this execution. |
| `expected_result` | string | yes | Expected result. |
| `actual_result` | string | yes | Actual result collected by Selenium. |
| `status` | enum | yes | `PASSED`, `FAILED`, `ERROR`, or `SKIPPED`. |
| `error_message` | string | no | Assertion or runtime error. |
| `screenshot_path` | string | no | Screenshot path when failed or errored. |
| `created_at` | ISO datetime | yes | Persist time. |

## ModuleNavigation

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `module` | string | yes | Module key, for example `dashboard`, `bookings`, `cars`, `finance`. |
| `entry_point` | string | yes | `sidebar`, `quick_menu`, or `deep_link`. |
| `target_path` | string | yes | Expected path after navigation. |
| `locator_type` | string | no | Locator strategy for click-based navigation. |
| `locator_value` | string | no | Locator expression for click-based navigation. |
| `expected_result` | string | yes | URL or page assertion after navigation. |

## SQLite Persistence

The local SQLite database is `autotest.sqlite3`.

- `test_cases` stores unique test cases by `case_id`; updates are upserts and must not duplicate a case.
- `test_runs` stores one row per execution with a unique `run_id`.
- `test_results` stores immutable execution results. History must not be overwritten.
- All writes must use parameterized queries.
- Migrations are additive and must not delete existing user data.
