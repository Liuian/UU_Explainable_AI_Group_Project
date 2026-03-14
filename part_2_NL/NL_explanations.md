# Natural Language Explanations Group 12
**Kumkum Singh Kumari**
**Pepijn Stoop**
**Yi-An Liu**
**Yiquan Hu**

## Explanation 1
You are the end-user of an AI agent. Consider the following situation. You instruct the agent to achieve the goal of having coffee, and that you prefer price over time and time over quality. The agent knows that it's prohibited to pay at the shop,  the staff card is available, you own the card, the colleague is available and Ann is in the office. To achieve the goal, the agent does the following actions: Get your own staff card, go to the kitchen, and get coffee from the kitchen. When you ask the agent to explain you why it does not pay at the shop, the agent gives you the following explanation:

The agent's goal was to have coffee. The agent skipped paying at the shop because you were not allowed to pay at the shop.

<div style="page-break-after: always;"></div>
## Explanation 2
You are the end-user of an AI agent. Consider the following situation. You instruct the agent to achieve the goal of having coffee, and you prefer quality over price and price over time. The agent knows that there is no prohibition, and it believes that the staff card is available and you own a card. To achieve the goal, the agent does the following actions: Get your own staff card, go to the kitchen, and get coffee from the kitchen. When you ask the agent to explain why it gets coffee from the kitchen, the agent gives you the following explanation:

The agent's goal was to get coffee. The agent got coffee in the kitchen because a staff card was available. The agent obtained your own card because you owned a card. The agent got coffee in the kitchen because you had a card available. The agent didn't get coffee from Ann's office because Ann was not present in her office. The agent didn't get coffee from the shop because you did not have enough money. The agent didn't obtain someone else's card because the colleague was not available to lend a card.



<div style="page-break-after: always;"></div>
## Explanation 3
You are the end-user of an AI agent. Consider the following situation. You instruct the agent to achieve the goal of having coffee, and you prefer quality over price and price over time. The agent knows that there is no prohibition, and it believes that you have money and Ann is in the office. To achieve the goal, the agent does the following actions: Go to the coffee shop, pay at the shop, and get coffee from the shop. When you ask the agent to explain why it gets coffee from the shop, the agent gives you the following explanation:

The agent's goal was to get coffee. The agent got coffee from the shop because you had enough money. Given the agent's priorities, the agent chose getting coffee from the shop over getting coffee from Ann's office because it was better in terms of time. The agent paid at the shop because you had enough money. The agent got coffee from the shop. The agent didn't get coffee in the kitchen because a staff card was not available.

<div style="page-break-after: always;"></div>
## Explanation 4
You are the end-user of an AI agent. Consider the following situation. You instruct the agent to achieve the goal of having coffee, and you prefer quality over price and price over time. The agent knows that it is prohibited to go to Ann’s office, and it believes that a staff card is available, you own a card, the colleague is available, you have money, and Ann is in the office. To achieve the goal, the agent does the following actions: Go to the coffee shop, pay at the shop, and get coffee from the shop. When you ask the agent to explain why it pays at the shop, the agent gives you the following explanation:

The agent's goal was to get coffee. The agent got coffee from the shop because you had enough money. Given the agent's priorities, the agent chose getting coffee from the shop over getting coffee in the kitchen because it was better in terms of time. The agent paid at the shop because you had enough money. The agent skipped getting coffee from Ann's office because you were not allowed to go to Ann's office.

<div style="page-break-after: always;"></div>
## Explanation 5
You are the end-user of an AI agent. Consider the following situation. You instruct the agent to achieve the goal of having coffee, and you prefer time over quality and quality over price. The agent knows that it is prohibited to pay at the shop, and it believes that a staff card is available, you own a card, the colleague is available, and you have money. To achieve the goal, the agent does the following actions: Get your own staff card, go to the kitchen, and get coffee from the kitchen. When you ask the agent to explain why it  goes to the kitchen, the agent gives you the following explanation:

The agent's goal was to get coffee. The agent got coffee in the kitchen because a staff card was available. The agent obtained your own card because you owned a card. Given the agent's priorities, the agent chose obtaining your own card over obtaining someone else's card because it was better in terms of time. The agent skipped getting coffee from the shop because you were not allowed to pay at the shop. The agent didn't get coffee from Ann's office because Ann was not present in her office.

