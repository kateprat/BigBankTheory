import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def dict_to_text(d, label="Document"):
    lines = [f"{label}:"]
    for k, v in d.items():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)


def check_consistency_with_groq(dict1, dict2, system_instructions=None):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
    You are a data consistency checker.

    Given two sets of information about a person, identify any inconsistencies or contradictions.
    Be specific — point out mismatched names, addresses, document IDs, etc.
    If everything matches, respond with confirmation.

    {dict_to_text(dict1, 'Document A')}

    {dict_to_text(dict2, 'Document B')}
    """

    if not system_instructions:
        system_instructions = "You are a precise and helpful assistant that checks for data mismatches between two profiles."

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=512,
    )

    return response.choices[0].message.content
