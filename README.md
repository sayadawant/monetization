# Monetization strategies for Shepherd

Below I'm presenting three monetization strategies (beyond potential Node rewards) for the Shepherd agent and corresponding sub-agents Kairos, Pythia, Pan, and Zenodotos.

1. ## Donation/offering protocol

Shepherd sub-agents, where applicable, will feature a donation protocol. Before and/or after performing tasks, the system will ask for mandatory or optional donations to the Shepherd treasury when interacting with agents and requesting task performance.  
For example:

* Asking Kairos for guidance on purpose, career change, or new opportunities – a donation option is presented after free advice.  
* Asking Pythia for oracle duties and revelations – a donation is mandatory to access Pythia; the donation option is presented after sharing guidance.  
* Querying Zenodotos for History of Alex snippets – a donation option is presented after free advice.

Functional requirements

* Hot XPR protocol supporting a wallet with PFT acceptance capabilities to which users can donate  
* Tie into agents with specific triggers, maximizing conversion rate (e.g., force donation after providing a query)  
* Prompt users to send PFT to the treasury wallet address with a randomly generated memo string  
* Use a transaction checker script that runs asynchronously with the following functionality:  
  1. Polls the XRP Ledger for incoming transactions to a specified wallet  
  2. Filters for RippleState changes that transfer PFT tokens  
  3. Verifies that transaction amounts meet minimum requirements  
  4. Checks that transaction memos contain the appropriate identifier  
  5. Returns transaction verification status after polling

This functionality is already demonstrated in the Pythia v0.1 implementation.

Script for verifying transactions: [transaction check](https://github.com/sayadawant/monetization/blob/main/pft_transact_check.py)

2. ## Premium tier tailored research and user report

At a stage of the project where sub-agents are developed and tested—demonstrating real value creation for users—a Shepherd paid tier functionality will be introduced with the following user and transaction flow:

* The user asks for comprehensive Shepherd guidance to help them orient in the PFT network and generally in a post-AGI world.  
* Shepherd asks a) three to five context-assisting questions to assess the user's need, b) optionally asks for links to a Task Node context file, and c) offers the option for the user to attach additional files.  
* Shepherd processes all inputs, and based on the summary, interacts with all four sub-agents to provide guidance based on their output:  
  *  Kairos helps users orient by finding their purpose and best utilization of their skills in the PFT network  
  * Zenodotos offers selected quotes to support and motivate the user to engage with the PFT network and build ideological and mission alignment  
  *  Pan shows options for onboarding, node engagement, and agent choices  
  *  Finally, Pythia provides esoteric/mystical interpretation and advice on direction options  
* A final report of 3-5 pages in exportable format is generated as a "starter kit" for the user to get started on their journey toward reorienting to a post-AGI reality.  
* Short report snippets are made available for free.  
* The full report is available for Y (TBD) PFT, with user instructions on depositing to a wallet address and verifying with PFT Transact Check:

[transaction check](https://github.com/sayadawant/monetization/blob/main/pft_transact_check.py)

3. ## Affiliate referral revenue generation

For Pan, the sub-agent focused on presenting PFT-related opportunities such as earning tokens and spending tokens to reach specific goals, an affiliate model type of monetization is a good fit for specific advice on earning tokens, investment opportunities for trading agents, and other spending opportunities.  
As a first iteration and demo, we can conceive the following user process and token flow:

* Pan, during user interactions, recommends our other sub-agent, Pythia, for mystical advice and techno-prophecies for further guidance.  
* Pan asks the user to invoke Pythia with a specific added ID, e.g., \!pythia refer-pan.  
* Pythia is modified in such a way that:  
  * A referral processing module identifies the referring agent from the invoking command parameter "refer-".  
  * It stores the referral parameter in the user database, attaching it to the user.  
  * Whenever a donation is made by the user, it pulls available wallet data for the referring agent, in this case "pan".  
  * After the donation transaction is verified, it initiates a transaction with X% (e.g., x=20) of the donation amount paid out to "pan" as a finder's fee.  
* This functionality can be built in a modular way and developed into a standard on the PFT network, utilised in agent-to-agent referral revenue share. 

In a future state, depending on the development of the PFT blockchain and user interface alignment, an automated way of redirecting users to agents from Pan's (and other agent’s) conversation and functions can be explored for automated attribution of user referrals.

Code example for Agent implementation of referral payment: [agent demo](https://github.com/sayadawant/monetization/blob/main/referral_agent_demo.py)


