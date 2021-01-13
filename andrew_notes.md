## Andrew comments
* Too many test and potential ways to run models in the readme. Can we cut or streamline, or at least explain why so many separate steps and what they do.
* Not enough context on what we are solving, etc. 
* Glossary is good, but needs to be finished. Add concepts such as CDP, ADP,redemption price, market price, redemption rate, etc. These can be found from the reflexer whitepaper
* Too many directories with too many additional things. Confusing file structure.

### Notebook review
* https://github.com/BlockScience/reflexer/blob/master/notebooks/system_model_v2/notebook_debt_market.ipynb
	- Describe what the debt market model means. Provide an overview with math equations and write-up. See example here: https://nbviewer.jupyter.org/github/BlockScience/Aragon_Conviction_Voting/blob/a5bf8accbc832c34e3cc7f206106edd89ea0aa7d/models/v3/Aragon_Conviction_Voting_Model.ipynb
	- Show how to download pickle file. Show in readme and here. Pull out glf_continue_callback and add to utilites file but describe here what it is doing and why. 
	- Instead of comments in code, moving the text to markdown is usually cleaner and easy to understand.
	- Abstract out a lot of processing stuff into another file. Same for the initial states and parameters. You can show some here and talk through how and why, but it is cleaner to be in a file.
	- Supress the pink model run output
	- Describe what are we analzying from the simulation? And what do we see?
	- Supress 61 output
	- Add a conclusion. What did we learn?
* https://github.com/BlockScience/reflexer/blob/master/notebooks/system_model_v1/notebook_validation_market_price.ipynb
 	- Define the math for the PI controller and what specifically you are tuning in the overview
 	- Describe what you see in the plots
 	- Provide a conclusion where you tell what we learned from the simulation
 * https://github.com/BlockScience/reflexer/blob/master/notebooks/system_model_v1/notebook_validation_debt_price.ipynb
 	- Beef up the overview. What specifically are we doing? Add math if possible and text
 	- add a conclusion, explain plots
 * https://github.com/BlockScience/reflexer/blob/master/notebooks/system_model_v1/notebook_validation_regression.ipynb
 	- Same feedback
 * https://github.com/BlockScience/reflexer/blob/master/notebooks/system_model_v2/notebook_secondary_market_maker.ipynb
  	- Same feedback
  * https://github.com/BlockScience/reflexer/blob/master/notebooks/solidity_cadcad/notebook_solidity_validation.ipynb
  	- Same feedback


 ### General code notes
 * Refactor to standard best practices structure
 * Document, document, document. Not line by line code, but what are we doing and why?
 * What do the plots tell us?
