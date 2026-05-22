import React from "react";

class ErrorBoundary extends React.Component {

  constructor(props) {

    super(props);

    this.state = {
      hasError: false
    };
  }

  static getDerivedStateFromError() {

    return {
      hasError: true
    };
  }

  componentDidCatch(error) {

    console.error(error);
  }

  render() {

    if (this.state.hasError) {

      return (

        <div
          style={{
            height: "100vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            background: "#050816",
            color: "white",
            fontSize: "20px"
          }}
        >
          DigiT encountered an unexpected issue.
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;