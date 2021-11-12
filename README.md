# Jesse bulk backtest

Loads a CSV you got from Jesse's optimization. Removes duplicates and filteres it according to your config.

Then runs all backtests according to your configuration with the DNAs and creates a CSV containing all metrics of the backtests.

Only works with the dashboard version / branch of jesse.

Currently no progress bar is shown during backtesting. Just trust the process.

You will find the results in a csv in your project folder. 

Uses multiprocessing. Uses pickle cache for candles. You might want to clear `storage/bulk` if you use it a lot and run out of space.

# Installation

```sh
# install from git
pip install git+https://github.com/cryptocoinserver/jesse-bulk.git

# cd in your Jesse project directory

# create config file
jesse-bulk create-config

# edit the create yml file in your project directory 
jesse-bulk run StrategyName Optimization.csv

```


## Disclaimer
This software is for educational purposes only. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS. Do not risk money which you are afraid to lose. There might be bugs in the code - this software DOES NOT come with ANY warranty.
