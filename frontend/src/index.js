import React from "react";

import ReactDOM from "react-dom/client";

import "./index.css";

import App from "./App";

import Auth from "./Auth";

import { supabase } from "./supabase";

import ErrorBoundary from "./ErrorBoundary";

const root = ReactDOM.createRoot(
  document.getElementById("root")
);

function Root() {

  const [session, setSession] = React.useState(undefined);

  React.useEffect(() => {

    // ==========================================
    // GET EXISTING SESSION
    // ==========================================

    supabase.auth.getSession()

      .then(({ data: { session } }) => {

        setSession(session);
      });

    // ==========================================
    // AUTH LISTENER
    // ==========================================

    const {

      data: listener

    } = supabase.auth.onAuthStateChange(

      (_event, session) => {

        setSession(session);
      }
    );

    return () => {

      listener.subscription.unsubscribe();
    };

  }, []);

  // ==========================================
  // LOADING
  // ==========================================

  if (session === undefined) {

    return null;
  }

  // ==========================================
  // ROUTING
  // ==========================================

  return session
    ? <App session={session} />
    : <Auth />;
}

root.render(

  <React.StrictMode>

    <ErrorBoundary>

      <Root />

    </ErrorBoundary>

  </React.StrictMode>
);