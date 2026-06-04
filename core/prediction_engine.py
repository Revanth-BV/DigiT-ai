# ==========================================
# DIGIT PREDICTION ENGINE
# ==========================================

def generate_prediction(
    beliefs
):

    if not beliefs:
        return None

    belief_text = " ".join(

        b.get(
            "belief",
            ""
        ).lower()

        for b in beliefs
    )

    # ======================================
    # GROWTH PREDICTION
    # ======================================

    if (
        "growth" in belief_text
        or
        "mastery" in belief_text
    ):

        return {

            "prediction":
            "The user is likely to respond well to structured long-term planning.",

            "confidence":
            0.85
        }

    # ======================================
    # STRESS PREDICTION
    # ======================================

    if (
        "expectations" in belief_text
        or
        "pressure" in belief_text
    ):

        return {

            "prediction":
            "The user may benefit from emotional decompression and recovery.",

            "confidence":
            0.80
        }

    return None