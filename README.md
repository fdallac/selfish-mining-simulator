# Selfish mining simulator
This is a selfish-mining attack simulator with interactive GUI, implemented as a project for Dr. Grunspan Cyril's course "Cryptocurrencies" at ESILV. \
The purpose of this work is to compute the profitability of selfish-mining strategy against Bitcoin blockchain, and in particular the first-day of gain. \
Selfish mining is a deviant mining strategy, where a major mining operator withholds mined blocks and releases them with a well timed strategy in order to invalidate the maximum number of blocks mined by the rest of the network. Profitability of the attack is directly related to reduction of mining difficulty as consequense of slowering down of the network. \
In this sense, for some ranges of hashrate and connection rate, selfish-mining attacker may have to stand a first period when his reward is lower than the honest counterpart and this could be inhibitory since mining costs are generally constant and the attack may not be convenient. \
\
Simulator interface shows:
- **attack reward over time**, parametrized on the hashrate;
- **difficulty adjustment over time**, where 1 is the initial difficulty level;
- **distribution of the winning starting day**, i.e. how many days attacker needs to wait before his strategy starts to be more profitable than honest mining (*warning:* average value is more undestimated as more simulations lie under the honest reward level, and the attacker never starts to have an advantage - I will fix this bug as soon as possible)
- **distribution of orphan blocks**, i.e. honestly mined blocks that end up to be invalidated after the release of the attacker branch. 

# Instruction to run
By Command Window:
> CD [current path] \
> conda activate \
> bokeh serve --show simu_guy.py

# Preview
![PREVIEW](https://i.ibb.co/L1C8QTQ/prev.png)

# Resources
Grunspan C., Perez R. "On Profitability of Selfish Mining \
*https://webusers.imj-prg.fr/~ricardo.perez-marco/publications/articles/OnSelfishMining20.pdf*
