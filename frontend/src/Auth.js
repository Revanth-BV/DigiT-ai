import React, { useState } from "react";
import "./Auth.css";
import { supabase } from "./supabase";

function Auth({ onLogin }) {

  const [isSignup, setIsSignup] = useState(false);

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  const handleAuth = async () => {

    setLoading(true);

    try {

      if (isSignup) {

        const { error } = await supabase.auth.signUp({

          email,
          password
        });

        if (error) {

          alert(error.message);

        } else {

          alert("Account created successfully.");
        }

      } else {

        const {

          data,
          error

        } = await supabase.auth.signInWithPassword({

          email,
          password
        });

        if (error) {

          alert(error.message);

        } else {

          onLogin(data.session);
        }
      }

    } catch (err) {

      console.error(err);

    } finally {

      setLoading(false);
    }
  };

  return (

    <div className="auth-page">

      <div className="auth-card">

        <div className="auth-logo">
          DigiT
        </div>

        <h1>
          You are the AI
        </h1>

        <p>
          Your adaptive digital consciousness.
        </p>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
        />

        <button
          onClick={handleAuth}
          disabled={loading}
        >
          {
            loading
              ? "Please wait..."
              : isSignup
                ? "Create Account"
                : "Enter DigiT"
          }
        </button>

        <div
          className="auth-toggle"
          onClick={() =>
            setIsSignup(!isSignup)
          }
        >
          {
            isSignup
              ? "Already have an account?"
              : "Create new account"
          }
        </div>

      </div>

    </div>
  );
}

export default Auth;