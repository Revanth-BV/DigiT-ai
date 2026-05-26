# ==========================================
# DIGIT REFLECTION ENGINE
# ==========================================

def generate_reflection(
    memories
):

    if not memories:

        return None

    recent = memories[-3:]

    combined = " ".join(recent)

    if "stress" in combined:

        return (
            "You seem mentally overloaded lately."
        )

    if "goal" in combined:

        return (
            "You’ve been thinking a lot about growth recently."
        )

    return None