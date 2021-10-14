# Arbing AMMs


## statespace definitions

Suppose there are 2 AMMs, each with 2 tokens and equal weights. the quantity of token 1 in AMM "x" will be denoted $X_1$, and the quantity of token 1 in AMM "z" is denoted $Z_1$. Expanding this notation to cover the entire joint state space we have 

| name | symbol | defintion |
| -------- | -------- | -------- | 
|     | $X_1$     | The Quantity of token 1 in AMM 'X'     |
| |  $X_2$ | The Quantity of token 2 in AMM 'X'|
| | $P_x = \frac{X_1}{X_2}$ |
| | $K_x = X_1 \cdot X_2$|| 
|     | $Z_1$     | Text     |
|  |  $Z_2$ |
| | $P_z = \frac{Z_1}{Z_2}$ |
| | $K_z = Z_1 \cdot Z_2$|| 

we suspect an arbitrage opportunity if $||P_x - P_z|| \ge \epsilon$, but we need to examine the transaction costs and the slippage in order to flesh out the true opportunity.

To do this we need to add in some extra parameters accounting for fees and gas costs. 

| name | symbol | defintion |
| -------- | -------- | -------- |
|     | $\gamma_x$   | gas amount for calling swap on AMM "x"  |
|  |  $\gamma_z$ | gas amount for calling swap on AMM "z" |
| | $c$ | the ETH paid per unit gas | 
| | $\phi_x$ | fee for swapping on AMM "x"|
| | $\phi_z$ | fee for swapping on AMM "z"|
| | $\rho_1$| price of token 1 in eth | 
| |$\rho_2$ | price of token 2 in eth |

suppose we wanted to define the Eth value of the assets in the AMMs, we would have
$$L_x = \rho_1 X_1 + \rho_2 X_2$$
and
$$L_z = \rho_1 Z_1 + \rho_2 Z_2$$


now we can define the swap mechanism for each AMM.

Suppose we have a swap on AMM 'x' with input trade $x_1$ the

$$x_2 = f(x_1; X_1, X_2, \phi_x) = \frac{X_2 \cdot x_1(1-\phi_x)}{X_1+x_1(1-\phi_x)}$$

complementarily we we will do the reverse in AMM "z"

$$z_1 = f(z_2; Z_1, Z_2, \phi_z) = \frac{Z_1 \cdot z_2(1-\phi_z)}{Z_2+z_2(1-\phi_z)}$$

suppose we compose these into a sequence, there are actually 4 sequences based on where you are using AMM "x" then AMM "z" and trading token "1" then token "2" or flipping either or both of those orderings. For the purpose of this analysis we will consider the AMM "x" first, and trading token "1" in first.

this gives us the constraint:
$$ x_2 = z_2 $$

composing the state updates we have 

$$z_1 = f(f(x_1; X_1, X_2, \phi_x); Z_1, Z_2, \phi_z)$$

Suppose we examine the "raw" profit equation

$$R = z_1-x_1$$

extend this to include gas costs and let's use ethereum as a numeraire

$$E = \rho_1 (z_1-x_1) - c\cdot (\gamma_x + \gamma_z)$$

our actual inequality for real profit is $E(action)>0$.


the key to understanding the arb opportunities is to be able say under the "conditions"
$$P_x, P_z, \rho_1, \rho_2, \phi_x, \phi_z, \bar c, K_x, K_z $$

is $E$ the largest

now once we one can do this for two 50-50 pools, you can generalize to weighted pools (or in your case a 50-50 uniswap pool versus a general weights balancer), and include the balancer weights in the "conditions". 


arb value avaible
$$ E = G(conditions)$$

analytically (and in data) demonstrate regions of large "$E$" within the conditions space.


---note---
Might also include personal liquidity as a variable, or state this is operating assuming infinite liquidity (if the token in question has flash loans available, it may almost be true... but thats more fees and gas costs) 

Jeff presented this as an idea for arbing between honeyswap and uniswap, which is where liquidity would really matter because the time to cross the bridge is non negligible, so you will want to have deep pockets on both sides and rebalance as needed.

If you have less personal liquidity in that token, the gas may eat up your profit since you can't maximize the opportunity, or you will have to swap various other tokens to achive the needed liquidity.