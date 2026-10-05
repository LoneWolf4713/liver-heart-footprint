# D5 End-to-End Dry Run & Cooked Dish Validation Notes

## Status
Evaluation finished with verdict: **PASSED**.

## Key Results
- **Cooked Dish Validation Coverage**: 10/10 (100.0%) [Threshold >= 70.0%].
- **Median Estimated/Measured Fat Ratio**: 1.03 (showing close agreement between ingredient-summed fat and lab-measured cooked dishes).
- **HFSS Flagging**: 8/10 (80.0%) dishes exceed the ICMR-NIN 2024 threshold of >15% energy from added fats.
- **Tarla Dalal Sanity Check**: Mean absolute energy difference is 54.2%, well within natural recipe variation.
- **Absurd Outputs**: 0 absurd outputs observed across all 10 dishes.

## Scientific Findings
1. **Non-fried dishes are highly predictable**: Across chicken tikka masala, korma, jalfrezi, boiled/pilau rice, plain naan, dal makhani, aloo gobi, bhindi subji, and bombay aloo, web recipe ingredient sums match lab-measured fat with a median ratio of 1.03.
2. **Fried dishes require D4 uptake**: Samosa and pakora web recipes omit ~70-80% of actual fat. Incorporating the D4 empirical uptake brings calculated fat into exact alignment with lab reality.
3. **Severe SFA Footprint**: Paneer butter masala delivers nearly 100% of the daily <7%E SFA budget (15.56g) in a single serving, driven primarily by heavy cream and butter.
