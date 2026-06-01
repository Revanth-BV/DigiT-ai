# ==========================================
# DIGIT REFLECTION MEMORY ENGINE
# ==========================================

def generate_reflection_memory(
    thoughts
):

    if not thoughts:

        return None

    categories = [

        t.get("category")

        for t in thoughts
    ]

    ambition_count = categories.count(
        "ambition"
    )

    emotional_count = categories.count(
        "emotional"
    )

    reflection_count = categories.count(
        "reflection"
    )

    if ambition_count >= 3:

        return {

            "reflection":
            "Long-term achievement appears central to the user's identity.",

            "confidence":
            0.8
        }

    if emotional_count >= 3:

        return {

            "reflection":
            "The user may be experiencing sustained emotional pressure.",

            "confidence":
            0.75
        }

    if reflection_count >= 3:

        return {

            "reflection":
            "The user demonstrates a strong tendency toward self-reflection.",

            "confidence":
            0.8
        }

    return None