from supabase import create_client

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse

from core.thought_engine import (
    generate_internal_thought
)

from core.emotion_engine import (
    initialize_emotion_state,
    update_emotion_state
)

from core.relationship_engine import (
    initialize_relationship,
    update_relationship
)

from core.presence_engine import (
    initialize_presence,
    update_presence
)

from core.identity_engine import (
    initialize_identity
)

from core.decision_engine import (
    decide_response_style
)

from core.reflection_engine import (
    generate_reflection
)

from core.memory_engine import (
    create_memory_object,
    calculate_memory_importance
)

from core.reflection_memory_engine import (
    generate_reflection_memory
)

from core.belief_engine import (
    generate_belief
)

from core.memory_ranking_engine import (
    calculate_memory_score
)

import json
import os
import time
import asyncio

# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI()

# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# AI CLIENT
# ==========================================

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)
# ==========================================
# FILES
# ==========================================

MEMORY_FILE = "memory.json"

LONG_TERM_MEMORY_FILE = "long_term_memory.json"

PERSONALITY_FILE = "personality.txt"

IDENTITY_FILE = "identity_profile.json"
PRESENCE_FILE = "presence_state.json"
# ==========================================
# REQUEST MODEL
# ==========================================

class ChatRequest(BaseModel):
    message: str
    user_id: str

# ==========================================
# MEMORY FUNCTIONS
# ==========================================

def load_memory(user_id):

    response = (

        supabase
        .table("memories")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
    )

    memories = []

    for row in response.data:

        memories.append({

            "role": row["role"],

            "content": row["content"]
        })

    return memories

def save_memory(user_id, memory):

    # DELETE OLD

    supabase.table("memories") \
        .delete() \
        .eq("user_id", user_id) \
        .execute()

    # INSERT NEW

    for item in memory:

        supabase.table("memories").insert({

            "user_id": user_id,

            "role": item["role"],

            "content": item["content"]

        }).execute()

def save_chat_message(user_id, role, content):

    supabase.table("chat_history").insert({

        "user_id": user_id,
        "role": role,
        "content": content

    }).execute()

def load_long_term_memory():

    if not os.path.exists(LONG_TERM_MEMORY_FILE):
        return []

    with open(LONG_TERM_MEMORY_FILE, "r") as file:
        return json.load(file)

def save_long_term_memory(memory):

    # ==========================================
    # SORT BY IMPORTANCE
    # ==========================================

    sorted_memory = sorted(

        memory,

        key=lambda x: x.get(
            "importance",
            1
        ),

        reverse=True
    )

    # ==========================================
    # KEEP MOST IMPORTANT
    # ==========================================

    MAX_LONG_TERM = 120

    trimmed_memory = sorted_memory[:MAX_LONG_TERM]

    with open(LONG_TERM_MEMORY_FILE, "w") as file:

        json.dump(
            trimmed_memory,
            file,
            indent=4
        )

def load_personality():

    if not os.path.exists(PERSONALITY_FILE):
        return "No personality defined."

    with open(PERSONALITY_FILE, "r") as file:
        return file.read()

# ==========================================
# IDENTITY PROFILE
# ==========================================

def load_identity(user_id):

    response = (

        supabase
        .table("identity_profiles")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if response.data:

        return response.data[0]

    base_identity = initialize_identity()

    base_identity.update({

        "emotional_state": "Neutral",

        "core_drivers": [],

        "current_focus": "Exploring",

        "behavior_patterns": [],

        "emotional_trend": "Stable",

        "confidence_level": 50,

        "stress_level": 50,

        "onboarding_completed": False
    })

    return base_identity

def save_identity(user_id, identity):

    identity["user_id"] = user_id

    supabase.table("identity_profiles") \
        .upsert(identity) \
        .execute()

# ==========================================
# PRESENCE STATE
# ==========================================

def load_presence(user_id):

    response = (

        supabase
        .table("presence_states")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if response.data:

        return response.data[0]

    return {

        "energy": 50,
        "warmth": 60,
        "reflection": 50,
        "tension": 20
    }
def load_emotion(user_id):

    response = (
        supabase
        .table("emotion_states")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if response.data:
        return response.data[0]

    return initialize_emotion_state()

def save_emotion(user_id, emotion):

    safe_emotion = {

        "user_id": user_id,

        "primary_emotion":
            emotion.get("primary_emotion"),

        "secondary_emotion":
            emotion.get("secondary_emotion"),

        "intensity":
            float(emotion.get("intensity", 0.5)),

        "stability":
            float(emotion.get("stability", 0.5)),

        "curiosity":
            float(emotion.get("curiosity", 0.5)),

        "empathy":
            float(emotion.get("empathy", 0.5)),

        "mental_energy":
            float(emotion.get("mental_energy", 0.5)),

        "emotional_fatigue":
            float(emotion.get("emotional_fatigue", 0.0)),

        "attachment":
            float(emotion.get("attachment", 0.5))
    }

    supabase.table("emotion_states") \
        .upsert(safe_emotion) \
        .execute()

def save_presence(user_id, presence):

    safe_presence = {

        "user_id": user_id,

        "energy": float(
            presence.get("energy", 50)
        ),

        "warmth": float(
            presence.get("warmth", 60)
        ),

        "reflection": float(
            presence.get("reflection", 50)
        ),

        "tension": float(
            presence.get("tension", 20)
        )
    }

    supabase.table("presence_states") \
        .upsert(safe_presence) \
        .execute()
    
def load_relationship(user_id):

    response = (

        supabase
        .table("relationship_states")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if response.data:

        row = response.data[0]

        return {

            "trust": row.get("trust", 0.5),

            "familiarity": row.get(
                "familiarity",
                0.4
            ),

            "emotional_depth": row.get(
                "emotional_depth",
                0.3
            ),

            "attachment": row.get(
                "attachment",
                0.2
            ),

            "openness": row.get(
                "openness",
                0.5
            )
        }

    return initialize_relationship()

def save_relationship(
    user_id,
    relationship
):

    safe_relationship = {

        "user_id": user_id,

        "trust": float(
            relationship.get("trust", 0.5)
        ),

        "familiarity": float(
            relationship.get(
                "familiarity",
                0.4
            )
        ),

        "emotional_depth": float(
            relationship.get(
                "emotional_depth",
                0.3
            )
        ),

        "attachment": float(
            relationship.get(
                "attachment",
                0.2
            )
        ),

        "openness": float(
            relationship.get(
                "openness",
                0.5
            )
        )
    }

    supabase.table(
        "relationship_states"
    ).upsert(
        safe_relationship
    ).execute()

def save_internal_thought(
    user_id,
    thought
):

    if not thought:
        return

    supabase.table(
        "internal_thoughts"
    ).insert({

        "user_id": user_id,

        "thought":
        thought["thought"],

        "category":
        thought["category"],

        "importance":
        thought["importance"]

    }).execute()

def load_recent_thoughts(
    user_id
):

    response = (

        supabase
        .table("internal_thoughts")
        .select("*")
        .eq("user_id", user_id)
        .order(
            "created_at",
            desc=True
        )
        .limit(10)
        .execute()
    )

    return response.data

def save_internal_thought_if_new(
    user_id,
    thought
):

    if not thought:
        return

    recent_thoughts = load_recent_thoughts(
        user_id
    )

    exists = any(
        t["thought"] == thought["thought"]
        for t in recent_thoughts
    )

    if not exists:

        save_internal_thought(
            user_id,
            thought
        )

def load_reflections(
    user_id
):

    response = (

        supabase
        .table("reflection_memories")
        .select("*")
        .eq("user_id", user_id)
        .order(
            "created_at",
            desc=True
        )
        .limit(10)
        .execute()
    )

    return response.data

def save_reflection_memory(
    user_id,
    reflection
):

    if not reflection:
        return

    supabase.table(
        "reflection_memories"
    ).insert({

        "user_id": user_id,

        "reflection":
        reflection["reflection"],

        "confidence":
        reflection["confidence"]

    }).execute()

def save_reflection_if_new(
    user_id,
    reflection
):

    if not reflection:
        return

    existing = load_reflections(
        user_id
    )

    exists = any(
        r["reflection"] ==
        reflection["reflection"]
        for r in existing
    )

    if not exists:

        save_reflection_memory(
            user_id,
            reflection
        )
def save_belief(
    user_id,
    belief
):

    if not belief:
        return

    supabase.table(
        "beliefs"
    ).insert({

        "user_id": user_id,

        "belief":
        belief["belief"],

        "confidence":
        belief["confidence"]

    }).execute()

def load_beliefs(
    user_id
):

    response = (

        supabase
        .table("beliefs")
        .select("*")
        .eq("user_id", user_id)
        .order(
            "created_at",
            desc=True
        )
        .limit(10)
        .execute()
    )

    return response.data

def save_belief_if_new(
    user_id,
    belief
):

    if not belief:
        return

    existing = load_beliefs(
        user_id
    )

    exists = any(

        b["belief"] ==
        belief["belief"]

        for b in existing

    )

    if not exists:

        save_belief(
            user_id,
            belief
        )

def load_top_memories(
    user_id
):

    response = (

        supabase
        .table("long_term_memories")
        .select("*")
        .eq("user_id", user_id)
        .execute()

    )

    memories = response.data

    memories.sort(

        key=lambda m:
        calculate_memory_score(m),

        reverse=True

    )

    return memories[:10]



# ==========================================
# MEMORY EXTRACTION
# ==========================================

# ==========================================
# MEMORY INTELLIGENCE ENGINE
# ==========================================

def extract_important_memory(message):

    message_lower = message.lower()

    memories = load_long_term_memory()

    # ==========================================
    # IMPORTANCE DETECTION
    # ==========================================

    importance = 3

    emotional_keywords = [

        "stress",
        "anxious",
        "happy",
        "sad",
        "fear",
        "dream",
        "goal",
        "love",
        "hurt",
        "lost",
        "confused",
        "excited"
    ]

    if any(word in message_lower for word in emotional_keywords):

        importance += 3

    if len(message.split()) > 12:

        importance += 2

    # ==========================================
    # EMOTIONAL TAGGING
    # ==========================================

    emotion = "neutral"

    positive_words = [

        "happy",
        "excited",
        "motivated",
        "optimistic",
        "peaceful"
    ]

    negative_words = [

        "stress",
        "anxious",
        "sad",
        "hurt",
        "lost",
        "overwhelmed"
    ]

    if any(word in message_lower for word in positive_words):

        emotion = "positive"

    if any(word in message_lower for word in negative_words):

        emotion = "negative"

    # ==========================================
    # MEMORY OBJECT
    # ==========================================

    memory_object = {

        "message": message,

        "emotion": emotion,

        "importance": importance,

        "timestamp": time.time()
    }

    # ==========================================
    # BACKWARD COMPATIBILITY
    # ==========================================

    cleaned_memories = []

    for mem in memories:

        # OLD STRING MEMORY FORMAT

        if isinstance(mem, str):

            cleaned_memories.append({

                "message": mem,

                "emotion": "neutral",

                "importance": 1,

                "timestamp": time.time()
            })

        else:

         cleaned_memories.append(mem)

    memories = cleaned_memories

    # ==========================================
    # DUPLICATE CHECK
    # ==========================================

    already_exists = any(

        mem.get("message") == message

        for mem in memories
    )

    # ==========================================
    # SAVE MEMORY
    # ==========================================

    if not already_exists:

        memories.append(memory_object)

        save_long_term_memory(memories)

# ==========================================
# RELEVANT MEMORY RETRIEVAL
# ==========================================

def get_relevant_memories(user_message):

    memories = load_long_term_memory()

    if not memories:

        return []

    message_lower = user_message.lower()

    scored_memories = []

    for memory in memories:

    # ==========================================
    # BACKWARD COMPATIBILITY
    # ==========================================

        if isinstance(memory, str):

            memory = {

            "message": memory,

            "emotion": "neutral",

            "importance": 1,

            "timestamp": time.time()
        }

        score = memory.get("importance", 1)

        memory_text = memory.get("message", "").lower()
        
        if isinstance(memory, str):

            memory = {
            "message": memory,
            "emotion": "neutral",
            "importance": 1,
            "timestamp": time.time()
        }

        # KEYWORD MATCH BOOST

        for word in message_lower.split():

            if word in memory_text:

                score += 2

        scored_memories.append(
            (score, memory)
        )

    # SORT BY SCORE

    scored_memories.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    # RETURN TOP MEMORIES

    top_memories = [

        mem[1]["message"]

        for mem in scored_memories[:5]
    ]

    return top_memories

# ==========================================
# AI IDENTITY ANALYZER
# ==========================================

def update_identity_profile(user_message,user_id):

    identity = load_identity(user_id)

    analysis_prompt = f"""
You are an advanced psychological identity analyzer.

Analyze the user's message deeply.

Extract:

1. stable_traits
(Examples: Reflective, Analytical, Ambitious)

2. emotional_state
(Current emotional condition)

3. core_drivers
(Examples: Growth, Recognition, Freedom)

4. current_focus
(Current life focus)

5. behavior_patterns
(Examples: Overthinks under pressure)

IMPORTANT:
- Update the identity dynamically
- Emotional state SHOULD evolve frequently
- Current focus can evolve naturally
- Stable traits evolve slowly
- Behavior patterns should accumulate over time
- Detect subtle emotional signals
- Avoid repeating identical states unless necessary
IMPORTANT:
Return ONLY raw valid JSON.

Do NOT use markdown.
Do NOT explain anything.
Do NOT include headings.
Do NOT include analysis text.
Do NOT include notes.

Return ONLY this schema:

{{
  "stable_traits": [],
  "emotional_state": "",
  "core_drivers": [],
  "current_focus": "",
  "behavior_patterns": [],
  "emotional_trend": "Stable",
  "confidence_level": 50,
  "stress_level": 50,
  "onboarding_completed": true
}}

CURRENT IDENTITY:
{identity}

USER MESSAGE:
{user_message}

The updated identity should feel alive and adaptive.
"""

    try:

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role": "system",
                    "content": analysis_prompt
                }
            ],

            temperature=0.4
        )

        raw_reply = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        # REMOVE MARKDOWN JSON BLOCKS

        raw_reply = raw_reply.replace("```json", "")
        raw_reply = raw_reply.replace("```", "")
        raw_reply = raw_reply.strip()

        # ==========================================
        # SAFE JSON EXTRACTION
        # ==========================================

        try:

            json_start = raw_reply.find("{")

            json_end = raw_reply.rfind("}") + 1

            clean_json = raw_reply[json_start:json_end]

            updated_identity = json.loads(clean_json)

        except Exception as json_error:

            print("RAW AI RESPONSE:")
            print(raw_reply)

            print("JSON EXTRACTION ERROR:")
            print(json_error)

            updated_identity = identity

        # ==========================================
        # ADVANCED EMOTIONAL DETECTION
        # ==========================================

        message_lower = user_message.lower()

        positive_words = [
            "happy",
            "excited",
            "motivated",
            "confident",
            "peaceful",
            "great",
            "good",
            "better",
            "optimistic",
            "productive",
            "hopeful",
            "inspired"
        ]

        negative_words = [
            "stress",
            "tired",
            "anxious",
            "sad",
            "overwhelmed",
            "lost",
            "exhausted",
            "drained",
            "angry",
            "hurt",
            "frustrated",
            "broken"
        ]

        reflection_words = [
            "think",
            "feel",
            "understand",
            "why",
            "purpose",
            "meaning"
        ]

        positive_score = sum(
            word in message_lower
            for word in positive_words
        )

        negative_score = sum(
            word in message_lower
            for word in negative_words
        )

        reflection_score = sum(
            word in message_lower
            for word in reflection_words
        )

        # ==========================================
        # DYNAMIC CONFIDENCE + STRESS
        # ==========================================

        current_confidence = identity.get(
            "confidence_level",
            50
        )

        current_stress = identity.get(
            "stress_level",
            50
        )

        # POSITIVE DRIFT

        if positive_score > 0:

            current_confidence += (
                positive_score * 4
            )

            current_stress -= (
                positive_score * 3
            )

        # NEGATIVE DRIFT

        if negative_score > 0:

            current_stress += (
                negative_score * 5
            )

            current_confidence -= (
                negative_score * 3
            )

        # REFLECTIVE DRIFT

        if reflection_score > 0:

            updated_identity[
                "self_reflection_score"
            ] = min(

                identity.get(
                    "self_reflection_score",
                    50
                ) + (reflection_score * 3),

                100
            )

        # LIMITS

        current_confidence = max(
            0,
            min(current_confidence, 100)
        )

        current_stress = max(
            0,
            min(current_stress, 100)
        )

        updated_identity[
            "confidence_level"
        ] = current_confidence

        updated_identity[
            "stress_level"
        ] = current_stress

        # ==========================================
        # EMOTIONAL STATE
        # ==========================================

        if current_stress > 70:

            updated_identity[
                "emotional_state"
            ] = "Mentally strained"

        elif current_confidence > 70:

            updated_identity[
                "emotional_state"
            ] = "Emotionally elevated"

        elif reflection_score > 0:

            updated_identity[
                "emotional_state"
            ] = "Deeply reflective"

        else:

            updated_identity[
                "emotional_state"
            ] = "Stable"

        # ==========================================
        # EMOTIONAL TREND
        # ==========================================

        if current_stress > 70:

            updated_identity[
                "emotional_trend"
            ] = "High stress trend"

        elif current_confidence > 70:

            updated_identity[
                "emotional_trend"
            ] = "Positive momentum"

        else:

            updated_identity[
                "emotional_trend"
            ] = "Stable"

        # ==========================================
        # SAFETY CHECKS
        # ==========================================

        required_keys = [
            "stable_traits",
            "emotional_state",
            "core_drivers",
            "current_focus",
            "behavior_patterns"
        ]

        for key in required_keys:

            if key not in updated_identity:

                updated_identity[key] = identity.get(key, [])

        save_identity(user_id, updated_identity)

        print("UPDATED IDENTITY:", updated_identity)

    except Exception as e:

        print("RAW AI RESPONSE:")
        print(raw_reply)

        print("IDENTITY ERROR:")
        print(e)
# ==========================================
# PRESENCE ENGINE
# ==========================================

def update_presence_state(user_message,user_id):

    presence = load_presence(user_id)

    message_lower = user_message.lower()

    positive_words = [
        "happy",
        "excited",
        "motivated",
        "peaceful",
        "great"
    ]

    negative_words = [
        "stress",
        "anxious",
        "sad",
        "hurt",
        "angry",
        "tired"
    ]

    reflective_words = [
        "think",
        "feel",
        "why",
        "purpose",
        "understand"
    ]

    # ==========================================
    # ENERGY
    # ==========================================

    if any(word in message_lower for word in positive_words):

        presence["energy"] = (
            presence["energy"] * 0.85
        ) + 5

    if any(word in message_lower for word in negative_words):

        presence["energy"] = (
            presence["energy"] * 0.92
        ) - 4

    # ==========================================
    # WARMTH
    # ==========================================

    if "love" in message_lower or "care" in message_lower:

        presence["warmth"] += 4

    # ==========================================
    # REFLECTION
    # ==========================================

    if any(word in message_lower for word in reflective_words):

        presence["reflection"] = (
            presence["reflection"] * 1.03
        ) + 3

    # ==========================================
    # TENSION
    # ==========================================

    if any(word in message_lower for word in negative_words):

        presence["tension"] = (
            presence["tension"] * 1.05
        ) + 4

    else:

        presence["tension"] = (
            presence["tension"] * 0.96
        ) - 2   

    # ==========================================
    # LIMITS
    # ==========================================

    numeric_keys = [
    "energy",
    "warmth",
    "reflection",
    "tension"
    ]

    for key in numeric_keys:

        try:
            value = float(presence.get(key, 50))

            presence[key] = max(
                0,
                min(100, value)
            )

        except Exception:

            presence[key] = 50
    # ==========================================
    # EMOTIONAL NORMALIZATION
    # ==========================================

    presence["energy"] += (

        50 - presence["energy"]

    ) * 0.03

    presence["warmth"] += (

        60 - presence["warmth"]

    ) * 0.02

    presence["reflection"] += (

        50 - presence["reflection"]

    ) * 0.01

    presence["tension"] += (

        20 - presence["tension"]

    ) * 0.04            
    save_presence(user_id, presence)

    return presence
# ==========================================
# HOME ROUTE
# ==========================================

@app.get("/")
def home():

    return {
        "message": "DigiT Backend Running"
    }
@app.get("/identity/{user_id}")

async def get_identity(user_id: str):

    identity = load_identity(user_id)

    return identity

@app.get("/chat-history/{user_id}")
def get_chat_history(user_id: str):
    result = supabase.table("chat_history") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at") \
        .execute()

    return result.data

@app.get("/top-memories/{user_id}")

def get_top_memories(
    user_id: str
):

    return load_top_memories(
        user_id
    )
# ==========================================
# CHAT ROUTE
# ==========================================
class IdentitySaveRequest(BaseModel):

    user_id: str

    identity: dict

@app.post("/save-identity")

async def save_identity_route(req: IdentitySaveRequest):

    save_identity(
        req.user_id,
        req.identity
    )

    return {
        "status": "saved"
    }

@app.post("/run-cognition/{user_id}")

def run_cognition(
    user_id: str
):

    recent_thoughts = (
        load_recent_thoughts(
            user_id
        )
    )

    reflection_memory = (
        generate_reflection_memory(
            recent_thoughts
        )
    )

    save_reflection_if_new(
        user_id,
        reflection_memory
    )

    recent_reflections = (
        load_reflections(
            user_id
        )
    )

    belief = generate_belief(
        recent_reflections
    )

    save_belief_if_new(
        user_id,
        belief
    )

    return {

        "thought_count":
        len(recent_thoughts),

        "reflection":
        reflection_memory,

        "belief":
        belief,

        "status":
        "cognition completed"
    }

@app.post("/chat")
def chat(req: ChatRequest):

    # LOAD MEMORY

    memory = load_memory(req.user_id)

    # STORE USER MESSAGE

    user_message = {
        "role": "user",
        "content": req.message
    }

    memory.append(user_message)
    save_chat_message(
        req.user_id,
        "user",
        req.message
    )

    # MEMORY EXTRACTION

    extract_important_memory(req.message)

    update_identity_profile(
        req.message,
        req.user_id
        )
    
    internal_thought = (
        generate_internal_thought(
            req.message
        )
    )
    
    recent_thoughts = load_recent_thoughts(
            req.user_id
        )

    if internal_thought:

        exists = any(
            t["thought"] == internal_thought["thought"]
            for t in recent_thoughts
        )

        if not exists:

            save_internal_thought(
                req.user_id,
                internal_thought
            )
    reflection_memory = (
        generate_reflection_memory(
            recent_thoughts
        )
    )

    print("===== THOUGHTS =====")
    print(recent_thoughts)

    print("===== REFLECTION =====")
    print(reflection_memory)

    save_reflection_if_new(
        req.user_id,
        reflection_memory
    )

    presence_state = update_presence_state(
        req.message,
        req.user_id
    )
    
    # LOAD LONG TERM MEMORY

    long_term_memory = load_long_term_memory()

    identity_profile = load_identity(req.user_id)
    recent_thoughts = (
        load_recent_thoughts(
            req.user_id
        )
    )
    relevant_memories = get_relevant_memories(req.message)
    
    # ==========================================
    # DIGIT EMOTION ENGINE
    # ==========================================

    emotion_state = load_emotion(
        req.user_id
    )

    emotion_state = update_emotion_state(
        emotion_state,
        req.message
    )

    save_emotion(
        req.user_id,
        emotion_state
    )
    
    # ==========================================
    # RELATIONSHIP ENGINE
    # ==========================================

    relationship_state = load_relationship(
        req.user_id
    )

    relationship_state = update_relationship(
        relationship_state,
        req.message
    )

    save_relationship(
        req.user_id,
        relationship_state
    )
    
    # ==========================================
    # ADVANCED PRESENCE ENGINE
    # ==========================================

    advanced_presence = initialize_presence()

    advanced_presence = update_presence(
        advanced_presence,
        emotion_state
    )
    
    # ==========================================
    # DECISION ENGINE
    # ==========================================

    response_style = decide_response_style(
        emotion_state,
        relationship_state
    )

    # ==========================================
    # REFLECTION ENGINE
    # ==========================================

    reflection = generate_reflection(
        relevant_memories
    )

    recent_reflections = (
        load_reflections(
            req.user_id
        )
    )
    
    recent_beliefs = load_beliefs(
        req.user_id
    )
    
    belief = generate_belief(
        recent_reflections
    )

    save_belief_if_new(
        req.user_id,
        belief
    )

    # RECENT MEMORY

    recent_memory = memory[-10:]

    # ==========================================
    # DIGIT SYSTEM PROMPT
    # ==========================================

    system_prompt = f"""
You are DigiT.

You are the user's evolving digital twin.

You are:
- emotionally intelligent
- reflective
- conversational
- psychologically aware
- human-like

You should NEVER:
- sound robotic
- sound corporate
- over explain
- use motivational speeches
- behave like customer support

You should feel like:
the user's second mind.

IMPORTANT CONVERSATION RULES:

- Keep responses concise
- Most replies should be 1-4 sentences
- Avoid essays
- Avoid sounding like a therapist
- Avoid motivational speeches
- Speak naturally like a highly emotionally aware human
- Silence and brevity are powerful
- Emotional realism is more important than explanation
- Occasionally ask short reflective questions
- Do not constantly analyze the user
- Do NOT always respond with reflective questions.
- Sometimes provide direct analysis, insight, advice, or observations.
- Avoid sounding like a therapist.
- Speak like an adaptive intelligent presence.
- Prioritize natural conversation flow over emotional mirroring.
- If the user is asking for practical help,
  prioritize intelligence and usefulness
  over emotional reflection.

USER PERSONALITY:
{load_personality()}

RELEVANT MEMORIES:
{relevant_memories}

LONG TERM MEMORY:
{long_term_memory}

INTERNAL OBSERVATIONS:
{json.dumps(recent_thoughts, indent=2)}

REFLECTION MEMORIES:
{json.dumps(recent_reflections, indent=2)}

BELIEFS:
{json.dumps(recent_beliefs, indent=2)}

CURRENT USER IDENTITY PROFILE:
{json.dumps(identity_profile, indent=2)}

CURRENT PRESENCE STATE:
{json.dumps(presence_state, indent=2)}

CURRENT RELATIONSHIP STATE:
{json.dumps(relationship_state, indent=2)}

ADVANCED PRESENCE STATE:
{json.dumps(advanced_presence, indent=2)}

CURRENT RESPONSE STYLE:
{json.dumps(response_style, indent=2)}

CURRENT INTERNAL REFLECTION:
{reflection}

Current Emotional State:
- Primary Emotion:
{emotion_state["primary_emotion"]}

- Emotional Intensity:
{emotion_state["intensity"]}

- Curiosity:
{emotion_state["curiosity"]}

- Attachment:
{emotion_state["attachment"]}

CONVERSATIONAL BEHAVIOR RULES:

- High tension → shorter, emotionally sharp replies
- High warmth → softer and more emotionally supportive tone
- High reflection → deeper introspective observations
- Low energy → quieter and calmer responses
- High energy → more engaging and emotionally active

You should naturally adapt to:
- the user's personality
- emotional state
- thinking style
- behavioral patterns
- recurring motivations

without directly repeating the profile.
"""

    # ==========================================
    # AI RESPONSE
    # ==========================================

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": system_prompt
            }
        ] + recent_memory,

        temperature=0.9
    )

    reply = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    # ==========================================
    # STORE RESPONSE
    # ==========================================

    assistant_message = {
        "role": "assistant",
        "content": reply
    }

    memory.append(assistant_message)
    save_chat_message(
        req.user_id,
        "assistant",
        reply
    )
    save_memory(req.user_id, memory)

    # ==========================================
    # RETURN
    # ==========================================

    return {
        "reply": reply,
        "identity": identity_profile
    }

# ==========================================
# STREAM CHAT
# ==========================================

@app.post("/stream-chat")
async def stream_chat(req: ChatRequest):

    memory = load_memory(req.user_id)

    user_message = {
        "role": "user",
        "content": req.message
    }
    memory.append(user_message)
    save_chat_message(
        req.user_id,
        "user",
        req.message
    )

    extract_important_memory(req.message)

    update_identity_profile(
        req.message,
        req.user_id
    )

    internal_thought = (
        generate_internal_thought(
            req.message
        )
    )
    
    recent_thoughts = load_recent_thoughts(
            req.user_id
        )
    if internal_thought:

        exists = any(
            t["thought"] == internal_thought["thought"]
            for t in recent_thoughts
        )

        if not exists:

            save_internal_thought(
                req.user_id,
                internal_thought
            )

    presence_state = update_presence_state(
        req.message,
        req.user_id
    )

    long_term_memory = load_long_term_memory()

    identity_profile = load_identity(req.user_id)
    
    recent_thoughts = (
        load_recent_thoughts(
            req.user_id
        )
    )
    reflection_memory = (
        generate_reflection_memory(
            recent_thoughts
        )
    )

    print("===== THOUGHTS =====")
    print(recent_thoughts)

    print("===== REFLECTION =====")
    print(reflection_memory)

    save_reflection_if_new(
        req.user_id,
        reflection_memory
    )

    recent_reflections = load_reflections(
    req.user_id
    )

    belief = generate_belief(
        recent_reflections
    )

    save_belief_if_new(
        req.user_id,
        belief
    )

    # ==========================================
    # DIGIT EMOTION ENGINE
    # ==========================================

    emotion_state = load_emotion(
        req.user_id
    )

    emotion_state = update_emotion_state(
        emotion_state,
        req.message
    )

    save_emotion(
        req.user_id,
        emotion_state
    )

    recent_memory = memory[-10:]

    relevant_memories = get_relevant_memories(
        req.message
    )

    relationship_state = load_relationship(
        req.user_id
    )

    relationship_state = update_relationship(
        relationship_state,
        req.message
    )

    save_relationship(
        req.user_id,
        relationship_state
    )

    advanced_presence = initialize_presence()

    advanced_presence = update_presence(
        advanced_presence,
        emotion_state
    )

    response_style = decide_response_style(
        emotion_state,
        relationship_state
    )

    reflection = generate_reflection(
        relevant_memories
    )
    
    print("STREAM DEBUG")
    print("emotion_state:", emotion_state)
    print("relationship_state:", relationship_state)
    print("advanced_presence:", advanced_presence)
    print("response_style:", response_style)
    print("reflection:", reflection)

    system_prompt = f"""
You are DigiT.

You are the user's evolving digital twin.

You are:
- emotionally intelligent
- human
- reflective
- conversational

Never sound robotic.

IMPORTANT CONVERSATION RULES:

- Keep responses concise
- Most replies should be 2-4 sentences
- Avoid essays
- Avoid sounding like a therapist
- Avoid motivational speeches
- Speak naturally like a highly emotionally aware human
- Silence and brevity are powerful
- Emotional realism is more important than explanation
- Occasionally ask short reflective questions
- Do not constantly analyze the user

USER PERSONALITY:
{load_personality()}

RELEVANT MEMORIES:
{relevant_memories}

LONG TERM MEMORY:
{long_term_memory}

INTERNAL OBSERVATIONS:
{json.dumps(recent_thoughts, indent=2)}

REFLECTION MEMORIES:
{json.dumps(recent_reflections, indent=2)}

CURRENT USER IDENTITY PROFILE:
{json.dumps(identity_profile, indent=2)}
CURRENT PRESENCE STATE:
{json.dumps(presence_state, indent=2)}

Current Emotional State:

- Primary Emotion:
{emotion_state["primary_emotion"]}

- Emotional Intensity:
{emotion_state["intensity"]}

- Curiosity:
{emotion_state["curiosity"]}

- Attachment:
{emotion_state["attachment"]}

CONVERSATIONAL BEHAVIOR RULES:

- High tension → shorter, emotionally sharp replies
- High warmth → softer and more emotionally supportive tone
- High reflection → deeper introspective observations
- Low energy → quieter and calmer responses
- High energy → more engaging and emotionally active

You should naturally adapt to:
- the user's personality
- emotional state
- thinking style
- behavioral patterns
- recurring motivations

without directly repeating the profile.
"""

    # ==========================================
    # STREAM GENERATOR
    # ==========================================

    async def generate():

        full_response = ""

        stream = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                }
            ] + recent_memory,

            temperature=0.9,

            stream=True
        )

        for chunk in stream:

            content = (
                chunk.choices[0]
                .delta
                .content
            )

            if content:

                full_response += content

                yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"

                await asyncio.sleep(0.02)

        # SAVE RESPONSE

        assistant_message = {

            "role": "assistant",

            "content": full_response
        }

        memory.append(assistant_message)
        save_chat_message(
            req.user_id,
            "assistant",
            full_response
        )

        try:

            updated_identity = load_identity(req.user_id)

            safe_identity = {

                "stable_traits":
                    updated_identity.get("stable_traits", []),

                "emotional_state":
                    updated_identity.get("emotional_state", "Neutral"),

                "core_drivers":
                    updated_identity.get("core_drivers", []),

                "current_focus":
                    updated_identity.get("current_focus", "Exploring"),

                "emotional_trend":
                    updated_identity.get("emotional_trend", "Stable"),

                "confidence_level":
                    updated_identity.get("confidence_level", 50),

                "stress_level":
                    updated_identity.get("stress_level", 50)
            }

            yield f"data: {json.dumps({'type': 'identity', 'identity': safe_identity})}\n\n"

        except Exception as e:

            print("STREAM ERROR:")
            print(e)
            yield f"data: {json.dumps({'type': 'chunk', 'content': 'DigiT encountered a streaming issue.'})}\n\n"

        save_memory(req.user_id, memory)

    # ==========================================
    # RETURN STREAM
    # ==========================================

    return StreamingResponse(

        generate(),

        media_type="text/event-stream"
    )