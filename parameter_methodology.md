## Parameter selection methodology



The overall objective of the project is to provide Rai with a software \textbf{Decision Support System} (DSS),\footnote{See \textcite{Sauter2011} for a general introduction to DSS and its applications to business decision-making, and e.g. \textcite{LeeAzamfarSingh2019} for an example of DSS and blockchain-supported Cyber-Physical Production Systems.} implemented via \href{https://cadcad.org}{\cadcad}, that achieves two design goals. First, the DSS achieves the \textbf{immediate project objective}, which is to provide stakeholders with the optimal \textit{economic policy parameters} (described more fully in this Report) that are required to help implement the \filecoin system. Such parameters are unknown at the time of system design, and require estimation and/or optimization using the system representation that a DSS provides. 

Second, the \textbf{ongoing project objective} will be to address the fact that as the system changes over time, its optimal parameter values (and hence participant behavior) may also change. \cadcad's DSS representation is created with dynamic analysis in mind, allowing for periodic updating of parameters in response to real-time information from the system as it evolves over time \parencite[see e.g.][for treatments on realtime parametric estimation and system evolution]{SoderstromLjung1983,Ljung2017}. Such parameter updating allows the DSS to be used by individual miners, to assist in their own economic policy over time. Since miners must be incentivized to provide storage optimally given their cost structure, decisions regarding e.g. storage provision, sector termination etc. can be informed by the DSS as it provides a range of possible actions that are incentive compatible. Moreover, miners can use the DSS as an `early warning system', to assess the effects of unforeseen, disruptive systemic shocks. Without the use of a DSS, system shocks must be attended to as they arrive (`on-the-fly'), resulting in both lost time and large deadweight losses as repair strategies are attempted before it is decided that (say) a code fork is optimal.

For both of these project objectives, the DSS acts as a \textit{guide} to the decisions of both governance stakeholders (in the case of parameter setting and updating) and individual miners (in the case of incentivization and shock evaluation). It does not replace decision-making, nor does it automatically engage with the system itself to provide auto-correcting features. Rather, it acts as a `digital twin' of the system, that can be demonstrated to faithfully replicate those salient features that impact both parameter setting and system evolution over time.

\subsection{The Parameter and Metric Spaces}

% TODO commented out for new Filecoin Documentation
%\todo{This section is extrapolated from the \href{https://github.com/BlockScience/filecoin/blob/devel/misc/From\%20High\%20Dimensional\%20Data\%20to\%20Insights.md}{From High Dimensional Data to Insights} reference document.}

In order to formalize the cryptoeconomic system the sets of control and environmental parameters, and the associated output metrics, must be defined. These definitions fulfill two requirements:

\begin{enumerate}
    \item the parameter sets must be \textit{rich} enough to encompass the system objectives, allowing for a system designer to decide whether or not one or more objectives are fulfilled, and
    \item the parameter sets must be \textit{simple} enough to feasibly implement as a software DSS, capturing the salient features without becoming computationally intractable.
\end{enumerate}

Deriving the balance between these two requirements is part of the DSS implementation process: by creating incremental versions of the implementation and tracking the resulting outcomes, a partition of the relevant system parameters (and functions of parameters) can be performed. In addition, \textit{ex ante} design hypotheses regarding (for example) different partitions of these parameters can be tested rather than assumed, ensuring that the DSS is not developed under a set of restrictions that simply fulfills expectations that have (intentionally or unintentionally) been `hard coded' to begin with. 

The \cadcad DSS implementation achieves this balance by partitioning a larger (and potentially unknown) high-dimensional parameter space $\mathcal{P}$ into three (mutually exclusive) subsets:\footnote{We identify a subset of system parameters with output metrics in what follows, but in general the metrics are themselves functions of system parameters.}
\begin{enumerate}
    \item a set of \textbf{control parameters}, $\mathcal{P}_c$;
    \item a set of \textit{known} exogenous or \textbf{environmental parameters} $\mathcal{P}_e$;
    \item a set of \textit{unknown} environmental parameters $\mathcal{P}_u$.
\end{enumerate}
In what follows we shall assume that $\mathcal{P}_u = \emptyset$, i.e. that all relevant environmental parameters that determine the optimal values of the control parameters are known. Although this appears to be a restrictive assumption, in practice this is relaxed by admitting a probability distribution over known environmental factors that collects what is unknown and thus treats one or more environmental factors as one or more random variables. This is a standard approach commonly adopted to allow for the impact of unknown external factors in decision-making \parencite[e.g. Bayesian updating, cf.  ][]{CyertDeGroot1987} and in classification \parencite[e.g. Machine Learning, cf. ][]{Murphy2012}.

Thus, in practice $\mathcal{P} = \mathcal{P}_c \cup \mathcal{P}_e$. A generic vector of control parameters will be denoted in what follows by $p_c \in \mathcal{P}_c$, while a generic environmental parameter vector will be given by $p_e \in \mathcal{P}_e$.

Finally, the set of key performance indicators (KPIs) is assumed to depend upon the set of parameters $\mathcal{P}$, but may be functions of these parameters in addition to other structural variables that may be fixed \textit{a priori}.