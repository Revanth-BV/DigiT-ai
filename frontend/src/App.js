import React, { useState, useRef, useEffect } from "react";
import "./App.css";
import Onboarding from "./Onboarding";
import { supabase } from "./supabase";

import {
  FaBars,
  FaTimes,
  FaBrain,
  FaMoon
} from "react-icons/fa";



function App({ session }) {

  // ==================================================
  // ONBOARDING
  // ==================================================

  const [onboardingComplete, setOnboardingComplete] = useState(null);
  // ==================================================
  // CHAT
  // ==================================================
  const [reflecting, setReflecting] = useState(false);
  const [message, setMessage] = useState("");

  const [chat, setChat] = useState([
    {
      sender: "DigiT",
      text:
        "Your Digital Twin is initialized. I’m beginning to understand how you think."
    }
  ]);

console.log("SESSION:", session);
console.log("USER:", session?.user);
console.log("USER ID:", session?.user?.id);

  const [loading, setLoading] = useState(false);
  
    useEffect(() => {

      const loadHistory = async () => {

        if (!session?.user?.id) return;

        try {

          const response = await fetch(
            `https://digit-ai-production.up.railway.app/chat-history/${session.user.id}`
          );

          const data = await response.json();

          const formattedMessages = data.map((msg) => ({

            sender:
              msg.role === "assistant"
                ? "DigiT"
                : "You",

            text: msg.content

          }));

          if (formattedMessages.length > 0) {

            setChat(formattedMessages);

            setTimeout(() => {

              scrollToBottom();

            }, 100);

          }

        } catch (error) {

          console.error(
            "Failed to load chat history:",
            error
          );
        }
      };

      loadHistory();

    }, [session]);
      // ==================================================
      // SIDEBAR
      // ==================================================

      const [sidebarOpen, setSidebarOpen] = useState(false);

      // ==================================================
      // MODES
      // ==================================================

      const [focusMode, setFocusMode] = useState(false);

      const [emotionMode, setEmotionMode] = useState("calm");

      // ==================================================
      // IDENTITY
      // ==================================================

      const [identity, setIdentity] = useState({

      personality: "Reflective • Analytical",

      emotional: "Neutral",

      drivers: "Growth",

      focus: "Self exploration",

      trend: "Stable",

      confidence: 50,

      stress: 50
    });

      // ==================================================
      // SIDEBAR PULSE
      // ==================================================

      const [pulse, setPulse] = useState(false);

      // ==================================================
      // AUTO SCROLL
      // ==================================================

      const chatEndRef = useRef(null);
      const scrollToBottom = () => {

        chatEndRef.current?.scrollIntoView({
          behavior: "smooth"
        });

      };

      useEffect(() => {

        scrollToBottom();

      }, [chat]);   

      useEffect(() => {

      const fetchProfile = async () => {

        const response = await fetch(

          `https://digit-ai-production.up.railway.app/identity/${session.user.id}`
        );

        const data = await response.json();

        setOnboardingComplete(
          data.onboarding_completed || false
        );
      };

      fetchProfile();

    }, [session]);
  // ==================================================
  // ONBOARDING SCREEN
  // ==================================================

    if (!onboardingComplete) {

      return (

        <Onboarding
        onComplete={async (answers) => {

        console.log("User Answers:", answers);

      // ==========================================
      // LOAD EXISTING IDENTITY
      // ==========================================

      const response = await fetch(

        `https://digit-ai-production.up.railway.app/identity/${session.user.id}`
      );

      let identity = await response.json();

      if (!identity || Object.keys(identity).length === 0) {

        identity = {

          stable_traits: [],

          emotional_state: "neutral",

          core_drivers: [],

          current_focus: "Getting Started",

          behavior_patterns: [],

          emotional_trend: "stable",

          confidence_level: 50,

          stress_level: 50,

          onboarding_completed: true
        };

      } else {

        identity.onboarding_completed = true;
      }

      // ==========================================
      // SAVE UPDATED PROFILE
      // ==========================================

      await fetch(

        "https://digit-ai-production.up.railway.app/save-identity",

        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({

            user_id: session.user.id,

            identity
          })
        }
      );

      // ==========================================
      // COMPLETE
      // ==========================================

      setOnboardingComplete(true);
    }}
  />
    );
  }

  // ==================================================
  // SEND MESSAGE
  // ==================================================

const sendMessage = async () => {

  if (!message.trim()) return;

  // USER MESSAGE

  const userMessage = {

    sender: "You",

    text: message
  };

  setChat(prev => [...prev, userMessage]);

  const currentMessage = message;

  setMessage("");

  setLoading(true);

  // EMPTY DIGIT MESSAGE

  setChat(prev => [

    ...prev,

    {
      sender: "DigiT",
      text: ""
    }
  ]);

  try {

    // ==========================================
    // FETCH STREAM
    // ==========================================

    const response = await fetch(

      "https://digit-ai-production.up.railway.app/stream-chat",

      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          message: currentMessage,
          user_id: session.user.id

        })
      }
    );

    // ==========================================
    // STREAM SETUP
    // ==========================================

    const reader = response.body.getReader();

    const decoder = new TextDecoder("utf-8");

    let done = false;

    const streamedTextRef = {

      current: ""
    };

    // ==========================================
    // STREAM LOOP
    // ==========================================

    while (!done) {

      const result = await reader.read();

      done = result.done;

      const chunk = decoder.decode(
        result.value || new Uint8Array()
      );

      const lines = chunk
      .split("\n")
      .filter(line => line.startsWith("data: "));

      for (const line of lines) {

        if (!line.startsWith("data: ")) continue;

        let parsed;

try {

       parsed = JSON.parse(
       line.substring(6)
       );

    } catch {

      continue;
      }

        // ==========================================
        // STREAMED TEXT
        // ==========================================

        if (parsed.type === "chunk") {

          streamedTextRef.current += parsed.content;

          setChat(prev => {

            const updated = [...prev];

            updated[updated.length - 1] = {

              sender: "DigiT",

              text: streamedTextRef.current
            };

            return updated;
          });
        }

        // ==========================================
        // IDENTITY UPDATE
        // ==========================================

        if (parsed.type === "identity") {

          const profile = parsed.identity;

          setIdentity({

              personality:

              profile.stable_traits &&
              profile.stable_traits.length > 0

              ? profile.stable_traits.join(" • ")

              : "Adaptive",

              emotional:
              profile.emotional_state
              || "Neutral",

              drivers:

              profile.core_drivers &&
              profile.core_drivers.length > 0

              ? profile.core_drivers.join(" • ")

              : "Learning About You",

              focus:
              profile.current_focus
              || "Exploring",

              trend:
              profile.emotional_trend
              || "Stable",

              confidence:
              profile.confidence_level
              || 50,

              stress:
              profile.stress_level
              || 50
          });

          // PULSE

          setPulse(true);

          setTimeout(() => {

            setPulse(false);

          }, 1200);
        }
      }
    }

  } catch (error) {

    console.error(error);

    setChat(prev => [

      ...prev,

      {
        sender: "System",
        text: "Unable to connect to DigiT."
      }
    ]);

  } finally {

    setLoading(false);
  }
};

const runCognition = async () => {

  try {

    setReflecting(true);

    const response = await fetch(

      `https://digit-ai-production.up.railway.app/run-cognition/${session.user.id}`,

      {
        method: "POST"
      }
    );

    const data = await response.json();

    setChat(prev => [

      ...prev,

      {

        sender: "DigiT",

        text:

          `🧠 Reflection Complete\n\n` +

          `Reflection:\n${
              data.reflection?.reflection ||
              "No reflection"
          }\n\n` +

          `Belief:\n${
              data.belief?.belief ||
              "No belief"
          }\n\n` +

          `🔮 Prediction:\n${
              data.prediction?.prediction ||
              "No prediction"
          }`
      }

    ]);

    setTimeout(() => {

      chatEndRef.current?.scrollIntoView({
        behavior: "smooth"
      });

    }, 100);

  } catch (error) {

    console.error(error);

    setChat(prev => [

      ...prev,

      {
        sender: "System",
        text: "Unable to run cognition cycle."
      }

    ]);

  } finally {

    setReflecting(false);
  }
};

  // ==================================================
  // MAIN UI
  // ==================================================

  return (

    <div className={`app ${focusMode ? "focus-mode" : ""} ${emotionMode}`}>

      {/* ==================================================
          TOGGLE ORB
      ================================================== */}

      <button
        className="sidebar-toggle"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >

        {
          sidebarOpen
            ? <FaTimes />
            : <FaBars />
        }

      </button>

      {/* ==================================================
          FLOATING INSIGHT CAPSULE
      ================================================== */}

      <div
        className={
          sidebarOpen
            ? `sidebar open ${pulse ? "sidebar-pulse" : ""}`
            : `sidebar ${pulse ? "sidebar-pulse" : ""}`
        }
      >

        {/* LOGO */}

        <div className="logo">

          <div className="logo-orb"></div>

          <div>
            <h2>DigiT</h2>

            <span>You are the AI</span>
          </div>

        </div>

        {/* PERSONALITY */}

        <div className="sidebar-section">

          <h3>Personality</h3>

          <div className="identity-card">
            <p>{identity.personality}</p>
          </div>

        </div>

        {/* EMOTIONAL */}

        <div className="sidebar-section">

          <h3>Current State</h3>

          <div className="identity-card">
            <p>{identity.emotional}</p>
          </div>

        </div>

        {/* DRIVERS */}

        <div className="sidebar-section">

          <h3>Core Drivers</h3>

          <div className="identity-card">
            <p>{identity.drivers}</p>
          </div>

        </div>

        {/* FOCUS */}

        <div className="sidebar-section">

          <h3>Current Focus</h3>
          {/* EMOTIONAL TREND */}

           <div className="sidebar-section">

           <h3>Emotional Trend</h3>

            <div className="identity-card">
             <p>{identity.trend}</p>
            </div>

          </div>

{/* CONFIDENCE */}

<div className="sidebar-section">

  <h3>Confidence</h3>

  <div className="identity-card">
    <p>{identity.confidence}%</p>
  </div>

</div>

{/* STRESS */}

<div className="sidebar-section">

  <h3>Stress Level</h3>

  <div className="identity-card">
    <p>{identity.stress}%</p>
  </div>

</div>
          <div className="identity-card">
            <p>{identity.focus}</p>
          </div>

        </div>

      </div>

      {/* ==================================================
          MAIN CONTENT
      ================================================== */}

      <div className="main">

        {/* ==================================================
            HEADER
        ================================================== */}

        <div className="header">

          <div className="header-left">

            <div className="header-logo-orb"></div>

            <div>
              <h1>DigiT</h1>

              <span>You are the AI</span>
            </div>

          </div>

          {/* ==================================================
              HEADER ACTIONS
          ================================================== */}

          <div className="header-actions">

            {/* FOCUS MODE */}

            <button
              className="mode-button"
              onClick={() => setFocusMode(!focusMode)}
            >

              <FaBrain />

              {
                focusMode
                  ? "Exit Focus"
                  : "Focus Mode"
              }

            </button>
            <button
              className="mode-button"
              onClick={runCognition}
              disabled={reflecting}
            >

              {

                reflecting

                  ? "Reflecting..."

                  : "🧠 Reflect"

              }

            </button>

            {/* EMOTION MODES */}

            <button
              className="emotion-button"
              onClick={() => setEmotionMode("calm")}
            >
              Calm
            </button>

            <button
              className="emotion-button"
              onClick={() => setEmotionMode("intense")}
            >
              Intense
            </button>
            
            <button
              className="emotion-button"
              onClick={() => setEmotionMode("night")}
            >
              <FaMoon />
            </button>

            <button
              className="emotion-button"
              onClick={async () => {

                await supabase.auth.signOut();

                window.location.reload();
              }}
            >
              Logout
            </button>

          </div>

        </div>

        {/* ==================================================
            CHAT AREA
        ================================================== */}

        <div className="chat-box">

          {chat.map((msg, index) => (

            <div
              key={index}
              className={
                msg.sender === "You"
                  ? "user-message"
                  : "ai-message"
              }
            >

              <strong>{msg.sender}</strong>

              <div style={{ whiteSpace: "pre-wrap" }}>
                {msg.text}
              </div>

            </div>

          ))}

          {/* ==================================================
              LOADING
          ================================================== */}

          {loading && (

            <div className="typing">
              DigiT is reflecting...
            </div>
          )}

          <div ref={chatEndRef}></div>

        </div>

        {/* ==================================================
            INPUT AREA
        ================================================== */}

        <div className="input-area">

          <input
            type="text"

            placeholder="Talk to DigiT..."

            value={message}

            onChange={(e) => setMessage(e.target.value)}

            onKeyDown={(e) => {

              if (e.key === "Enter") {

                sendMessage();
              }

            }}
          />

          <button onClick={sendMessage}>
            Send
          </button>

        </div>

      </div>

    </div>
  );
}

export default App;