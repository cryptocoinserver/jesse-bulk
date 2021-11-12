import os
import pathlib
import pickle
import shutil
from multiprocessing import Pool

import click
import numpy as np
import pandas as pd
import pkg_resources
import yaml
import datetime

# create a Click group
@click.group()
@click.version_option(pkg_resources.get_distribution("jesse-bulk").version)
def cli() -> None:
    pass


@cli.command()
def create_config() -> None:
    validate_cwd()
    target_dirname = pathlib.Path().resolve()
    package_dir = pathlib.Path(__file__).resolve().parent
    shutil.copy2(f'{package_dir}/bulk_config.yml', f'{target_dirname}/bulk_config.yml')


@cli.command()
@click.argument('csv_path', required=True, type=str)
def pick(csv_path: str) -> None:
    from .picker import filter_and_sort_dna_df

    cfg = get_config()

    dna_df = filter_and_sort_dna_df(csv_path, cfg)


@cli.command()
@click.argument('strategy_name', required=True, type=str)
@click.argument('csv_path', required=True, type=str)
def refine(strategy_name: str, csv_path: str) -> None:
    validate_cwd()

    import jesse.helpers as jh

    cfg = get_config()

    StrategyClass = jh.get_strategy_class(strategy_name)
    hp_dict = StrategyClass().hyperparameters()

    config = {
        'starting_balance': cfg['backtest-data']['starting_balance'],
        'fee': cfg['backtest-data']['fee'],
        'futures_leverage': cfg['backtest-data']['futures_leverage'],
        'futures_leverage_mode': cfg['backtest-data']['futures_leverage_mode'],
        'exchange': cfg['backtest-data']['exchange'],
        'settlement_currency': cfg['backtest-data']['settlement_currency'],
        'warm_up_candles': cfg['backtest-data']['warm_up_candles']
    }

    mp_args = []
    for symbol in cfg['backtest-data']['symbols']:
        for timeframe in cfg['backtest-data']['timeframes']:
            for timespan in cfg['backtest-data']['timespans'].items():
                timespan = timespan[1]
                candles = {}
                extra_routes = []

                for extra_route in cfg['backtest-data']['extra_routes'].items():
                    extra_route = extra_route[1]
                    candles[jh.key(extra_route['exchange'], extra_route['symbol'])] = {
                        'exchange': extra_route['exchange'],
                        'symbol': extra_route['symbol'],
                        'candles': get_candles_with_cache(
                            extra_route['exchange'],
                            extra_route['symbol'],
                            extra_route['timeframe'],
                            timespan['start_date'],
                            timespan['finish_date'],
                        ),
                    }
                    extra_routes.append({'exchange': extra_route['exchange'], 'symbol': extra_route['symbol'],
                                         'timeframe': extra_route['timeframe']})
                candles[jh.key(cfg['backtest-data']['exchange'], symbol)] = {
                    'exchange': cfg['backtest-data']['exchange'],
                    'symbol': symbol,
                    'candles': get_candles_with_cache(
                        cfg['backtest-data']['exchange'],
                        symbol,
                        timeframe,
                        timespan['start_date'],
                        timespan['finish_date'],
                    ),
                }

                route = [{'exchange': cfg['backtest-data']['exchange'], 'strategy': strategy_name, 'symbol': symbol,
                          'timeframe': timeframe}]

                key = f'{symbol}-{timeframe}-{timespan["start_date"]}-{timespan["finish_date"]}'

                for dna in dna_df['dna']:
                    mp_args.append((key, config, route, extra_routes, candles, hp_dict, dna))

    with Pool() as pool:
        print('Starting bulk refine.')
        results = pool.starmap(backtest_with_info_key, mp_args)
        print('Done.')

    old_name = pathlib.Path(csv_path).stem
    new_path = pathlib.Path(csv_path).with_stem(f'{old_name}-results')

    results_df = pd.DataFrame.from_dict(results, orient='columns')

    results_df.to_csv(new_path, header=True, index=False, encoding='utf-8', sep='\t')


@cli.command()
@click.argument('strategy_name', required=True, type=str)
@click.argument('csv_path', required=True, type=str)
def bulk(strategy_name: str) -> None:
    validate_cwd()

    cfg = get_config()

    config = {
        'starting_balance': cfg['backtest-data']['starting_balance'],
        'fee': cfg['backtest-data']['fee'],
        'futures_leverage': cfg['backtest-data']['futures_leverage'],
        'futures_leverage_mode': cfg['backtest-data']['futures_leverage_mode'],
        'exchange': cfg['backtest-data']['exchange'],
        'settlement_currency': cfg['backtest-data']['settlement_currency'],
        'warm_up_candles': cfg['backtest-data']['warm_up_candles']
    }

    mp_args = []
    for symbol in cfg['backtest-data']['symbols']:
        for timeframe in cfg['backtest-data']['timeframes']:
            for timespan in cfg['backtest-data']['timespans'].items():
                timespan = timespan[1]
                candles = {}
                extra_routes = []

                for extra_route in cfg['backtest-data']['extra_routes'].items():
                    extra_route = extra_route[1]
                    candles[jh.key(extra_route['exchange'], extra_route['symbol'])] = {
                        'exchange': extra_route['exchange'],
                        'symbol': extra_route['symbol'],
                        'candles': get_candles_with_cache(
                            extra_route['exchange'],
                            extra_route['symbol'],
                            extra_route['timeframe'],
                            timespan['start_date'],
                            timespan['finish_date'],
                        ),
                    }
                    extra_routes.append({'exchange': extra_route['exchange'], 'symbol': extra_route['symbol'],
                                         'timeframe': extra_route['timeframe']})
                candles[jh.key(cfg['backtest-data']['exchange'], symbol)] = {
                    'exchange': cfg['backtest-data']['exchange'],
                    'symbol': symbol,
                    'candles': get_candles_with_cache(
                        cfg['backtest-data']['exchange'],
                        symbol,
                        timeframe,
                        timespan['start_date'],
                        timespan['finish_date'],
                    ),
                }

                route = [{'exchange': cfg['backtest-data']['exchange'], 'strategy': strategy_name, 'symbol': symbol,
                          'timeframe': timeframe}]

                key = f'{symbol}-{timeframe}-{timespan["start_date"]}-{timespan["finish_date"]}'

                mp_args.append((key, config, route, extra_routes, candles, None, None))

    with Pool() as pool:
        print('Starting bulk backtest.')
        results = pool.starmap(backtest_with_info_key, mp_args)
        print('Done.')

    results_df = pd.DataFrame.from_dict(results, orient='columns')

    dt = datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")

    results_df.to_csv(f'bulk_{dt}.csv', header=True, index=False, encoding='utf-8', sep='\t')


def validate_cwd() -> None:
    """
    make sure we're in a Jesse project
    """
    ls = os.listdir('.')
    is_jesse_project = 'strategies' in ls and 'storage' in ls

    if not is_jesse_project:
        print('Current directory is not a Jesse project. You must run commands from the root of a Jesse project.')
        exit()


def get_candles_with_cache(exchange: str, symbol: str, timeframe: str, start_date: str, finish_date: str) -> np.ndarray:
    path = pathlib.Path('storage/bulk')
    path.mkdir(parents=True, exist_ok=True)

    from jesse.research import get_candles

    cache_file_name = f"{exchange}-{symbol}-{timeframe}-{start_date}-{finish_date}.pickle"
    cache_file = pathlib.Path(f'storage/bulk/{cache_file_name}')

    if cache_file.is_file():
        with open(f'storage/bulk/{cache_file_name}', 'rb') as handle:
            candles = pickle.load(handle)
    else:
        candles = get_candles(exchange, symbol, timeframe, start_date, finish_date)
        with open(f'storage/bulk/{cache_file_name}', 'wb') as handle:
            pickle.dump(candles, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return candles


def backtest_with_info_key(key, config, route, extra_routes, candles, hp_dict, dna):
    from jesse.research import backtest
    import jesse.helpers as jh

    hp = jh.dna_to_hp(hp_dict, dna) if dna else None
    backtest_data = backtest(config, route, extra_routes, candles, True, hp)

    if backtest_data['total'] == 0:
        backtest_data = {'total': 0, 'total_winning_trades': None, 'total_losing_trades': None,
                         'starting_balance': None, 'finishing_balance': None, 'win_rate': None,
                         'ratio_avg_win_loss': None, 'longs_count': None, 'longs_percentage': None,
                         'shorts_percentage': None, 'shorts_count': None, 'fee': None, 'net_profit': None,
                         'net_profit_percentage': None, 'average_win': None, 'average_loss': None, 'expectancy': None,
                         'expectancy_percentage': None, 'expected_net_profit_every_100_trades': None,
                         'average_holding_period': None, 'average_winning_holding_period': None,
                         'average_losing_holding_period': None, 'gross_profit': None, 'gross_loss': None,
                         'max_drawdown': None, 'annual_return': None, 'sharpe_ratio': None, 'calmar_ratio': None,
                         'sortino_ratio': None, 'omega_ratio': None, 'serenity_index': None, 'smart_sharpe': None,
                         'smart_sortino': None, 'total_open_trades': None, 'open_pl': None, 'winning_streak': None,
                         'losing_streak': None, 'largest_losing_trade': None, 'largest_winning_trade': None,
                         'current_streak': None}

    return {**{'key': key}, **backtest_data}


def get_config():
    cfg_file = pathlib.Path('bulk_config.yml')

    if not cfg_file.is_file():
        print("bulk_config not found. Run create-config command.")
        exit()
    else:
        with open("bulk_config.yml", "r") as ymlfile:
            cfg = yaml.load(ymlfile, yaml.SafeLoader)

    return cfg
