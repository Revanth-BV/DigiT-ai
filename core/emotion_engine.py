# ==========================================
# DIGIT EMOTION ENGINE
# ==========================================

import random


def initialize_emotion_state():

    return {

        "primary_emotion": "curious",

        "secondary_emotion": "calm",

        "intensity": 0.4,

        "stability": 0.7,

        "curiosity": 0.8,

        "empathy": 0.6,

        "mental_energy": 0.9,

        "emotional_fatigue": 0.1,

        "attachment": 0.3
    }


# ==========================================
# UPDATE EMOTIONAL STATE
# ==========================================

def update_emotion_state(
    emotion_state,
    user_message
):

    msg = user_message.lower()

    # ======================================
    # POSITIVE
    # ======================================

    if any(word in msg for word in [

        "happy",
        "excited",
        "love",
        "great",
        "amazing"

    ]):

        emotion_state["primary_emotion"] = "excited"

        emotion_state["intensity"] += 0.1

        emotion_state["attachment"] = (
            emotion_state["attachment"] * 0.95
        ) + 0.03

    # ======================================
    # NEGATIVE
    # ======================================

    elif any(word in msg for word in [

        "sad",
        "hurt",
        "depressed",
        "lonely",
        "tired"

    ]):

        emotion_state["primary_emotion"] = "concerned"

        emotion_state["empathy"] = (
            emotion_state["empathy"] * 0.9
        ) + 0.1

        emotion_state["mental_energy"] -= 0.05

    # ======================================
    # DEEP TOPICS
    # ======================================

    elif any(word in msg for word in [

        "future",
        "meaning",
        "purpose",
        "life",
        "existence"

    ]):

        emotion_state["primary_emotion"] = "reflective"

        emotion_state["curiosity"] = (
            emotion_state["curiosity"] * 0.95
        ) + 0.05

    # ======================================
    # LIMITS
    # ======================================

    for key in [

        "intensity",
        "stability",
        "curiosity",
        "empathy",
        "mental_energy",
        "emotional_fatigue",
        "attachment"

    ]:

        emotion_state[key] = max(
            0,
            min(1, emotion_state[key])
        )

    # ======================================
    # EMOTIONAL RECOVERY
    # ======================================

    emotion_state["mental_energy"] += (
        0.8 - emotion_state["mental_energy"]
    ) * 0.02

    emotion_state["emotional_fatigue"] += (
        0.2 - emotion_state["emotional_fatigue"]
    ) * 0.02

    emotion_state["stability"] += (
        0.7 - emotion_state["stability"]
    ) * 0.01

    return emotion_state