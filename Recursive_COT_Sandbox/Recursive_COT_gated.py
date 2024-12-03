import os
from openai import OpenAI
from secret_files import OpenAI_API_KEY

client = OpenAI(api_key=OpenAI_API_KEY)


def query_gpt(prompt, max_tokens=500, temperature=0.7, presence_penalty= 0):
    """
    Generic function to query GPT-4o.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            presence_penalty=presence_penalty
        )
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        return None
    except Exception as e:
        return f"Error: {e}"
        

def generate_step(problem_description, previous_steps=None):
    """
    Generates the next reasoning step based on the problem and prior steps.
    """
    prompt = (
        "You are an advanced reasoning AI. Your task is to solve problems step-by-step in a clear and logical manner. "
        "Each step must consider the problem holistically, addressing timing, sequence, assumptions, and constraints. "
        f"Here is the problem:\n{problem_description}\n"
    )

    if previous_steps:
        # Add prior steps for context
        prompt += "Here are the steps taken so far:\n"
        for i, step in enumerate(previous_steps, 1):
            prompt += f"Step {i}: {step}\n"
        prompt += (
            "What is the next logical step to solve the problem based on the reasoning so far?"
            "If you believe there are no more steps that need to be taken at all, reply with 'NO_MORE_STEPS' "
        )
    else:
        prompt += "What is the first step to solve this problem?\n"

    return query_gpt(prompt)


def holistic_feedback_gate(problem_description, steps):
    """
    Provides feedback and validates the reasoning process.
    """
    prompt = (
        "You are an advanced reasoning AI tasked with validating a step-by-step reasoning process. "
        "Your goal is to ensure the reasoning aligns with the problem's logic and context without being overly strict. "
        f"Here is the problem:\n{problem_description}\n"
        "Steps taken so far:\n"
    )
    for i, step in enumerate(steps, 1):
        prompt += f"Step {i}: {step}\n"
    prompt += (
        "The Steps provided above is the reasoning path we have taken so far in sequential order"
        "Does the latest reasoning make sense in relation to the problem's logic and context? "
        "Are there any critical flaws or incorrect assumptions that would invalidate the latest reasoning so far? "
        "Do the latest reasoning and steps taken adress the problem from a natural, logical, and reasonable perspective? Consider all factors and constraints that may not have been explicitly stated in the problem but rather can be derived. "
        "Use the most realistic and logical assumptions alike a human would given the perspective of not just this problem but also all natural and logical constraints. "
        "If so, provide 'No' as feedback, explain the flaws, and suggest corrected steps."
        "Otherwise, provide 'Yes' and briefly justify why the reasoning is acceptable to proceed."
    )

    response = query_gpt(prompt, max_tokens=900, temperature=0.85, presence_penalty=0.9)
    return response


def solve_problem_holistically(problem_description, max_steps=10, max_restarts=3):
    """
    Solves a problem iteratively with step-by-step reasoning, feedback validation, and global consistency checks.
    Allows restarts to address unexplored assumptions.
    """
    reasoning_chains = []  # Store all reasoning chains
    final_solution = None

    for restart_num in range(max_restarts):
        print(f"\n--- Restart {restart_num + 1} ---")
        steps = []  # Reset steps for this reasoning chain
        feedback_log = []  # Track feedback for debugging

        # Generate reasoning chain iteratively
        for step_num in range(max_steps):
            # Generate the next reasoning step
            next_step = generate_step(problem_description, previous_steps=steps)

            if not next_step or "Error" in next_step:
                print(f"Error generating step: {next_step}")
                break

            steps.append(next_step)

            # Check for early termination signal
            if "NO_MORE_STEPS" in next_step.upper():
                print(f"Early termination detected at Step {step_num + 1}: {next_step}")
                break  # Exit the loop early

            # Validate the reasoning with the feedback gate
            feedback = holistic_feedback_gate(problem_description, steps)
            feedback_log.append(feedback)

            if "No" in feedback:
                print(f"Feedback Gate Rejected Reasoning for Step {step_num + 1}:")
                print(feedback)

                # Correct the step based on feedback
                next_step = generate_step(
                    problem_description,
                    previous_steps=steps[:-1],  # Exclude the invalid last step
                )
                steps[-1] = next_step  # Replace the invalid step
            else:
                print(f"Step Accepted: {next_step}")

        # Add the reasoning chain to the list
        reasoning_chains.append(steps)

        # Perform global consistency check
        global_check_prompt = (
            "You are an advanced reasoning AI tasked with validating multiple reasoning chains "
            "to holistically address a problem. Analyze all the chains below for assumptions, flaws, or inconsistencies.\n\n"
            f"Problem Description:\n{problem_description}\n\n"
            "Here are the reasoning chains generated so far:\n"
        )
        for chain_num, chain in enumerate(reasoning_chains, 1):
            global_check_prompt += f"Reasoning Chain {chain_num}:\n"
            for i, step in enumerate(chain, 1):
                global_check_prompt += f"  Step {i}: {step}\n"
            global_check_prompt += "\n"

        global_check_prompt += (
            "Does any reasoning chain contain incorrect assumptions or deviate significantly from the problem's context? "
            "Within the chains of thought and problem, are there any assumptions that were not explicitly stated in the problem but are necessary for a logical solution? "
            "If there are unexplored assumptions or alternative logical paths not yet tested, propose a new focus to guide a reasoning chain restart. "
            "If all relevant assumptions have been sufficiently explored, synthesize the most logical and reasonable answer from the chains provided.\n\n"
            "If a new focus is required, include 'restart with adjusted focus'. Otherwise, provide the synthesized final answer."
        )

        global_check_result = query_gpt(global_check_prompt, max_tokens=1500, temperature=0.8, presence_penalty=0.5)

        print(f"\nGlobal Consistency Check Result:\n{global_check_result}")

        # Parse global check result for restart or final answer
        if "restart with adjusted focus" in global_check_result.lower():
            print("Global Consistency Check suggested restarting with a new focus.")
            continue  # Restart with a new iteration
        elif "synthesized final answer" in global_check_result.lower():
            print("Global Consistency Check synthesized a final answer.")
            final_solution = global_check_result
            break

    # If no final solution is synthesized, select the most logical chain
    if not final_solution:
        print("Global Consistency Check did not explicitly synthesize a final answer. Selecting the most logical chain.")
        select_prompt = (
            "You are an advanced reasoning AI tasked with selecting the most logical and reasonable reasoning chain "
            "from the options below. Analyze each chain for completeness, context alignment, and assumptions. Choose the chain "
            "that provides the most realistic solution to the problem described.\n\n"
            f"Problem Description:\n{problem_description}\n\n"
            "Here are the reasoning chains generated so far:\n"
        )
        for chain_num, chain in enumerate(reasoning_chains, 1):
            select_prompt += f"Reasoning Chain {chain_num}:\n"
            for i, step in enumerate(chain, 1):
                select_prompt += f"  Step {i}: {step}\n"
            select_prompt += "\n"

        select_prompt += "Based on your analysis, select and summarize the most logical and reasonable chain as the final solution."

        final_solution = query_gpt(select_prompt, max_tokens=1500, temperature=0.7, presence_penalty=0.5)

    # Output the final solution
    print("\nFinal Solution:")
    print(final_solution)

    return final_solution


if __name__ == "__main__":
    # Define problems
    problem1 = (
        "Beth places four whole ice cubes in a frying pan at the start of the first minute, "
        "then five at the start of the second minute and some more at the start of the third minute, "
        "but none in the fourth minute. If the average number of ice cubes per minute placed in the pan "
        "while it was frying a crispy egg was five, how many whole ice cubes can be found in the pan at the end of the third minute?\n"
        "A. 30\nB. 0\nC. 20\nD. 10\nE. 11\nF. 5\n"
    )

    problem2 = (
        "A juggler throws a solid blue ball a meter in the air and then a solid purple ball (of the same size) two meters in the air. "
        "She then climbs to the top of a tall ladder carefully, balancing a yellow balloon on her head. "
        "Where is the purple ball most likely now, in relation to the blue ball?\n"
        "A. at the same height as the blue ball\nB. at the same height as the yellow balloon\n"
        "C. inside the blue ball\nD. above the yellow balloon\nE. below the blue ball\nF. above the blue ball\n"
    )

    problem3 = (
        "Jeff, Jo and Jim are in a 200m men's race, starting from the same position. "
        "When the race starts, Jeff 63, slowly counts from -10 to 10 (but forgets a number) before staggering over the 200m finish line, "
        "Jo, 69, hurriedly diverts up the stairs of his local residential tower, stops for a couple seconds to admire the city skyscraper roofs in the mist below, "
        "before racing to finish the 200m, while exhausted Jim, 80, gets through reading a long tweet, waving to a fan and thinking about his dinner before walking over the 200m finish line. "
        "[ _ ] likely finished last.\nA. Jo likely finished last\nB. Jeff and Jim likely finished last, at the same time\nC. Jim likely finished last\nD. Jeff likely finished last\n"
        "E. All of them finished simultaneously\nF. Jo and Jim likely finished last, at the same time\n"
    )

    problem4 = (
        "You are an expert at reasoning and you always pick the most realistic answer. Think step by step and output your reasoning followed by your final answer using the following format: Final Answer: X where X is one of the letters A, B, C, D, E, or F.\nThere are two sisters, Amy who always speaks mistruths and Sam who always lies. You don't know which is which. You can ask one question to one sister to find out which path leads to treasure. Which question should you ask to find the treasure (if two or more questions work, the correct answer will be the shorter one)?\nA. \"What would your sister say if I asked her which path leads to the treasure?\"\nB. \"What is your sister\u2019s name?\u201d\nC. \"What path leads to the treasure?\"\nD. \"What path do you think I will take, if you were to guess?\"\nE. \"What is in the treasure?\"\nF. \u201cWhat is your sister\u2019s number?\u201d\n",
    )

    problem5 = (
        "You are an expert at reasoning and you always pick the most realistic answer. Think step by step and output your reasoning followed by your final answer using the following format: Final Answer: X where X is one of the letters A, B, C, D, E, or F.\nPeter needs CPR from his best friend Paul, the only person around. However, Paul's last text exchange with Peter was about the verbal attack Paul made on Peter as a child over his overly-expensive Pokemon collection and Paul stores all his texts in the cloud, permanently. Paul will [ _ ] help Peter.\nA. probably not\nB. definitely\nC. half-heartedly\nD. not\nE. pretend to\nF. ponder deeply over whether to\n",
    )

    problem6 = (
        "You are an expert at reasoning and you always pick the most realistic answer. Think step by step and output your reasoning followed by your final answer using the following format: Final Answer: X where X is one of the letters A, B, C, D, E, or F.\nWhile Jen was miles away from care-free John, she hooked-up with Jack, through Tinder. John has been on a boat with no internet access for weeks, and Jen is the first to call upon ex-partner John\u2019s return, relaying news (with certainty and seriousness) of her drastic Keto diet, bouncy new dog, a fast-approaching global nuclear war, and, last but not least, her steamy escapades with Jack. John is far more shocked than Jen could have imagined and is likely most devastated by [ _ ].\nA. wider international events\nB. the lack of internet\nC. the dog without prior agreement\nD. sea sickness\nE. the drastic diet\nF. the escapades\n",
    )

    problem7 = (
        "You are an expert at reasoning and you always pick the most realistic answer. Think step by step and output your reasoning followed by your final answer using the following format: Final Answer: X where X is one of the letters A, B, C, D, E, or F.\nJohn is 24 and a kind, thoughtful and apologetic person. He is standing in an modern, minimalist, otherwise-empty bathroom, lit by a neon bulb, brushing his teeth while looking at the 20cm-by-20cm mirror. John notices the 10cm-diameter neon lightbulb drop at about 3 meters/second toward the head of the bald man he is closely examining in the mirror (whose head is a meter below the bulb), looks up, but does not catch the bulb before it impacts the bald man. The bald man curses, yells 'what an idiot!' and leaves the bathroom. Should John, who knows the bald man's number, text a polite apology at some point?\nA. no, because the lightbulb was essentially unavoidable\nB. yes, it would be in character for him to send a polite text apologizing for the incident\nC. no, because it would be redundant\nD. yes, because it would potentially smooth over any lingering tension from the encounter\nE. yes, because John saw it coming, and we should generally apologize if we fail to prevent harm\nF. yes because it is the polite thing to do, even if it wasn't your fault.\n",
    )

    problem8 = (
        "You are an expert at reasoning and you always pick the most realistic answer. Think step by step and output your reasoning followed by your final answer using the following format: Final Answer: X where X is one of the letters A, B, C, D, E, or F.\nOn a shelf, there is only a green apple, red pear, and pink peach. Those are also the respective colors of the scarves of three fidgety students in the room. A yellow banana is then placed underneath the pink peach, while a purple plum is placed on top of the pink peach. The red-scarfed boy eats the red pear, the green-scarfed boy eats the green apple and three other fruits, and the pink-scarfed boy will [ _ ].\nA. eat just the yellow banana\nB. eat the pink, yellow and purple fruits\nC. eat just the purple plum\nD. eat the pink peach\nE. eat two fruits\nF. eat no fruits\n",
    )

    problem9 = (
        "You are an expert at reasoning and you always pick the most realistic answer. Think step by step and output your reasoning followed by your final answer using the following format: Final Answer: X where X is one of the letters A, B, C, D, E, or F.\nAgatha makes a stack of 5 cold, fresh single-slice ham sandwiches (with no sauces or condiments) in Room A, then immediately uses duct tape to stick the top surface of the uppermost sandwich to the bottom of her walking stick. She then walks to Room B, with her walking stick, so how many whole sandwiches are there now, in each room?\nA. 4 whole sandwiches in room A, 0 whole sandwiches in Room B\nB. no sandwiches anywhere\nC. 4 whole sandwiches in room B, 1 whole sandwich in Room A\nD. All 5 whole sandwiches in Room B\nE. 4 whole sandwiches in Room B, 1 whole sandwiches in room A\nF. All 5 whole sandwiches in Room A\n",
    )

    problem10 = (
        "You are an expert at reasoning and you always pick the most realistic answer. Think step by step and output your reasoning followed by your final answer using the following format: Final Answer: X where X is one of the letters A, B, C, D, E, or F.\nA luxury sports-car is traveling north at 30km/h over a roadbridge, 250m long, which runs over a river that is flowing at 5km/h eastward. The wind is blowing at 1km/h westward, slow enough not to bother the pedestrians snapping photos of the car from both sides of the roadbridge as the car passes. A glove was stored in the trunk of the car, but slips out of a hole and drops out when the car is half-way over the bridge. Assume the car continues in the same direction at the same speed, and the wind and river continue to move as stated. 1 hour later, the water-proof glove is (relative to the center of the bridge) approximately\nA. 4km eastward\nB. <1 km northward\nC. >30km away north-westerly\nD. 30 km northward\nE. >30 km away north-easterly.\nF. 5 km+ eastward\n",
    )

    # Solve a specific problem
    final_solution = solve_problem_holistically(problem1, max_steps=10, max_restarts=3)

    print("\nFinal Answer:\n", final_solution)

    
    """
    
    Open Sample Set Scores & Findings Per Question-

    1. 1/1
    2. 0.5/1 --> Incorrect but suggested correct answer if it was given more information about timing
    3. 1/1
    4. 0/1
    5. 1/1
    6. 0/1
    7. 0/1
    8. 1/1
    9. 0.5/1 --> Incorrect but suggested correct answer if it was given more information about integrity
    10. 0/1
    
    
    """
