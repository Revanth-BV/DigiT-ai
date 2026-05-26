# ==========================================
# DIGIT DECISION ENGINE
# ==========================================

def decide_response_style(
    emotion_state,
    relationship
):

    style = {

        "tone": "calm",

        "verbosity": "medium",

        "empathy": 0.5
    }

    if emotion_state[
        "primary_emotion"
    ] == "concerned":

        style["tone"] = "gentle"

        style["empathy"] = 0.8

    if relationship[
        "trust"
    ] > 0.7:

        style["verbosity"] = "deep"

    return style