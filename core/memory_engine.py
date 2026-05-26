# ==========================================
# DIGIT MEMORY ENGINE
# ==========================================

import time


def calculate_memory_importance(message):

    importance = 1

    emotional_keywords = [

        "dream",
        "goal",
        "fear",
        "love",
        "stress",
        "future",
        "important",
        "hurt",
        "meaning"

    ]

    if any(word in message.lower()
           for word in emotional_keywords):

        importance += 3

    if len(message.split()) > 15:

        importance += 2

    return importance


def create_memory_object(message):

    return {

        "message": message,

        "importance":
            calculate_memory_importance(
                message
            ),

        "timestamp": time.time()
    }