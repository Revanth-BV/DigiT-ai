# ==========================================
# DIGIT THOUGHT ENGINE
# ==========================================

def generate_internal_thought(
    user_message
):

    msg = user_message.lower()

    # ======================================
    # AMBITION
    # ======================================

    ambition_words = [

        "goal",
        "career",
        "upsc",
        "future",
        "success",
        "dream"
    ]

    if any(word in msg for word in ambition_words):

        return {

            "thought":
            "User appears highly driven by long-term goals.",

            "category":
            "ambition",

            "importance":
            0.8
        }

    # ======================================
    # STRESS
    # ======================================

    stress_words = [

        "stress",
        "tired",
        "overwhelmed",
        "pressure",
        "anxious"
    ]

    if any(word in msg for word in stress_words):

        return {

            "thought":
            "User may be experiencing elevated stress levels.",

            "category":
            "emotional",

            "importance":
            0.7
        }

    # ======================================
    # SELF REFLECTION
    # ======================================

    reflection_words = [

        "meaning",
        "purpose",
        "why",
        "understand",
        "life"
    ]

    if any(word in msg for word in reflection_words):

        return {

            "thought":
            "User is engaging in deeper self-reflection.",

            "category":
            "reflection",

            "importance":
            0.75
        }

    return None