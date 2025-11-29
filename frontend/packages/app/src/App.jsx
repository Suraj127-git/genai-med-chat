import React, { useState, useEffect, useRef } from "react";
import { AuthProvider, useAuth, LoginForm, RegisterForm } from "@genai-med-chat/auth";
import { Chat } from "@genai-med-chat/chat";
import { Button } from "@genai-med-chat/shared";
import gsap from "gsap";

const App = () => (
  <AuthProvider>
    <Main />
  </AuthProvider>
);

const Main = () => {
  const { user, logout, login, register } = useAuth();
  const [isRegistering, setIsRegistering] = useState(false);

  const cardRef = useRef(null);
  const logoRef = useRef(null);

  useEffect(() => {
    // Fade in the main card and logo on mount
    gsap.fromTo(
      cardRef.current,
      { opacity: 0, y: 50, scale: 0.9 },
      { opacity: 1, y: 0, scale: 1, duration: 1, ease: "power3.out" }
    );
    gsap.to(logoRef.current, {
      y: -10,
      duration: 2,
      ease: "power1.inOut",
      yoyo: true,
      repeat: -1,
    });
  }, []);

  if (!user) {
    return (
      <div className="min-h-screen bg-[#0b0f14] text-gray-100 grid place-items-center">
        <div
          ref={cardRef}
          className="w-full max-w-md bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl"
        >
          <div className="text-center mb-6">
            <div ref={logoRef} className="inline-block mb-3">
              <div className="w-12 h-12 rounded-lg bg-teal-600/30 grid place-items-center text-teal-300">🧬</div>
            </div>
            <h1 className="text-2xl font-semibold text-teal-300">GenAI Medical Chat</h1>
            <p className="text-gray-400 mt-1 text-sm">
              {isRegistering ? "Create your account" : "Welcome back! Sign in"}
            </p>
          </div>

          <div className="transition-all duration-500">
            {isRegistering ? (
              <RegisterForm
                onRegister={async (userData) => {
                  await register(userData);
                }}
                onSwitchToLogin={() => setIsRegistering(false)}
              />
            ) : (
              <LoginForm
                onLogin={async (credentials) => {
                  await login(credentials);
                }}
                onSwitchToRegister={() => setIsRegistering(true)}
              />
            )}
          </div>

          <div className="mt-6 text-center text-sm text-gray-400">
            {isRegistering ? (
              <p>
                Already have an account?{" "}
                <button
                  className="text-teal-300 hover:underline font-semibold"
                  onClick={() => setIsRegistering(false)}
                >
                  Login
                </button>
              </p>
            ) : (
              <p>
                Don’t have an account?{" "}
                <button
                  className="text-teal-300 hover:underline font-semibold"
                  onClick={() => setIsRegistering(true)}
                >
                  Register
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0b0f14] text-gray-100 p-4">
      <Chat onLogout={logout} />
    </div>
  );
};

export default App;
