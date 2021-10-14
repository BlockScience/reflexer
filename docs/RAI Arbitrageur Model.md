# RAI Arbitrageur Model

The arbitrageur conditions upon the following information at time $t$:

1. **CDP debt subsystem information**:
  - Total collateral committed $Q(t)$ in ETH;
  - Total debt drawn on committed collateral $D(t)$ in RAI;
  - Liquidation ratio $\bar{L}$;
  - Redemption price $p^r(t)$ in USD/RAI;
  - Redemption rate $r(t)$;
  - Debt ceiling $\bar{D}$ in RAI;
2. **Uniswap secondary market information**:
  - Reserve quantity of RAI $R_{RAI}(t)$;
  - Reserve quantity of USD $R_{USD}(t)$;
  - Swap fee $\phi_u$ as a fraction of input 
  - Gas amount for calling swap $\gamma_U$ in units of gas;
3. **Aribitrage Pricing Theory (APT) information**:
  - Expected future market price $\mathbb{E}_t \: p(t+1)$ in USD/RAI;
4. **Ethereum information**:
  - Price of _ether_: $p^e(t)$ in USD/ETH.
  - Gas price $c(t)$ in ETH/gas.


An arbitrageur can compute the _pool market price_ of RAI for USD in Uniswap:
$$
p(t) := \frac{R_{USD}(t)}{R_{RAI}(t)}.
$$

## Controlled processes

The arbitrageur seeks to maximize its expected profit from engaging in debt and secondary market operations. Its decision (or control) variables are:

1. The amount of ETH to add to/remove from the debt market: $\Delta Q$; if $\Delta Q \leq 0$ this is a _lock_ of collateral, if $\Delta Q \geq 0$ this is a _free_ of collateral;
2. The amount of USD to add to/remove from the secondary market: $\Delta Z$; if $\Delta Z \leq 0$ this the amount spent for a _purchase_ of RAI, if $\Delta Z \geq 0$ these are proceeds from a _sale_ of RAI.
3. The amount of RAI to borrow from/repay to the debt market: $\Delta D$; if $\Delta D \leq 0$ this is a _wipe_ of repaid debt, if $\Delta D \geq 0$ this is a _draw_ of additional debt;
4. The amount of RAI to purchase or to sell on the secondary market: $\Delta R$; if $\Delta R \leq 0$ this is a _sale_ of RAI, if $\Delta R \geq 0$ this is a _purchase_ of RAI.

These control variables are not generally independent. In practice, the system constraints and the Uniswap market mechanics reduce the dimension of the control space from four to one: in what follows, it will be shown that either $\Delta Q$ or $\Delta Z$ is the control variable used to maximize the profit from an arbitrage opportunity.


## System constraints

1. The arbitrageur is assumed to be able to draw upon as much ETH as required to maximize their objective, _without changing the price of ETH_ $p^e(t)$. If the arbitrageur requires ETH then it is assumed that this is covered either from individual holdings or from purchases made using other assets (e.g. fiat).
2. The arbitrageur is assumed to be able to take out additional debt up to the _debt ceiling_ $\bar{D}$ of the CDP subsystem, i.e.
$$
\forall t, \: D(t) \leq \bar{D}.
$$
At time $t$, if the arbitrageur's optimal $\Delta D$ decision would ever cause $D(t) + \Delta D > \bar{D}$, then $\Delta D := \bar{D} - D(t)$, so that the debt ceiling is not violated.
3. The arbitrageur is assumed to know how to compute those combinations of collateral and debt that are feasible to generate from the debt market. This is modeled in cadCAD as those combinations of $(Q,D)$ such that:
$$
\frac{p^e(t) Q(t)}{p^r(t)D(t)} \geq \bar{L}.
$$
4. We collect the feasible combinations of $(Q,D)$ given #1 - #3 above into the **set** $F(p^e(t), p^r(t); \bar{L}, \bar{D})$. This set changes over time in response to ETH price and RAI redemption price changes, and is functionally dependent upon $\bar{L}$ and $\bar{D}$ (we assume here that an arbitrageur would strictly prefer that positions are not liquidated). An arbitrageur will make trades in the CDP subsystem that are feasible given this set.

:::warning
Q: Is there a per-redemption/per-lock fee assessed in the CDP market?
:::
6. The process of arbitrage involves 1) investing a quantity into one market to receive another quantity, and then 2) investing that quantity into the second market to receive a third quantity. The value of the first and third quantities are then compared--if the third is greater than the first, then a positive arbitrage gain is realized.

   This process can be formalized by treating the CDP debt market _as if_ it were an AMM. For example, if (cf. below) the secondary market price exceeds the redemption price, then an investment of ETH is made into the CDP market to realized RAI. This is in turn sold on the Uniswap market to receive USD, and (using the price of ETH) the original investment is compared to the value of USD in ETH.
   
   [Koch and Zargham/Zargham and Koch](https://hackmd.io/7Z2e-Is7Toi-5SaRl4K3tA?both) (2021) have presented this formalization for two Uniswap markets, and the process may be extended to any AMM-like environment, such as the CDP market here. In this example, given an _input_ in ETH to the CDP market of $\Delta Q \leq 0$, the _output_ $\Delta Z \geq 0$ of USD in the Uniswap market may be written as:
   $$
   -\Delta R = \Delta D \in \textbf{proj}_{\Delta Q} F(p^e(t), p^r(t); \bar{L}, \bar{D}), \\
   \Delta Z := p(t+1) |\Delta R| = f(\Delta R; R_{RAI}, R_{USD}, \phi_U),
   $$
where:
   - $\textbf{proj}_{\Delta Q} F(p^e(t), p^r(t); \bar{L}, \bar{D})$ is the set of feasible $\Delta D$ selections, given the input of $\Delta Q$ into the CDP market.
   The latter set can be simplified considerably if it is assumed that all open CDP positions are fully leveraged, providing a unique value of $\Delta D$:
   $$
   \Delta D = \frac{p^e(t) (Q(t) - \Delta Q)}{\bar{L}p^r(t)} - D(t).
   $$
   - $f(.)$ is the outcome of the swap RAI-for-USD and $\phi_U$ is the swap fee on the Uniswap market:
     $$
     f(\Delta R; R_{RAI}, R_{USD}, \phi_U) := \frac{R_{USD} \cdot |\Delta R|(1-\phi_U)}{R_{RAI}+2|\Delta R|(1-\phi_U)};
     $$
   
## Exogenous (uncontrolled) processes

1. The price of ETH is assumed to be an **exogenous process**, unrelated to actions taken by the arbitrageur (cf. System constraints #1 above).
2. The 'noise trading' liquidity demand for RAI in the secondary market is assumed to be an **exogenous process**, which may or may not be correlated with actions taken by the arbitrageur.

## Optimization

The arbitrageur seeks to maximize a return, or profit, made by exploiting a difference between the price of RAI in the CDP subsystem, i.e. the redemption price $p^r(t)$, and the price of RAI in the secondary Uniswap market, i.e. the market price $p(t)$. This exploitation takes the form of debt and secondary market operations such that a net transfer of RAI from one market to the other garners a positive return.

For simplicty of exposition we classify the optimization that occurs according to two different state realizations, such that which optimization is performed depends upon these realizations. 

### Realization 1: $p^r(t) < p(t)$

Under this realization the price of RAI in the debt market is cheaper than its secondary market price. An arbitrageur will attempt to maximize its return from this difference provided that the opportunity cost of doing so is low enough, i.e. provided that the _beliefs_ of the arbitrageur induce non-zero trading decisions. This assumption corresponds to the narrative articulated in Reflexer's white paper: if the arbitrageur believes that prices will continue to fall, they will act now to take profits by selling RAI on the secondary market, as the difference $p(t) - p^r(t)$ is expected to be smaller in the future.

The formalization of this narrative requires an _expectation_ of the future price $p(t+1)$, $\mathbb{E}_t \: p(t+1)$. This is furnished by the APT market model, which provides a computation of the expected future market price as a function of the exogenous processes and based upon historical data for single-collateral DAI. If $\mathbb{E}_t \: p(t+1) < p(t)$, then the arbitrageur will attempt to realize a profit by selecting $\Delta Q < 0$ to maximize:
$$
\frac{1}{p^e(t)}\Delta Z + \Delta Q - c(t)\gamma_U,
$$
such that
$$
\Delta Z = f(\Delta R; R_{RAI}, R_{USD}, \phi_U) > 0,
$$
$$
\Delta D = \frac{p^e(t) (Q(t) - \Delta Q)}{\bar{L}p^r(t)} - D(t) > 0,
$$
and
$$
\Delta R = -\Delta D < 0, \\
D(t) \leq \bar{D}.
$$

### Realization 2: $p^r(t) > p(t)$

Under this realization the price of RAI in the debt market is more expensive than in the secondary market. Following the same Reflexer white paper narrative as before, if the arbitrageur believes that prices will continue to rise, they will wish to act now to reduce their debt burden, as the difference $p^r(t) - p(t)$ is expected to be smaller in the future.

The formalization of this narrative again requires the APT market model's expectation of the future price $p(t+1)$, $\mathbb{E}_t \: p(t+1)$. If $\mathbb{E}_t \: p(t+1) > p(t)$, then the arbitrageur will attempt to realize a profit by selecting $\Delta Z < 0$ to maximize:
$$
\Delta Q + \frac{1}{p^e(t)}\Delta Z - c(t)\gamma_U,
$$
such that
$$
\Delta R = f^{-1}(\Delta Z; R_{RAI}, R_{USD}, \phi_U) > 0,
$$
$$
\Delta Q = \frac{p^r(t) \bar{L} (D(t) + \Delta D)}{p^e(t)} - Q(t) > 0,
$$
and
$$
\Delta R = -\Delta D >0, \\
D(t) \leq \bar{D}.
$$
