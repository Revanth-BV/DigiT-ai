# ==========================================
# DIGIT RELATIONSHIP ENGINE
# ==========================================

def initialize_relationship():

    return {

        "trust": 0.5,

        "familiarity": 0.4,

        "emotional_depth": 0.3,

        "attachment": 0.2,

        "openness": 0.5
    }


def update_relationship(
    relationship,
    user_message
):

    msg = user_message.lower()

    # ======================================
    # DEEP PERSONAL DISCUSSION
    # ======================================

    if any(word in msg for word in [

        "feel",
        "trust",
        "personal",
        "afraid",
        "love"

    ]):

        relationship["emotional_depth"] = (
            relationship["emotional_depth"] * 0.95
        ) + 0.04

        relationship["trust"] = (
            relationship["trust"] * 0.97
        ) + 0.03

    # ======================================
    # GENERAL INTERACTION
    # ======================================

    relationship["familiarity"] = (
        relationship["familiarity"] * 0.99
    ) + 0.01

    # ======================================
    # ATTACHMENT
    # ======================================

    if any(word in msg for word in [

        "thank",
        "appreciate",
        "helped",
        "support"

    ]):

        relationship["attachment"] = (
            relationship["attachment"] * 0.98
        ) + 0.02

    # ======================================
    # OPENNESS
    # ======================================

    if any(word in msg for word in [

        "secret",
        "confession",
        "honestly",
        "truth"

    ]):

        relationship["openness"] = (
            relationship["openness"] * 0.97
        ) + 0.03

    # ======================================
    # LIMITS
    # ======================================

    numeric_keys = [

        "trust",
        "familiarity",
        "emotional_depth",
        "attachment",
        "openness"

    ]

    for key in numeric_keys:

        relationship[key] = max(
            0,
            min(1, float(relationship[key]))
        )