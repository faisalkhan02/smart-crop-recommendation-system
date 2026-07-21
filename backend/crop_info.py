"""
crop_info.py

Static lookup data for crop advisory info:
- growing season
- water requirement
- suitable soil type
- harvest duration
- fertilizer suggestion

This is rule-based / lookup-based, not ML-based. No model is needed here
since this is fixed domain knowledge per crop - only the crop selection
itself (in main.py's /predict) is uncertain enough to require ML.

Note: values here are illustrative/general estimates. For the final
report, a couple of these should be verified against an actual
agriculture extension source (e.g. ICAR / state agriculture department
advisories) for accuracy and proper citation.
"""

# dictionary mapping each crop name to its advisory details
CROP_INFO = {
    "rice":        dict(season="Kharif (Jun-Nov)", water="High", soil="Clayey / Loamy", harvest_days="120-150", fertilizer="Urea + DAP + Potash (balanced N-P-K, split N application)"),
    "maize":       dict(season="Kharif/Rabi", water="Medium", soil="Well-drained Loamy", harvest_days="90-120", fertilizer="Urea-heavy (high N demand) + moderate P/K"),
    "chickpea":    dict(season="Rabi (Oct-Mar)", water="Low", soil="Sandy Loam", harvest_days="90-120", fertilizer="Low N (legume fixes own N), Phosphorus-rich (DAP)"),
    "kidneybeans": dict(season="Rabi/Kharif", water="Medium", soil="Well-drained Loamy", harvest_days="90-110", fertilizer="Low N, Phosphorus + Potash"),
    "pigeonpeas":  dict(season="Kharif (Jun-Dec)", water="Low-Medium", soil="Well-drained Loamy", harvest_days="150-180", fertilizer="Low N (legume), Phosphorus-rich"),
    "mothbeans":   dict(season="Kharif (Jun-Sep)", water="Low", soil="Sandy", harvest_days="60-90", fertilizer="Minimal N, light Phosphorus"),
    "mungbean":    dict(season="Kharif/Summer", water="Low-Medium", soil="Sandy Loam", harvest_days="60-90", fertilizer="Low N, Phosphorus + Potash"),
    "blackgram":   dict(season="Kharif/Rabi", water="Low-Medium", soil="Clayey Loam", harvest_days="70-90", fertilizer="Low N, Phosphorus-rich"),
    "lentil":      dict(season="Rabi (Oct-Mar)", water="Low", soil="Sandy Loam", harvest_days="100-130", fertilizer="Low N, Phosphorus + Sulphur"),
    "pomegranate": dict(season="Year-round (best: winter planting)", water="Low-Medium", soil="Well-drained Loamy", harvest_days="150-180 (per fruiting cycle)", fertilizer="Balanced N-P-K, extra Potash during fruiting"),
    "banana":      dict(season="Year-round", water="High", soil="Rich Loamy", harvest_days="270-365", fertilizer="High N + Potash, moderate Phosphorus"),
    "mango":       dict(season="Flowering: winter, Harvest: summer", water="Low-Medium", soil="Well-drained Alluvial/Laterite", harvest_days="100-150 (post flowering)", fertilizer="Balanced N-P-K, Potash during fruit development"),
    "grapes":      dict(season="Pruning: Oct, Harvest: Feb-Apr", water="Medium", soil="Well-drained Sandy Loam", harvest_days="150-180", fertilizer="High Phosphorus + Potash, moderate N"),
    "watermelon":  dict(season="Summer (Feb-May)", water="Medium-High", soil="Sandy Loam", harvest_days="80-110", fertilizer="High N (early), Potash (fruiting stage)"),
    "muskmelon":   dict(season="Summer (Feb-May)", water="Medium-High", soil="Sandy Loam", harvest_days="65-90", fertilizer="High N (early), Potash (fruiting stage)"),
    "apple":       dict(season="Flowering: spring, Harvest: autumn", water="Medium", soil="Well-drained Loamy (cool climate)", harvest_days="150-180 (post flowering)", fertilizer="High Phosphorus + Potash for fruiting"),
    "orange":      dict(season="Flowering: spring, Harvest: winter", water="Medium", soil="Well-drained Sandy Loam", harvest_days="240-300", fertilizer="Balanced N-P-K, split application"),
    "papaya":      dict(season="Year-round", water="Medium-High", soil="Well-drained Loamy", harvest_days="180-270", fertilizer="High N + Potash, moderate Phosphorus"),
    "coconut":     dict(season="Year-round", water="High", soil="Sandy Coastal / Loamy", harvest_days="365+ (perennial)", fertilizer="High Potash, moderate N + Phosphorus"),
    "cotton":      dict(season="Kharif (Apr-Oct)", water="Medium", soil="Black Cotton Soil (Regur)", harvest_days="150-180", fertilizer="High N, moderate Phosphorus + Potash"),
    "jute":        dict(season="Kharif (Mar-Jul)", water="High", soil="Alluvial (river basin)", harvest_days="100-120", fertilizer="High N, moderate Phosphorus + Potash"),
    "coffee":      dict(season="Flowering: spring, Harvest: winter", water="Medium-High", soil="Well-drained Loamy (hill/shade)", harvest_days="270-300", fertilizer="Balanced N-P-K, organic matter recommended"),
}


def get_crop_info(crop_name: str):
    # normalizing input - lowercase and no extra spaces, so lookups
    # work regardless of how the crop name was typed/passed in
    crop_name = crop_name.strip().lower()

    # returns None if the crop isn't in the dictionary, instead of raising an error -
    # lets the calling code (main.py) decide how to handle a missing crop
    return CROP_INFO.get(crop_name, None)