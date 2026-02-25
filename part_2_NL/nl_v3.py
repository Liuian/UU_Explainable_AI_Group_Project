# Example of explanation from assignment
explanations = [
                [['C', 'getKitchenCoffee', ['staffCardAvailable']], ['F', 'getAnnOfficeCoffee', ['AnnInOffice']], ['F', 'getShopCoffee', ['haveMoney']], ['C', 'getOwnCard', ['ownCard']], ['F', 'getOthersCard', ['colleagueAvailable']], ['P', 'getOwnCard', ['ownCard']], ['P', 'getCoffeeKitchen', ['haveCard', 'atKitchen']], ['D', 'getKitchenCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [0, 1, 2]]]],
                [['C', 'getShopCoffee', ['haveMoney']], ['F', 'getKitchenCoffee', ['staffCardAvailable']], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getAnnOfficeCoffee', [2.0, 0.0, 6.0]], ['P', 'payShop', ['haveMoney']], ['P', 'getCoffeeShop', ['atShop']], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [0, 1, 2]]]],
                [['C', 'getShopCoffee', ['haveMoney']], ['V', 'getShopCoffee', [0.0, 3.0, 9.0], '>', 'getKitchenCoffee', [5.0, 0.0, 3.0]], ['N', 'getAnnOfficeCoffee', 'P(gotoAnnOffice)'], ['P', 'payShop', ['haveMoney']], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [0, 1, 2]]]],
                [['C', 'getKitchenCoffee', ['staffCardAvailable']], ['F', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getShopCoffee', 'P(payShop)'], ['C', 'getOwnCard', ['ownCard']], ['V', 'getOwnCard', [0.0, 0.0, 0.0], '>', 'getOthersCard', [0.0, 0.0, 2.0]], ['P', 'getOwnCard', ['ownCard']], ['L', 'gotoKitchen', '->', 'getCoffeeKitchen'], ['D', 'getKitchenCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [1, 2, 0]]]]



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
    'getOwnCard': "obtained your own card",
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
    "ownCard": "you owned a card",
    "colleagueAvailable": "the colleague was available to lend a card",
    "haveCard": "you had a card available",
    "staffCardAvailable": "a staff card was available",
    "haveMoney": "you had enough money",
    "AnnInOffice": "Ann was present in her office",
    "havePod": "you had a coffee pod",
    "paidShop": "you had paid at the shop"
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
        return f"you were not allowed to {actions_text[0]}" if len(actions_text) == 1 \
            else f"you were not allowed to {', '.join(actions_text[:-1])}, or {actions_text[-1]}"
    elif norm_type == 'O':
        return f"you were supposed to {actions_text[0]}" if len(actions_text) == 1 \
            else f"you were supposed to {', '.join(actions_text[:-1])}, or {actions_text[-1]}"

"""
Function to replace past tenses with the gerund to fit grammar structure for N items
"""
def past_to_gerund(past_text):
    replacements = {
        'got ': 'getting ',
        'obtained ': 'obtaining ',
        'paid ': 'paying ',
        'went ': 'going ',
        'own ': 'owning ',
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

    # Determine overall goal (last D)
    overall_goal = None
    for f in reversed(explanation):
        if f[0] == 'D' and isinstance(f[1], str):
            overall_goal = action_names_present.get(f[1], f[1])
            break

    # Turn overall goal into natural English part
    if overall_goal:
        story.append(f"The agent's goal was to {overall_goal}.")

    # Extract priorities
    # for f in explanation:
    #     if f[0] == 'U':
    #         criteria, priorities = f[1][0], f[1][1]
    #         sorted_criteria = [criteria[i] for i in priorities]
    #         first_priority = sorted_criteria[0]
    #         rest_priority = sorted_criteria[1:]
    #         if len(sorted_criteria) == 2:
    #             story.append(f"The agent valued {first_priority} the most, followed by {rest_priority[0]}")
    #         else:
    #             story.append(f"The agent valued {first_priority} the most, followed by {', '.join(rest_priority[:-1])} and {rest_priority[-1]}.")
    #


    # Extract N actions to merge all N sentences for explaining
    n_explanation = {}
    f_explanation = []
    non_nf_explanation = []

    for f in explanation:
        if f[0] == 'N':
            alt, norm_code = f[1], f[2]
            n_explanation.setdefault(norm_code, []).append(alt)
        elif f[0] == 'F':
            f_explanation.append(f)
        else:
            non_nf_explanation.append(f)

    # Process explanation lines
    for f in non_nf_explanation:
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
                    f"Given the agent's priorities, the agent chose "
                    f"{past_to_gerund(action_names_past.get(chosen, chosen))} over "
                    f"{past_to_gerund(action_names_past.get(other, other))} because "
                    f"it was better in terms of {reason}."
                )

    # For all Skipped actions, only explain the reason once
    for norm_code, alts in n_explanation.items():
        alts_gerund = [past_to_gerund(action_names_past.get(alt, alt)) for alt in alts]
        if len(alts_gerund) == 1:
            skipped_actions = alts_gerund[0]
        else:
            skipped_actions = ", ".join(alts_gerund[:-1]) + " and " + alts_gerund[-1]
        story.append(f"The agent skipped {skipped_actions} because {norm_to_english(norm_code)}.")

    # Map F parts to their respective natural language parts
    for f in f_explanation:
        if len(f) > 1 and isinstance(f[1], str):
            action_text = action_names_present.get(f[1], f[1])
        else:
            continue

        preconds = f[2]
        meaningful = [pc for pc in preconds if pc in negated_precondition_mapping]
        if meaningful:
            text = " and ".join(negated_precondition_mapping[pc] for pc in meaningful)
            story.append(f"The agent didn't {action_text} because {text}.")
        else:
            story.append(f"The agent didn't {action_text}.")

    return " ".join(story)
# Run the code and print final explanation
with open("nl_output_5inputs_v3.txt", "w", encoding="utf-8") as f:
    for idx, explanation in enumerate(explanations, 1):
        nl_story = generate_nl_explanation(explanation)
        f.write(f"{idx}.explanation:\n{explanation}\nstory:\n{nl_story}\n\n\n")

