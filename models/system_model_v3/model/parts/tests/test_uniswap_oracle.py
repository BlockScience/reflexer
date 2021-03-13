import copy
import time
import pytest
from uniswap_oracle import UniswapOracle
import random
class TestUniswapOraclee:
    def test_speed(self):
        o = UniswapOracle()

        cumulative_times = list(range(1, 4000))

        rai_balances = [random.randint(1000, 1000000) for _ in range(len(cumulative_times))]
        eth_balances = [random.randint(1000, 1000000) for _ in range(len(cumulative_times))]
        eth_prices = [random.randint(100, 1000) for _ in range(len(cumulative_times))]

        states = [{'RAI_balance': rai_balances[i], 'ETH_balance': eth_balances[i],
                   'eth_price': eth_prices[i], 'cumulative_time': cumulative_times[i]} for i in range(len(cumulative_times))]
        s = time.time()
        for state in states:
            o.update_result(state)
            copy.deepcopy(o)
        print(f"took {time.time() - s} secs")

