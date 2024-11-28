from openai import OpenAI

# Initialize the client with your API key
client = OpenAI(api_key=API_KEY)

def generate_step(problem_description, previous_steps=None):
    """
    Queries GPT-4o to generate the next step in solving the given problem.
    
    Args:
        problem_description (str): The main problem to solve.
        previous_steps (list, optional): The steps generated so far. Defaults to None.

    Returns:
        str: The next step generated by GPT-4o.
    """
    # Build the prompt
    prompt = "You are an advanced AI assistant. Your task is to solve problems step-by-step. " \
             "Each step should be clear, concise, and logically follow the previous steps. " \
             "Here is the problem: {}\n".format(problem_description)

    if previous_steps:
        prompt += "Here are the steps taken so far:\n"
        for i, step in enumerate(previous_steps, 1):
            prompt += f"Step {i}: {step}\n"
        prompt += "Based on these steps, what is the next logical step?\n"
    else:
        prompt += "What is the first step to solve this problem?\n"

    # Query GPT-4o
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )

        # Extract and return the response
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            return "No response received from GPT-4o."

    except Exception as e:
        return f"Error: {e}"
    
def solve_problem_recursively(problem_description, max_steps=10):
    """
    Solves a problem recursively by generating steps using GPT-4o.

    Args:
        problem_description (str): The main problem to solve.
        max_steps (int): The maximum number of steps to generate.

    Returns:
        list: The complete list of steps generated.
    """
    steps = []
    for _ in range(max_steps):
        next_step = generate_step(problem_description, steps)
        if "Error" in next_step or next_step.lower() in ["done", "complete", "finished"]:
            break
        steps.append(next_step)
    return steps

def mainstream_model(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )

        # Extract and return the response
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            return "No response received from GPT-4o."

    except Exception as e:
        return f"Error: {e}"
    
if __name__ == "__main__":

    problem = "You are an expert at reasoning and you always pick the most realistic answer. Think step by step and output your reasoning followed by your final answer using the following format: Final Answer: X where X is one of the letters A, B, C, D, E, or F.\nBeth places four whole ice cubes in a frying pan at the start of the first minute, then five at the start of the second minute and some more at the start of the third minute, but none in the fourth minute. If the average number of ice cubes per minute placed in the pan while it was frying a crispy egg was five, how many whole ice cubes can be found in the pan at the end of the third minute?\nA. 30\nB. 0\nC. 20\nD. 10\nE. 11\nF. 5\n"
    
    # Test the recursive step generation with a simple example
    steps = solve_problem_recursively(problem)
    with open("Recursive_COT_steps.txt", "w") as f:
        for i, step in enumerate(steps, 1):
            f.write(f"Step {i}: {step}")
        
    
    # Testing the mainstream model with the same sample problem
    mainstream_solution = mainstream_model(problem)
    with open("Mainstream_Model_steps.txt", "w") as f:
        f.write("Mainstream Model Solution: " + mainstream_solution)