import models.options as options
import models.constants as constants
import models.system_model_v3.model.parts.failure_modes as failure


def update_target_rate(params, substep, state_history, state, policy_input):
    """
    Calculate the PI controller target rate using the Kp and Ki constants and the error states.
    """

    if state['cumulative_time'] % params['control_period'] == 0:
        error = state["error_star"]  # unit USD
        error_integral = state["error_star_integral"]  # unit USD * seconds

        target_rate = (
            params["kp"] * error + (params["ki"] / params['control_period']) * error_integral
        )

        target_rate = target_rate if policy_input["controller_enabled"] else 0  # unitless
    else:
        target_rate = state['target_rate'] if policy_input["controller_enabled"] else 0

    return "target_rate", target_rate


def update_target_price(params, substep, state_history, state, policy_input):
    """
    Update the controller target_price state ("redemption price") according to the controller target_rate state ("redemption rate")

    Notes:
    * exp(bt) = (1+b)**t for low values of b; but to avoid compounding errors
    * we should probably stick to the same implementation as the solidity version
    * target_price =  state['target_price'] * FXnum(state['target_rate'] * state['timedelta']).exp()
    * target_price =  state['target_price'] * math.exp(state['target_rate'] * state['timedelta'])
    """

    target_price = state["target_price"]
    try:
        target_price = (
            state["target_price"] * (1 + state["target_rate"]) ** state["timedelta"]
        )
    except OverflowError as e:
        raise failure.ControllerTargetOverflowException((e, target_price))

    if target_price < 0:
        target_price = 0

    return "target_price", target_price


def observe_errors(params, substep, state_history, state):
    """
    Calculate the error between the target and market price, using the error_term parameter.
    The error_term parameter allows you to set whether the error is calculated as target - market or market - target.
    """

    target_price = state["target_price"] * params["liquidation_ratio"] if params["rescale_target_price"] else state["target_price"]
    error = params["error_term"](target_price, state["market_price_twap"])

    return {"error_star": error}


def store_error_star(params, substep, state_history, state, policy_input):
    """
    Store the error_star state, which is the error between the target and market price.
    """

    error = policy_input["error_star"]

    return "error_star", error


def update_error_star_integral(params, substep, state_history, state, policy_input):
    """
    Update and store the error integral state.

    Calculate the error integral using numerical integration (trapezoid rule):
    See https://github.com/cadCAD-org/demos/blob/master/tutorials/numerical_computation/numerical_integration_1.ipynb
    """

    # Numerical integration (trapezoid rule)
    error_star_integral = state["error_star_integral"]
    old_error = state["error_star"]  # unit: USD
    new_error = policy_input["error_star"]  # unit: USD
    mean_error = (old_error + new_error) / 2  # unit: USD
    timedelta = state["timedelta"]  # unit: time (seconds)
    area = mean_error * timedelta  # unit: USD * seconds

    # Select whether to implement a leaky integral or not
    if params[options.IntegralType.__name__] == options.IntegralType.LEAKY.value:
        alpha = params["alpha"]
        remaing_frac = float(alpha / constants.RAY) ** timedelta  # unitless
        remaining = int(remaing_frac * error_star_integral)  # unit: USD * seconds
        error_integral = remaining + area  # unit: USD * seconds
    else:
        error_integral = error_star_integral + area  # unit: USD * seconds

    return "error_star_integral", error_integral  # unit: USD * seconds
