# Testing Report — Unit, Integration & API Tests

## Test Suite Summary
| Category | Tests | Status |
|----------|-------|--------|
| Preprocessing | 8 | ✅ All passed |
| Drift Monitoring | 4 | ✅ All passed |
| Model Validation Gate | 2 | ✅ All passed |
| API Validation | 4 | ✅ All passed |
| **Total** | **17** | **✅ All passed** |

## Test Details

### Preprocessing Tests
| Test | Purpose |
|------|---------|
| test_merge_returns_dataframe | Verify merged output is DataFrame |
| test_all_cities_present | All 5 cities in merged data |
| test_date_parsed | Date column parsed correctly |
| test_no_missing_aqi_after_clean | No null AQI after cleaning |
| test_lag_features_exist | Lag features created |
| test_no_same_day_leakage | No same-day pollutant leakage |
| test_lag_values_are_previous_day | Lag values match previous day |
| test_calendar_features_range | Calendar features in valid ranges |

### Drift Monitoring Tests
| Test | Purpose |
|------|---------|
| test_psi_identical_distributions | PSI ~0 for identical data |
| test_psi_very_different_distributions | PSI > 0.2 for shifted data |
| test_psi_non_negative | PSI always >= 0 |

### Model Validation Gate
| Test | Threshold | Result |
|------|-----------|--------|
| R² >= 0.85 | 0.85 | ✅ 0.9196 |
| MAE <= 20 | 20 | ✅ 14.68 |

### API Tests
| Test | Purpose |
|------|---------|
| aqi_category boundaries | Good, Satisfactory, Moderate, Poor, Very Poor, Severe |

## Run Tests
```bash
pytest src/test_pipeline.py -v --tb=short
```
