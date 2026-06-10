# ==========================================
# DIGIT REFLECTION ENGINE
# ==========================================

def generate_reflection(
    memories
):

    if not memories:

        return None

    recent = memories[-3:]

    texts = []

    for memory in recent:

        if isinstance(memory, dict):

            texts.append(
                memory.get("message", "")
            )

        else:

            texts.append(
                str(memory)
            )

    combined = " ".join(texts)

    if "stress" in combined:

        return (
            "You seem mentally overloaded lately."
        )

    if "goal" in combined:

        return (
            "You’ve been thinking a lot about growth recently."
        )

    return None