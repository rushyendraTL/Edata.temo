import pandas as pd
import polars as pl
from datetime import date, datetime
import json

# vv = dd.read_csv('data/VV_Q1_2025.csv',
#                  dtype={'Colour': 'object',
#                         'VehicleCondition': 'object'})

# all_makes = vv['Make'].unique().compute()
# all_models = vv['Model'].unique().compute()
# start_date = vv['InquiryDate'].min().compute()
# end_date = vv['InquiryDate'].max().compute()

# print(len(all_makes))
# print(len(all_models))
# print(start_date)
# print(end_date)

# pd version
make_country_map = json.load(open('data/make_countries.json'))

vv = pl.scan_parquet('data/VV_Q1_2025_processed.parquet')
vs = pl.scan_parquet('data/VS_Q1_2025_processed.parquet')
cmf = pl.scan_parquet('data/Claims.parquet')

vs = vs.filter(
    pl.col('Region') != 'IMPORTED/GCC'
)

# print(vv.columns)

all_make_q = vs.select(
    unique_makes=pl.col('Make').cast(pl.Categorical).unique()
)
all_makes = all_make_q.collect()['unique_makes'].to_list()

all_models_q = vs.select(
    unique_models=pl.col('Model').cast(pl.Categorical).unique()
)
all_models = all_models_q.collect()['unique_models'].to_list()

all_countries = []
country_iso = json.load(open('data/country_iso.json'))
with open('data/countries.txt', 'r') as f:
    for line in f:
        all_countries.append(line.strip())

# Combine make/model pairs from both dataframes
make_models_q = vs.filter(
    pl.col('Make').is_not_null(),
    pl.col('Model').is_not_null(),
    pl.col('Make') != '',
    pl.col('Model') != ''
).select(
    pl.col('Make').cast(pl.Categorical),
    pl.col('Model').cast(pl.Categorical)
).group_by(
    pl.col('Make'),
).agg(
    pl.col('Model').cast(pl.Categorical).unique()
)

make_models = make_models_q.collect()
makes = make_models['Make'].to_list()
models = make_models['Model'].to_list()
make_models = {
    make: models for make, models in zip(makes, models)
}

# make_models_combined = pd.concat([
#     vv[['Make', 'Model']].drop_duplicates(),
#     vs[['Make', 'Model']].drop_duplicates()
# ]).drop_duplicates()
# make_models = make_models_combined.groupby(
#     'Make')['Model'].apply(list).to_dict()

# print(make_models)

# Convert dates for both dataframes
vv_min_data = vv.select(
    pl.col('InquiryDate').str.to_datetime('%Y-%m-%d %H:%M:%S').min()
).collect()['InquiryDate'].to_list()[0]
vv_max_data = vv.select(
    pl.col('InquiryDate').str.to_datetime('%Y-%m-%d %H:%M:%S').max()
).collect()['InquiryDate'].to_list()[0]

vs_min_data = vs.select(
    pl.col('InquiryDate').str.to_datetime('%Y-%m-%d %H:%M:%S').min()
).collect()['InquiryDate'].to_list()[0]
vs_max_data = vs.select(
    pl.col('InquiryDate').str.to_datetime('%Y-%m-%d %H:%M:%S').max()
).collect()['InquiryDate'].to_list()[0]

# Get min/max dates across both dataframes
start_date = min(vv_min_data, vs_min_data)
end_date = max(vv_max_data, vs_max_data)

print(start_date)
print(end_date)

year_ranges_enum = pl.Enum(['1900 to 2000', '2000 to 2010',
                           '2010 to 2015', '2015 to 2020', '2020 to 2024', '2025 to Present'])
price_ranges_enum = pl.Enum(
    ['<50K', '50K to 100K', '100K to 250K', '250K to 500K', '500K to 1M', '>1M'])
