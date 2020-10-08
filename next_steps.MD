# Possible Next Steps

## Hybrid market price
In order to be able to shock the system at the market price level, we could explore making it so that the market price
was defined as the sum of two signals: 
1. the output of the market model as it is currently defined;
1. an exogenous signal (steps, ramps, sinusoids, martingales,...)

## Revisiting the debt price model
One of the limitations of the current debt price model is that we cannot run simulations with variations of it around 
it's current setup, which would be desirable in the process of designing a robust redemption rate controller. To address 
that, we could revisit the debt price model with the goal of deriving a more interpretable one, based on a differential equation, 
so that we can run Monte Carlo experiments with variations of its coefficients.

In addition to that, it's worth exploring variations of the definition of debt price for the purposes of fitting the debt price model. 
We currently have it defined as the 10-days exponential moving average of the market price. 
However, this is a lagging indicator of the market price, and our assumption is that it is actually the market 
price that tracks the debt price, and not the opposite. One alternative would be to simply shift the 10-days EMA by a few days (10? 15?).

It's important to keep in mind that after revisiting the debt price model the market price model must be refitted.

## System model with debt price model in the loop
In the current system model, the debt price model is not ran in simulation time because we're interpreting it as being independent of 
the state variables in the system. However, if we were to interpret the debt variables in the debt price model as being denominated in USD rather 
than in DAI, the redemption price would have an effect on them. Meaning we would have to predict the debt price based on the computed USD-denominated 
debt variables taking into account the redemption price in the simulation's context. Similarly, we would need to replace the stability fee as one of the 
independent variables in the model with the combined "rate of change of the debt":  
((1 + stability fee)*(1 + redemption rate) - 1)

<a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;(1&plus;\beta)(1&plus;d)-1\\&space;\text{where:}\\&space;\beta\text{&space;is&space;the&space;stability&space;fee&space;and}\\&space;d\text{&space;is&space;the&space;redemption&space;rate}" target="_blank"><img src="https://latex.codecogs.com/png.latex?\inline&space;(1&plus;\beta)(1&plus;d)-1\\&space;\text{where:}\\&space;\beta\text{&space;is&space;the&space;stability&space;fee&space;and}\\&space;d\text{&space;is&space;the&space;redemption&space;rate}" title="(1+\beta)(1+d)-1\\ \text{where:}\\ \beta\text{ is the stability fee and}\\ d\text{ is the redemption rate}" /></a>

## Add contraints to controller
The controller currently in use in our model is free of some contraints implemented in the solidity version, 
such as the noise barrier for example. Other constraints that may have been implemented in the model, such as the 
leaky integrator, have not been verified for consistency across implementation like the Kp and Ki coefficients have. 
Other constraints might be required, such as saturation on the output of the controller.
