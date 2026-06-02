# ==========================================
# DIGIT MEMORY RANKING ENGINE
# ==========================================

def calculate_memory_score(memory):

    importance = memory.get(
        "importance",
        5
    )

    emotional_weight = memory.get(
        "emotional_weight",
        0.5
    )

    repetition_count = memory.get(
        "repetition_count",
        1
    )

    score = (

        (importance / 10) * 0.5 +

        emotional_weight * 0.3 +

        min(
            repetition_count / 10,
            1
        ) * 0.2

    )

    return round(
        score,
        3
    )