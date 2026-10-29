Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 52 test(s).
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, packing, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying packing.0001_initial... OK
  Applying sessions.0001_initial...test_box_rejects_bad_values (packing.tests.test_api.ModelValidationTests) ... ok
test_order_item_quantity_must_be_positive (packing.tests.test_api.ModelValidationTests) ... ok
test_product_rejects_non_positive_values (packing.tests.test_api.ModelValidationTests) ... ok
test_create_order_rejects_get (packing.tests.test_api.OrderTests) ... ok
test_create_order_stores_box_and_items (packing.tests.test_api.OrderTests) ... ok
test_duplicate_reference_is_409_and_creates_nothing (packing.tests.test_api.OrderTests) ... ok
test_get_missing_order_is_404 (packing.tests.test_api.OrderTests) ... ok
test_get_order (packing.tests.test_api.OrderTests) ... ok
test_order_with_no_fitting_box_needs_review (packing.tests.test_api.OrderTests) ... ok
test_reference_is_required_and_trimmed (packing.tests.test_api.OrderTests) ... ok
test_unknown_sku_creates_no_order (packing.tests.test_api.OrderTests) ... ok
test_does_not_write_to_the_database (packing.tests.test_api.RecommendBoxTests) ... ok
test_inactive_box_is_ignored (packing.tests.test_api.RecommendBoxTests) ... ok
test_invalid_payloads_are_rejected (packing.tests.test_api.RecommendBoxTests) ... ok
test_item_too_big_for_small_goes_to_medium (packing.tests.test_api.RecommendBoxTests) ... ok
test_malformed_json (packing.tests.test_api.RecommendBoxTests) ... ok
test_missing_items_key (packing.tests.test_api.RecommendBoxTests) ... ok
test_no_box_fits_returns_null_and_message (packing.tests.test_api.RecommendBoxTests) ... ok
test_only_post_allowed (packing.tests.test_api.RecommendBoxTests) ... ok
test_picks_cheapest_box_that_fits (packing.tests.test_api.RecommendBoxTests) ... ok
test_quantity_defaults_to_one (packing.tests.test_api.RecommendBoxTests) ... ok
test_repeated_skus_are_merged (packing.tests.test_api.RecommendBoxTests) ... ok
test_response_contains_placements_and_utilization (packing.tests.test_api.RecommendBoxTests) ... ok
test_too_many_units_is_a_clean_400 (packing.tests.test_api.RecommendBoxTests) ... ok
test_unknown_sku (packing.tests.test_api.RecommendBoxTests) ... ok
test_weight_pushes_order_to_a_stronger_box (packing.tests.test_api.RecommendBoxTests) ... ok
test_seed_is_idempotent_and_usable (packing.tests.test_api.SeedCommandTests) ... ok
test_bad_quantities_rejected (packing.tests.test_algorithm.InputValidationTests) ... ok
test_empty_order_rejected (packing.tests.test_algorithm.InputValidationTests) ... ok
test_exactly_max_units_is_allowed (packing.tests.test_algorithm.InputValidationTests) ... ok
test_invalid_box_rejected (packing.tests.test_algorithm.InputValidationTests) ... ok
test_invalid_item_dimensions_rejected (packing.tests.test_algorithm.InputValidationTests) ... ok
test_quantity_expands_units_and_weight (packing.tests.test_algorithm.InputValidationTests) ... ok
test_too_many_units_rejected_before_expansion (packing.tests.test_algorithm.InputValidationTests) ... ok
test_eight_cubes_fill_a_cube (packing.tests.test_algorithm.PackingTests) ... ok
test_eight_slabs_fill_box_exactly (packing.tests.test_algorithm.PackingTests) ... ok
test_mixed_items_have_valid_placements (packing.tests.test_algorithm.PackingTests) ... ok
test_placements_are_deterministic (packing.tests.test_algorithm.PackingTests) ... ok
test_two_items_fill_box_exactly (packing.tests.test_algorithm.PackingTests) ... ok
test_validator_catches_overlap_and_overflow (packing.tests.test_algorithm.PackingTests) ... ok
test_enough_volume_but_no_arrangement (packing.tests.test_algorithm.RejectionReasonTests) ... ok
test_item_too_large_in_every_rotation (packing.tests.test_algorithm.RejectionReasonTests) ... ok
test_rotation_lets_long_item_fit (packing.tests.test_algorithm.RejectionReasonTests) ... ok
test_volume_exceeded (packing.tests.test_algorithm.RejectionReasonTests) ... ok
test_weight_exactly_at_limit_is_allowed (packing.tests.test_algorithm.RejectionReasonTests) ... ok
test_weight_is_summed_across_quantity (packing.tests.test_algorithm.RejectionReasonTests) ... ok
test_weight_limit_excludes_box (packing.tests.test_algorithm.RejectionReasonTests) ... ok
test_cheapest_fitting_box_wins_even_if_bigger (packing.tests.test_algorithm.SelectionTests) ... ok
test_cost_tie_prefers_smaller_volume (packing.tests.test_algorithm.SelectionTests) ... ok
test_full_tie_falls_back_to_name (packing.tests.test_algorithm.SelectionTests) ... ok
test_no_box_fits_returns_none_but_reports_every_box (packing.tests.test_algorithm.SelectionTests) ... ok
test_no_boxes_at_all (packing.tests.test_algorithm.SelectionTests) ... ok

----------------------------------------------------------------------
Ran 52 tests in 0.328s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
 OK
System check identified no issues (0 silenced).
