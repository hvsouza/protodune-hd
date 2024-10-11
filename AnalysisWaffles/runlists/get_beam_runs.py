import polars as pl
import numpy as np


runsled = 0

def findrun(value:int):
    global runsled
    for ref in runsled:
        if ref < value <= ref+5:
            return ref
    return pl.Null
    
    
    
df = pl.read_csv('./beam_run_list.csv')

df = df.filter(
    ~pl.col('Run').is_null()
)

dfcosmics = df.filter(
    pl.col('type') == "COSMIC" # not good, because many do not have cosmics
).sort('Run')


dfcosmics = dfcosmics.with_columns(
    pl.lit(180).alias('Efield'),
    pl.lit(26261).alias('Run LED'),
)

dfcosmics:pl.DataFrame = dfcosmics.with_columns(
    # Run = pl.col('Run').cast(pl.Int16),
    pl.col('Time Start').str.replace_all('\.','/').str.split_exact(" ", 1).alias('Date')
).unnest('Date').with_columns(
    pl.col("field_0").alias("Date"),
    pl.col("field_1").alias("Time Start"),
).select(['Run', 'Date', 'Time Start','Efield', 'Run LED'])

with pl.Config(tbl_rows=35):
    print(dfcosmics)

dfcosmics.write_csv("beam_runs.csv")




