# Misc Notes, Aggregate Arbitrageur Model

###### tags: `Reflexer` 

The arbitrageur conditions upon the following information at time $t$:

1. **CDP debt subsystem information**:
  - Total collateral committed $Q(t)$ in ETH;
  - Total debt borrowed on committed collateral $D(t)$ in RAI;
  - Liquidation ratio $\bar{L}$;
  - Redemption price $p^r(t)$ in USD/RAI;
  - Redemption rate $r(t)$;
  - Debt ceiling $\bar{D}$ in RAI;
  - Gas amount for calling contract $\gamma_{CDP}$ in units of gas;
2. **Uniswap secondary market information**:
  - Reserve quantity of RAI $R_{RAI}(t)$;
  - Reserve quantity of ETH $R_{ETH}(t)$;
  - Swap fee $\phi_u$ as a fraction of input 
  - Gas amount for calling swap $\gamma_U$ in units of gas;
3. **Aribitrage Pricing Theory (APT) information**:
  - Expected future market price $\mathbb{E}_t \: p(t+1)$ in USD/RAI (based upon APT use of single-collateral DAI data);
4. **Ethereum information**:
  - Price of _ether_: $p^e(t)$ in USD/ETH.
  - Gas price $c(t)$ in ETH/gas.


An arbitrageur can compute the _pool market price_ of RAI for ETH in Uniswap, which must be scaled by the price of ETH in USD, $p^e(t)$ to convert to the market price $p(t)$ in USD/RAI:
$$
p(t) := p^e(t)\frac{R_{ETH}(t)}{R_{RAI}(t)}.
$$

## System constraints

1. The arbitrageur is assumed to be able to draw upon as much ETH as required to maximize their objective, _without changing the price of ETH_ $p^e(t)$. If the arbitrageur requires ETH then it is assumed that this is covered either from individual holdings or from purchases made using other assets (e.g. fiat).
2. The arbitrageur is assumed to be able to take out additional debt up to the _debt ceiling_ $\bar{D}$ of the CDP subsystem, i.e.
$$
\forall t, \: D(t) \leq \bar{D}.
$$
At time $t$, if the arbitrageur's optimal $d^\star$ decision would ever cause $D(t) + d^\star > \bar{D}$, then $d^\star := \bar{D} - D(t)$, so that the debt ceiling is not violated.
3. The arbitrageur is assumed to know how to compute those combinations of collateral and debt that are feasible to generate from the debt market. This is modeled in cadCAD as those combinations of $(Q,D)$ such that:
$$
\frac{p^e(t) Q(t)}{p^r(t)D(t)} \geq \bar{L}.
$$
4. We collect the feasible combinations of $(Q,D)$ given #1 - #3 above into the **set** $F(p^e(t), p^r(t); \bar{L}, \bar{D})$. This set changes over time in response to ETH price and RAI redemption price changes, and is functionally dependent upon $\bar{L}$ and $\bar{D}$ (we assume here that an arbitrageur would strictly prefer that positions are not liquidated). An arbitrageur will make trades in the CDP subsystem that are feasible given this set.


6. The process of arbitrage involves 1) investing a quantity into one market to receive another quantity, and then 2) investing that quantity into the second market to receive a third quantity. The value of the first and third quantities are then compared--if the third is greater than the first, then a positive arbitrage gain is realized.

   This process can be formalized by treating the CDP debt market _as if_ it were an AMM. For example, if (cf. below) the secondary market price exceeds the redemption price by some factor, then an investment of ETH is made into the CDP market to borrow RAI. This is in turn sold on the Uniswap market to receive ETH, and the original ETH investment is compared to the received ETH.
   
   [Koch and Zargham/Zargham and Koch](https://hackmd.io/7Z2e-Is7Toi-5SaRl4K3tA?both) (2021) have presented this formalization for two Uniswap markets, and the process may be extended to any AMM-like environment, such as the CDP market here. In this example, given an _input_ $q$ in ETH to the CDP market, the _output_ $z$ of ETH in the Uniswap market may be written as:
   $$
   d \in \textbf{proj}_{q} F(p^e(t), p^r(t); \bar{L}, \bar{D}), \\
   z := p(t+1) d = f(d; R_{RAI}, R_{ETH}, \phi_U),
   $$
where:
   - $\textbf{proj}_{q} F(p^e(t), p^r(t); \bar{L}, \bar{D})$ is the set of feasible $d$ selections, given the input of $q$ into the CDP market;
   - $f(.)$ is the outcome of the swap RAI-for-ETH and $\phi_U$ is the swap fee on the Uniswap market:
     $$
     f(d; R_{RAI}, R_{ETH}, \phi_U) := \frac{R_{ETH} \cdot d(1-\phi_U)}{R_{RAI}+d(1-\phi_U)};
     $$
   
## Exogenous (uncontrolled) processes

1. The price of ETH is assumed to be an **exogenous process**, unrelated to actions taken by the arbitrageur (cf. System constraints #1 above).
2. The 'noise trading' liquidity demand for RAI in the secondary market is assumed to be an **exogenous process**, which may or may not be correlated with actions taken by the arbitrageur.

## Optimization

The arbitrageur seeks to maximize a return, or profit, made by exploiting a difference between the price of RAI in the CDP subsystem, i.e. the redemption price $p^r(t)$, and the price of RAI in the secondary Uniswap market, i.e. the market price $p(t)$. This exploitation takes the form of debt and secondary market operations such that a net transfer of RAI from one market to the other garners a positive return.

For simplicty of exposition we classify the optimization that occurs according to two different state realizations, such that which optimization is performed depends upon these realizations. 

### Realization 1: $p^r(t) < \frac{1-\phi}{\bar{L}}p(t)$

Under this realization the price of RAI in the debt market is sufficiently cheaper than its secondary market price. An arbitrageur will attempt to maximize its return from this difference provided that the opportunity cost of doing so is low enough, i.e. provided that the _beliefs_ of the arbitrageur induce non-zero trading decisions. This assumption corresponds to the narrative articulated in Reflexer's white paper: if the arbitrageur believes that prices will continue to fall, they will act now to take profits by selling RAI on the secondary market, as the price difference is expected to be smaller in the future.

The formalization of this narrative requires an _expectation_ of the future price $p(t+1)$, $\mathbb{E}_t \: p(t+1)$. This is furnished by the APT market model, which provides a computation of the expected future market price as a function of the exogenous processes and based upon historical data for single-collateral DAI. If $\mathbb{E}_t \: p(t+1) < p(t)$, then the arbitrageur will attempt to realize a profit by selecting its CDP collateral deposit $q > 0$ to maximize:
$$
f(d; R_{RAI}, R_{ETH}, \phi_U) - q  - c(t)(\gamma_U + \gamma_{CDP}),
$$
such that
$$
p^e(t) (Q + q) \geq \bar{L}p^r(t)(D + d), \qquad (\mu_1)
$$
$$
\bar{D} \geq D + d, \qquad (\mu_2)
$$
$$
q \geq 0 \quad (\mu_q), \: d \geq 0 \quad (\mu_d).
$$

#### First Order & Slack Conditions

$$
\frac{\partial}{\partial q}: -1 + p^e(t)\mu_1 + \mu_q = 0, \\
\frac{\partial}{\partial d}: \frac{R_{RAI} R_{ETH} (1 - \phi_U)}{(R_{RAI} + d(1-\phi_U))^2} - \bar{L}p^r(t)\mu_1  - \mu_2 + \mu_d = 0, \\
(p^e(t) (Q + q) - \bar{L}p^r(t)(D + d))\mu_1 = 0, \\
(\bar{D} - D - d)\mu_2 = 0, \\
q\mu_q = d\mu_d = 0.
$$

Interior solution when $q > 0,d > 0 \Rightarrow \mu_q = \mu_d = 0$:

$$
\mu_1 = \frac{1}{p^e(t)}, \\
\frac{R_{RAI} R_{ETH} (1 - \phi_U)}{(R_{RAI} + d(1-\phi_U))^2} - \bar{L}p^r(t)\mu_1  - \mu_2 = 0, \\
(p^e(t) (Q + q) - \bar{L}p^r(t)(D + d))\mu_1 = 0, \\
(\bar{D} - D - d)\mu_2 = 0. \\
$$

Since $\mu_1 = 1/p^e(t)$,
$$
(Q + q) = \frac{\bar{L}p^r(t)}{p^e(t)}(D + d) \Rightarrow \\
d^\star = \frac{p^e(t)}{\bar{L}p^r(t)}(Q + q^\star) - D,
$$
i.e. the liquidation ratio binds (this makes intuitive sense without a motive for precautionary savings, such as risk tolerance of a future change in prices).


Substitution of $d^\star$ into FOC wrt $q$ and simplifying yields:
$$
d^\star = \frac{g_1(\mu_2) - R_{RAI}}{(1-\phi_U)}, \\
q^\star = \frac{\bar{L}p^r(t)}{p^e(t)} \left ( D + d^\star \right ) - Q, \\
g_1(\mu_2) := \left ( \frac{p^e(t)R_{RAI}R_{ETH}(1-\phi)}{\bar{L} p^r(t) + \mu_2} \right )^{1/2}.
$$

These are the equations governing deposits ($q^\star)$ and borrowing ($d^\star$) in the event that it is in the arbitrageur's best interest to buy RAI on the debt market and sell in the Uniswap market.

Notice that provided it is the case that:
$$
\frac{\partial f}{\partial d^\star}\frac{\partial d^\star}{\partial g_1} \geq \frac{\partial q^\star}{\partial g_1},
$$
it will be optimal to set $\mu_2 = 0$ (since $\frac{\partial g_1(\mu_2)}{\partial \mu_2} < 0$). This case can be simplified to:
$$
\frac{R_{RAI} R_{ETH} (1 - \phi_U)}{(R_{RAI} + d^\star(1-\phi_U))^2} \geq \frac{\bar{L}p^r(t)}{p^e(t)},
$$
or
$$
\frac{R_{RAI} R_{ETH} (1 - \phi_U)}{g_1(\mu_2)^2} \geq \frac{\bar{L}p^r(t)}{p^e(t)} \Leftrightarrow
$$
$$
  \bar{L} p^r(t) + \mu_2  \geq \bar{L}p^r(t),
$$
which is always true since $\mu_2 \geq 0$. The arbitrageur borrows up to the debt ceiling if it binds (admitting the possibility that $\mu_2 > 0$), and will otherwise borrow the value given at the point $\mu_2 = 0$, i.e. when $g(\mu_2) = g(0)$ (cf. below). 

It is important to note that there is a _restriction_ on redemption and market prices that indicates to the arbitrageur when it is optimal to _borrow_ RAI to _sell_ on Uniswap. This is the case when $d^\star > 0$, i.e. when
$$
d^\star = \frac{g_1(0) - R_{RAI}}{(1-\phi_U)} > 0 \Rightarrow \\
d^\star = \left ( \frac{p^e(t)R_{RAI}R_{ETH}(1-\phi)}{\bar{L} p^r(t)} \right )^{1/2} - R_{RAI} > 0 \Rightarrow \\
\frac{p^e(t)R_{RAI}R_{ETH}(1-\phi)}{\bar{L} p^r(t)} > (R_{RAI})^2 \Rightarrow \\
p^e(t)\frac{R_{ETH}}{R_{RAI}} > \frac{\bar{L}}{(1-\phi)}p^r(t) \Leftrightarrow \\
p(t) > \frac{\bar{L}}{(1-\phi)}p^r(t).
$$

Finally, the profit of the arbitrageur at the optimal deposit and borrowing values must be positive net of gas costs, otherwise it will not be worth trading. In other words,
$$
f(d^\star; R_{RAI}, R_{ETH}, \phi_U) - q^\star  - c(t)(\gamma_U + \gamma_{CDP}) > 0.
$$

Thus, it is not enough simply that there exists a difference $p(t) - p^r(t)$ to "exploit". Rather, the true cost of borrowing RAI to sell on Uniswap depends both upon the Liquidation Ratio $\bar{L}$ and the Uniswap fee $\phi_U$. If, for example, the Uniswap fee is very high, the difference between the Uniswap and redemption prices must be high enough to overcome this trading friction. In addition, if very little RAI can be generated from a large CDP collateral injection, then again the Uniswap price must be high enough to compensate for the large collateral outlay.


::: success
**Conditions** under which an arbitrage is executed:
1. $p^r(t) < \frac{1-\phi}{\bar{L}} p(t)$;
2. $\mathbb{E}_t \: p(t+1) < p(t)$.
3. (Positive net profit): $z^\star - q_{deposit}^\star  - c(t)(\gamma_U + \gamma_{CDP}) > 0.$

cadCAD representations & notes:

1. $\mathbb{E}_t \: p(t+1)$ is $\texttt{expected_market_price}$ from the APT model
2. $p^r(t)$ is $\texttt{target_price}$ (redemption price)
3. $p(t)$ is $\texttt{market_price}$; the ratio of $R_{ETH}$ and $R_{RAI}$ scaled by $p^e(t)$
4. $\bar{L}$ is $\texttt{liquidation_ratio}$; note that here $\texttt{liquidation_buffer} = 1$ by assumption
5. $\phi_U$ will be the $0.3\%$ Uniswap fee
6. $Q(t)$ is $\texttt{deposited}$, the **total** deposited collateral in the CDP subsystem
7. $D(t)$ is $\texttt{borrowed}$, the **total** debt borrowed in the CDP subsystem
8. $\bar{D}$ is the debt ceiling, which is (likely) a protocol-level definition (exogenous variable)
9. $z^\star$ is the amount of ETH received from the swap on Uniswap of the borrowed RAI $d^\star_{borrow}$. It is not needed for the CDP subsystem, but may be accounted for as the 'in the pocket' earnings of the arbitrageur. Similarly, $q^\star_{deposit}$, the optimal deposit of ETH collateral into the CDP, is the 'out of pocket' payment of the arbitrageur. The _gross profit_ of the arbitrageur is thus $z^\star - q^\star_{deposit}$.

The optimal **borrow** $d_{borrow}^\star$ and **deposit** $q_{deposit}^\star$ are
$$
d_{borrow}^\star = \min \left \{\bar{D} - D(t), \frac{g_1(0) - R_{RAI}(t)}{(1-\phi_U)} \right \}, \\
q_{deposit}^\star = \frac{\bar{L}p^r(t)}{p^e(t)} \left ( D(t) + d_{borrow}^\star \right ) - Q(t), \\
z^\star := \frac{R_{ETH} \cdot d^\star_{borrow}(1-\phi_U)}{R_{RAI}+d^\star_{borrow}(1-\phi_U)}, \\
g_1(0) := \left ( \frac{p^e(t)R_{RAI}R_{ETH}(1-\phi)}{\bar{L} p^r(t)} \right )^{1/2}.
$$

**Note**: The Liquidation Ratio is always met in this market, since it always pays to borrow as much as possible on the existing collateral (there is no precaution taken according to future expectations since the market price is expected to _fall_ from the APT prediction). This runs counter to the single-collateral DAI historical data, where the Liquidation ratio was set to 1.5, but the actual collateralization ratio was around 3.
:::


### Realization 2: $p^r(t) > \frac{1}{(1-\phi_U)\bar{L}}p(t)$

A similar approach to the above applies for the arbitrage strategy of _buying_ RAI on Uniswap to _pay down_ debt from an open CDP position. The resulting strategies are:

::: success
**Conditions** under which an arbitrage is executed:
1. $p^r(t) > \frac{1}{(1-\phi)\bar{L}} p(t)$;
2. $\mathbb{E}_t \: p(t+1) > p(t)$.
3. (Positive net profit): $q^\star_{withdraw} - z^\star - c(t)(\gamma_U + \gamma_{CDP}) > 0.$

cadCAD representations & notes:

1. $\mathbb{E}_t \: p(t+1)$ is $\texttt{expected_market_price}$ from the APT model
2. $p^r(t)$ is $\texttt{target_price}$ (redemption price)
3. $p(t)$ is $\texttt{market_price}$, the ratio of $R_{ETH}$ and $R_{RAI}$ scaled by $p^e(t)$
4. $\bar{L}$ is $\texttt{liquidation_ratio}$; note that here $\texttt{liquidation_buffer} = 1$ by assumption
5. $\phi_U$ will be the $0.3\%$ Uniswap fee
6. $Q(t)$ is $\texttt{deposited}$, the **total** deposited collateral in the CDP subsystem
7. $D(t)$ is $\texttt{borrowed}$, the **total** debt borrowed in the CDP subsystem
8. $z^\star$ is the optimal amount of ETH to swap in Uniswap for $d^\star$ RAI. It is not needed for the CDP subsystem, but may be accounted for as the 'out of pocket' payment of the arbitrageur. Similarly, $q^\star_{withdraw}$, the optimal withdrawal of ETH collateral from the CDP, is the 'in the pocket' earnings of the arbitrageur. The _gross profit_ of the arbitrageur is thus $q^\star_{withdraw} - z^\star$.

The optimal **repayment** $d_{repay}^\star$ and **withdrawal** $q_{withdraw}^\star$ are 
$$
d_{repay}^\star = \frac{R_{RAI}z^\star(1-\phi_U)}{R_{ETH} +  z^\star (1-\phi_U)}, \\
q_{withdraw}^\star = Q(t) - \frac{\bar{L}p^r(t)}{p^e(t)} \left ( D(t) - d_{repay}^\star \right ), \\
z^\star = \frac{g_2(0) - R_{ETH}(t)}{(1-\phi_U)}, \\
g_2(0) := \left (R_{RAI}R_{ETH}(1-\phi_U) \bar{L}\frac{p^r(t)}{p^e(t)} \right )^{1/2}.
$$
**Note**: The Liquidation Ratio is always met in this market, since it always pays to withdraw as much collateral as possible (there is no precaution taken according to future expectations since the market price is expected to _rise_ from the APT prediction). This runs counter to the single-collateral DAI historical data, where the Liquidation ratio was set to 1.5, but the actual collateralization ratio was around 3.
:::

