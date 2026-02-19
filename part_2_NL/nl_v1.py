# Example of explanation from assignment 4
explanations = [
                [['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['N', 'getAnnOfficeCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['N', 'getAnnOfficeCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['N', 'getAnnOfficeCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['N', 'getAnnOfficeCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['P', 'payShop', ['haveMoney']], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['N', 'getAnnOfficeCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['P', 'payShop', ['haveMoney']], ['P', 'getCoffeeShop', ['atShop']], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['N', 'getAnnOfficeCoffee', 'P(gotoAnnOffice, gotoKitchen)'], ['P', 'payShop', ['haveMoney']], ['P', 'getCoffeeShop', ['atShop']], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],

                [['C', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getKitchenCoffee', 'P(gotoKitchen)'], ['F', 'getShopCoffee', ['haveMoney']], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getKitchenCoffee', 'P(gotoKitchen)'], ['F', 'getShopCoffee', ['haveMoney']], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getKitchenCoffee', 'P(gotoKitchen)'], ['F', 'getShopCoffee', ['haveMoney']], ['P', 'gotoAnnOffice', ['AnnInOffice']], ['D', 'getAnnOfficeCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getKitchenCoffee', 'P(gotoKitchen)'], ['F', 'getShopCoffee', ['haveMoney']], ['P', 'gotoAnnOffice', ['AnnInOffice']], ['D', 'getAnnOfficeCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getKitchenCoffee', 'P(gotoKitchen)'], ['F', 'getShopCoffee', ['haveMoney']], ['P', 'gotoAnnOffice', ['AnnInOffice']], ['P', 'getCoffeeAnnOffice', ['havePod', 'atAnnOffice']], ['D', 'getAnnOfficeCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getKitchenCoffee', 'P(gotoKitchen)'], ['F', 'getShopCoffee', ['haveMoney']], ['P', 'gotoAnnOffice', ['AnnInOffice']], ['P', 'getCoffeeAnnOffice', ['havePod', 'atAnnOffice']], ['D', 'getAnnOfficeCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],

                [['C', 'getShopCoffee', ['haveMoney']], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getKitchenCoffee', [5.0, 0.0, 5.0]], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getAnnOfficeCoffee', [2.0, 0.0, 6.0]], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getShopCoffee', ['haveMoney']], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getKitchenCoffee', [5.0, 0.0, 5.0]], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getAnnOfficeCoffee', [2.0, 0.0, 6.0]], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getShopCoffee', ['haveMoney']], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getKitchenCoffee', [5.0, 0.0, 5.0]], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getAnnOfficeCoffee', [2.0, 0.0, 6.0]], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getShopCoffee', ['haveMoney']], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getKitchenCoffee', [5.0, 0.0, 5.0]], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getAnnOfficeCoffee', [2.0, 0.0, 6.0]], ['P', 'payShop', ['haveMoney']], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]],
                [['C', 'getShopCoffee', ['haveMoney']], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getKitchenCoffee', [5.0, 0.0, 5.0]], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getAnnOfficeCoffee', [2.0, 0.0, 6.0]], ['P', 'payShop', ['haveMoney']], ['P', 'getCoffeeShop', ['atShop']], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]
               ]
"""
These dictionaries of actions and preconditions consists of the variables from
the assignment 4 explanations translated into English natural language parts of
sentences.  
"""
# Names of translated actions in past tense
action_names_past = {
    'getKitchenCoffee': "got coffee in the kitchen",
    'getAnnOfficeCoffee': "got coffee from Ann's office",
    'getShopCoffee': "got coffee from the shop",
    'getOwnCard': "obtained their own card",
    'getOthersCard': "obtained someone else's card",
    'getCoffeeKitchen': "got coffee in the kitchen",
    'getCoffeeShop': "got coffee from the shop",
    'getCoffee': "got coffee",
    'getStaffCard': "got a staff card",
    'gotoKitchen': "went to the kitchen",
    'gotoAnnOffice': "went to Ann's office",
    'gotoShop': "went to the shop",
    'getPod': "obtained a coffee pod",
    'payShop': "paid at the shop"
}

# Function to map tense of action variables into present tense for F and D items
action_names_present = {k: v.replace("got", "get").replace("obtained", "obtain").replace("paid", "pay").replace("went", "go")
                        for k, v in action_names_past.items()}

# Precondition variable names mapped to natural English sentence parts
# atShop, atAnnOffice, atKitchen excluded since they are not valuable
precondition_mapping = {
    "ownCard": "they already had their own card",
    "colleagueAvailable": "a colleague was available to lend a card",
    "haveCard": "they had a card available",
    "staffCardAvailable": "a staff card was available to them",
    "haveMoney": "they had enough money",
    "AnnInOffice": "Ann was present in her office",
    "havePod": "they had a coffee pod",
    "paidShop": "they had paid at the shop"
}

# Function to negate preconditions for F items
negated_precondition_mapping = {k: v.replace("were", "were not").replace("had", "did not have").replace("was", "was not")
                               for k, v in precondition_mapping.items()}

"""
Function to translate user norms (P or O) into natural English
"""
def norm_to_english(norm_code):
    norm_type = norm_code[0]
    actions_list = norm_code[norm_code.find("(")+1:norm_code.find(")")].split(",")
    actions_text = [action_names_present.get(a.strip(), a.strip()) for a in actions_list]

    if norm_type == 'P':
        return f"they were not allowed to {actions_text[0]}" if len(actions_text) == 1 \
            else f"they were not allowed to {', '.join(actions_text[:-1])}, or {actions_text[-1]}"
    elif norm_type == 'O':
        return f"they were supposed to {actions_text[0]}" if len(actions_text) == 1 \
            else f"they were supposed to {', '.join(actions_text[:-1])}, or {actions_text[-1]}"

"""
Function to replace past tenses with the gerund to fit grammar structure for N items
"""
def past_to_gerund(past_text):
    replacements = {
        'got ': 'getting ',
        'obtained ': 'obtaining ',
        'paid ': 'paying ',
        'went ': 'going ',
    }
    for k, v in replacements.items():
        if past_text.startswith(k):
            return past_text.replace(k, v, 1)
    return past_text + "ing"


"""
Function to generate the full natural English story based on the explanation of 
assignment 4. Loops through the explanation to identify items (N, F, D etc.) and
replace their parts with natural English structures. 
"""
def generate_nl_explanation(explanation):
    story = []
    criteria, priorities = None, None

    # Extract priorities
    for f in explanation:
        if f[0] == 'U':
            criteria, priorities = f[1][0], f[1][1]

    # Determine overall goal (last D)
    overall_goal = None
    for f in reversed(explanation):
        if f[0] == 'D' and isinstance(f[1], str):
            overall_goal = action_names_present.get(f[1], f[1])
            break

    # Turn overall goal into natural English part
    if overall_goal:
        story.append(f"The agent's goal was to {overall_goal}.")

    # Process explanation lines
    for f in explanation:
        key = f[0]

        if len(f) > 1 and isinstance(f[1], str):
            if key in ['F', 'N']:
                action_text = action_names_present.get(f[1], f[1])
            else:
                action_text = action_names_past.get(f[1], f[1])
        else:
            continue

        preconds = f[2] if len(f) > 2 else []

        # Map C and P items to respective natural language parts
        if key in ['P', 'C']:
            meaningful = [pc for pc in preconds if pc in precondition_mapping]
            if meaningful:
                text = " and ".join(precondition_mapping[pc] for pc in meaningful)
                story.append(f"The agent {action_text} because {text}.")
            else:
                story.append(f"The agent {action_text}.")

        # Map F parts to their respective natural language parts
        elif key == 'F':
            meaningful = [pc for pc in preconds if pc in negated_precondition_mapping]
            if meaningful:
                text = " and ".join(negated_precondition_mapping[pc] for pc in meaningful)
                story.append(f"The agent failed to {action_text} because {text}.")
            else:
                story.append(f"The agent failed to {action_text}.")

        # Map N items to respective natural language parts
        elif key == 'N':
            alt, norm_code = f[1], f[2]
            alt_gerund = past_to_gerund(action_names_past.get(alt, alt))
            story.append(f"The agent skipped {alt_gerund} because {norm_to_english(norm_code)}.")

        # Determine mapping of user preferences and choose correct nl mapping
        elif key == 'V':
            chosen, other = f[1], f[4]
            chosen_costs, other_costs = f[2], f[5]

            if criteria and priorities:
                sorted_idx = sorted(range(len(priorities)), key=lambda i: -priorities[i])
                for idx2 in sorted_idx:
                    if chosen_costs[idx2] != other_costs[idx2]:
                        reason = criteria[idx2]
                        break
                else:
                    reason = criteria[0]

                # Append explanation of priorities agent
                story.append(
                    f"Given the agent's priorities, they chose to "
                    f"{action_names_past.get(chosen, chosen)} over "
                    f"{action_names_past.get(other, other)} because "
                    f"it was better in terms of {reason}."
                )

    return " ".join(story)



# Run the code and print final explanation
for explanation in explanations:
    nl_story = generate_nl_explanation(explanation)
    with open("nl_output_v1.txt", "a", encoding="utf-8") as f:
        f.write(f"explanation:\n{explanation}\nstory:\n{nl_story}\n\n\n")
print("Translated natural English story")
print(nl_story)