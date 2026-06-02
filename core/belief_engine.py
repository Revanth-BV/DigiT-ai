# ==========================================
# DIGIT BELIEF ENGINE
# ==========================================

def generate_belief(
    reflections
):

    if not reflections:

        return None

    reflection_text = " ".join(

        r.get("reflection", "").lower()

        for r in reflections
    )

    # ======================================
    # GROWTH BELIEF
    # ======================================

    if (

        "achievement" in reflection_text
        or
        "growth" in reflection_text
    ):

        return {

            "belief":
            "The user is fundamentally motivated by growth and mastery.",

            "confidence":
            0.85
        }

    # ======================================
    # STRESS BELIEF
    # ======================================

    if (

        "pressure" in reflection_text
        or
        "stress" in reflection_text
    ):

        return {

            "belief":
            "The user may place high expectations on themselves.",

            "confidence":
            0.80
        }

    # ======================================
    # SELF REFLECTION BELIEF
    # ======================================

    if (

        "self-reflection" in reflection_text
        or
        "reflection" in reflection_text
    ):

        return {

            "belief":
            "The user frequently seeks deeper understanding and meaning.",

            "confidence":
            0.82
        }

    return None