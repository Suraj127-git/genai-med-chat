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
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-100 via-white to-blue-200 relative overflow-hidden">
        {/* Floating circles for background motion */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-[-50px] left-[20%] w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
          <div className="absolute bottom-[-50px] right-[15%] w-80 h-80 bg-indigo-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
        </div>

        {/* Card */}
        <div
          ref={cardRef}
          className="relative z-10 w-full max-w-md bg-white/40 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl p-8"
        >
          <div className="text-center mb-6">
            <div ref={logoRef} className="inline-block mb-3">
              <img
                src="https://cdn-icons-png.flaticon.com/512/387/387561.png"
                alt="Medical Icon"
                className="w-12 h-12 mx-auto"
              />
            </div>
            <h1 className="text-3xl font-bold text-blue-700 tracking-tight">
              GenAI Medical Chat
            </h1>
            <p className="text-gray-600 mt-2 text-sm">
              {isRegistering
                ? "Create your secure account to get AI medical insights"
                : "Welcome back! Sign in to continue your medical conversations"}
            </p>
          </div>

          {/* Login/Register */}
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

          <div className="mt-6 text-center text-sm text-gray-600">
            {isRegistering ? (
              <p>
                Already have an account?{" "}
                <button
                  className="text-blue-600 hover:underline font-semibold"
                  onClick={() => setIsRegistering(false)}
                >
                  Login
                </button>
              </p>
            ) : (
              <p>
                Don’t have an account?{" "}
                <button
                  className="text-blue-600 hover:underline font-semibold"
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

  // Chat UI after login
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-blue-50 to-white">
      <header className="bg-white shadow-md p-4 flex justify-between items-center border-b border-blue-100">
        <h1 className="text-2xl font-semibold text-blue-700">🩺 GenAI Medical Chatbot</h1>
        <Button
          onClick={logout}
          variant="secondary"
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg"
        >
          Logout
        </Button>
      </header>
      <main className="flex-1 p-4 overflow-y-auto">
        <Chat />
      </main>
    </div>
  );
};

export default App;
