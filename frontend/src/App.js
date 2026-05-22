import React, { useState, useRef } from "react";
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

  const [message, setMessage] = useState("");

  const [chat, setChat] = useState([
    {
      sender: "DigiT",
      text:
        "Your Digital Twin is initialized. I’m beginning to understand how you think."
    }
  ]);

  const [loading, setLoading] = useState(false);

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
  useEffect(() => {

  const fetchProfile = async () => {

    const response = await fetch(

      `http://127.0.0.1:8000/identity/${session.user.id}`
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

        `http://127.0.0.1:8000/identity/${session.user.id}`
      );

      const identity = await response.json();

      // ==========================================
      // UPDATE ONBOARDING STATUS
      // ==========================================

      identity.onboarding_completed = true;

      // ==========================================
      // SAVE UPDATED PROFILE
      // ==========================================

      await fetch(

        "http://127.0.0.1:8000/save-identity",

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

      "http://127.0.0.1:8000/stream-chat",

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
              profile.stable_traits?.join(" • ")
              || "Unknown",

              emotional:
              profile.emotional_state
              || "Neutral",

              drivers:
              profile.core_drivers?.join(" • ")
              || "Undefined",

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