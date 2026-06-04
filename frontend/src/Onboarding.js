import React, { useState } from "react";
import "./Onboarding.css";

const questions = [

  "What motivates you the most right now?",

  "How do you usually handle pressure or uncertainty?",

  "What kind of future are you working toward?",

  "What do you value more: stability or growth?",

  "What’s something people often misunderstand about you?"
];

function Onboarding({ onComplete }) {

  const [started, setStarted] = useState(false);

  const [currentQuestion, setCurrentQuestion] = useState(0);

  const [input, setInput] = useState("");

  const [answers, setAnswers] = useState([]);

  const [buildingTwin, setBuildingTwin] = useState(false);

  // =========================================
  // NEXT QUESTION
  // =========================================

  const nextQuestion = () => {

    if (!input.trim()) return;

    const updatedAnswers = [

      ...answers,

      {
        question: questions[currentQuestion],
        answer: input
      }
    ];

    setAnswers(updatedAnswers);

    setInput("");

    // NEXT QUESTION

    if (currentQuestion < questions.length - 1) {

      setCurrentQuestion(prev => prev + 1);
    }

    // COMPLETE

    else {

      setBuildingTwin(true);

      setTimeout(() => {

        onComplete(updatedAnswers);

      }, 3500);
    }
  };

  // =========================================
  // INTRO SCREEN
  // =========================================

  if (!started) {

    return (

      <div className="onboarding-page">

        <div className="ambient-glow glow-one"></div>

        <div className="ambient-glow glow-two"></div>

        <div className="intro-content">

          <div className="intro-badge">
            DigiT • You('R') AI
          </div>

          <h1>
            Meet DigiT
          </h1>

          <p>
            An adaptive AI built around
            your personality, thoughts, and decisions.
          </p>

          <button
            className="begin-button"
            onClick={() => setStarted(true)}
          >
            Initialize DigiT
          </button>

        </div>

      </div>
    );
  }

  // =========================================
  // BUILDING DIGIT
  // =========================================

  if (buildingTwin) {

    return (

      <div className="onboarding-page">

        <div className="ambient-glow glow-one"></div>

        <div className="ambient-glow glow-two"></div>

        <div className="build-container">

          <div className="neural-orb">

            <div className="ring ring-1"></div>

            <div className="ring ring-2"></div>

            <div className="ring ring-3"></div>

            <div className="core"></div>

          </div>

          <h2>
            Initializing DigiT
          </h2>

          <p>
            Building your adaptive identity profile
            based on behavioral and conversational patterns.
          </p>

        </div>

      </div>
    );
  }

  // =========================================
  // QUESTIONS
  // =========================================

  return (

    <div className="onboarding-page">

      <div className="ambient-glow glow-one"></div>

      <div className="ambient-glow glow-two"></div>

      <div className="question-wrapper">

        <div className="question-progress">

          <div
            className="progress-fill"
            style={{
              width:
                `${((currentQuestion + 1) / questions.length) * 100}%`
            }}
          ></div>

        </div>

        <div className="question-count">
          Question {currentQuestion + 1}
          {" "}of{" "}
          {questions.length}
        </div>

        <h2 className="question-text">
          {questions[currentQuestion]}
        </h2>

        <div className="thought-input-container">

          <textarea
            placeholder="Type what comes naturally..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

        </div>

        <button
          className="continue-button"
          onClick={nextQuestion}
        >
          Continue
        </button>

      </div>

    </div>
  );
}

export default Onboarding;