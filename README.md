# Jesse bulk backtest

`jesse-bulk pick`
Loads a CSV you got from Jesse's optimization. Removes duplicates and filteres it according to your config.

`jesse-bulk refine`
Runs all backtests according to your configuration (symbols, timeframes, start & finish-dates) with the DNAs from the CSV and creates a CSV containing all metrics of the backtests.

`jesse-bulk bulk`
Runs all backtests according to your configuration (symbols, timeframes, start & finish-dates) and creates a CSV containing all metrics of the backtests.

Only works with the dashboard version / branch of jesse.

You will find the results in a csv in your project folder. 

Uses joblib for multiprocessing. Uses pickle cache for candles. You might want to clear `storage/bulk` if you use it a lot and run out of space.

The bulk_config.yml should be self-explainatory.

## Warning
- warm-up-candles are taken from the candles passed. So the actual start_date is different then it would be during a normal backtest.
- extra route candles are added to all backtests - even though they might not be needed by the symbol. 

This could be improved.


# Installation

```sh
# install from git
pip install git+https://github.com/cryptocoinserver/jesse-bulk.git

# cd in your Jesse project directory

# create the config file
jesse-bulk create-config

# edit the created yml file in your project directory 

# pick / filter optimization csv
jesse-bulk pick Optimization.csv

# refine bulk backtests with DNAs
jesse-bulk refine StrategyName Optimization.csv

# bulk backtests
jesse-bulk bulk StrategyName 

```


## Disclaimer
This software is for educational purposes only. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS. Do not risk money which you are afraid to lose. There might be bugs in the code - this software DOES NOT come with ANY warranty.
