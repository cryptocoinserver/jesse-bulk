import click
import jesse.helpers as jh
import pkg_resources
import yaml
from jesse.research import get_candles
import shutil
import pathlib

from .picker import filter_and_sort_dna_df


# create a Click group
@click.group()
@click.version_option(pkg_resources.get_distribution("jesse-bulk").version)
def cli() -> None:
    pass

@cli.command()
def create_config() -> None:
    dirname = pathlib.Path().resolve()
    shutil.copy2('bulk_config.yml', f'{dirname}/bulk_config.yml')

@cli.command()
@click.argument('strategy_name', required=True, type=str)
@click.argument('csv_path', required=True, type=str)
def run(strategy_name: str, csv_path: str) -> None:

    try:
        with open("bulk_config.yml", "r") as ymlfile:
            cfg = yaml.load(ymlfile)
    except IOError:
        print("bulk_config not found. Run create-config command.")

    dna_df = filter_and_sort_dna_df(csv_path, cfg)

    StrategyClass = jh.get_strategy_class(strategy_name)
    hp_dict = StrategyClass.hyperparameters()

    config = {
        'starting_balance': cfg['backtest-data']['starting_balance'],
        'fee': cfg['backtest-data']['fee'],
        'futures_leverage': cfg['backtest-data']['futures_leverage'],
        'futures_leverage_mode': cfg['backtest-data']['futures_leverage_mode'],
        'exchange': cfg['backtest-data']['exchange'],
        'settlement_currency': cfg['backtest-data']['settlement_currency'],
        'warm_up_candles': cfg['backtest-data']['warm_up_candles']
    }

    for symbol in cfg['backtest-data']['symbols']:
        for timeframe in cfg['backtest-data']['timeframes']:
            for timespan in cfg['backtest-data']['timespans']:
                candles = {}
                extra_routes = []
                for extra_route in cfg['backtest-data']['extra_routes']:
                    candles[jh.key(extra_route['exchange'], extra_route['symbol'])] = {
                            'exchange': extra_route['exchange'],
                            'symbol': extra_route['symbol'],
                            'candles': get_candles(
                                extra_route['exchange'],
                                extra_route['symbol'],
                                extra_route['timeframe'],
                                timespan[0],
                                timespan[1],
                            ),
                        }
                    extra_routes.append({'exchange': extra_route['exchange'], 'symbol': extra_route['symbol'], 'timeframe':  extra_route['timeframe']})

                candles[jh.key(cfg['backtest-data']['exchange'], symbol)] = {
                        'exchange': cfg['backtest-data']['exchange'],
                        'symbol': symbol,
                        'candles': get_candles(
                            cfg['backtest-data']['exchange'],
                            symbol,
                            timeframe,
                            timespan[0],
                            timespan[1],
                        ),
                    }

                route = [{'exchange': cfg['backtest-data']['exchange'], 'strategy': strategy_name, 'symbol': symbol,
                          'timeframe': timeframe}]

                for index, row in dna_df['dna'].iterrows():
                    backtest_data = backtest(config, route, extra_routes, candles, jh.dna_to_hp(hp_dict, row['dna']))
