# ==========================================
# DIGIT PRESENCE ENGINE
# ==========================================

def initialize_presence():

    return {

        "social_energy": 0.8,

        "attentiveness": 0.7,

        "protectiveness": 0.4,

        "curiosity": 0.8,

        "calmness": 0.6
    }


def update_presence(
    presence,
    emotion_state
):

    if emotion_state[
        "primary_emotion"
    ] == "concerned":

        presence[
            "protectiveness"
        ] += 0.05

        presence[
            "social_energy"
        ] -= 0.03

    if emotion_state[
        "primary_emotion"
    ] == "reflective":

        presence[
            "curiosity"
        ] += 0.04

    # LIMITS

    for key in presence:

        presence[key] = max(
            0,
            min(1, presence[key])
        )

    return presence