import polars as pl
import numpy as np


runsled = 0

def findrun(value:int):
    global runsled
    for ref in runsled:
        if ref < value <= ref+5:
            return ref
    return pl.Null
    
    
    
df = pl.read_csv('./run_list.csv')

df = df.filter(
    ~pl.col('Run').is_null()
)

dfcosmics = df.filter(
    pl.col('type') == "COSMIC" # not good, because many do not have cosmics
).sort('Run')

dfled = df.filter(
    pl.col('type') == "LEDG" # not good, because many do not have cosmics
).sort('Run')
runsled = dfled['Run'].to_numpy()

dfcosmics = dfcosmics.with_columns(
    pl.col('Configuration').str.extract_groups(r"([0-9][0-9]?[0-9]?) ?kV").struct["1"].cast(pl.Float64).alias('ef')
)
dfcosmics = dfcosmics.with_row_index()
dfcosmics:pl.DataFrame = dfcosmics.with_columns(
    ef = pl.when(pl.col('index')==0).then(0).otherwise(
        pl.col('ef')
    )
).with_columns(
    Efield = pl.col('ef').forward_fill(),
    Run = pl.col('Run').cast(pl.Int16),
).with_columns(
    pl.col('Start time').fill_null("??:??")
).with_columns(
    pl.col('Run').map_elements(findrun, return_dtype=pl.Int64).alias("Run LED")
).with_columns(
    pl.col('Run LED').forward_fill()
).select(['Run','Date','Start time','Efield', 'Run LED'])

with pl.Config(tbl_rows=35):
    print(dfcosmics)
    print(dfled)

dfcosmics.write_csv("cosmic_runs.csv")




