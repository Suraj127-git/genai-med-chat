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

  // Chat UI after login
  return (
    <div className="min-h-screen bg-[#0b0f14] text-gray-100 flex">
      <aside className="hidden md:flex md:w-64 flex-col bg-black/20 border-r border-white/10 p-3">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded bg-teal-500/30" />
            <span className="text-sm text-gray-300">Home</span>
          </div>
          <button className="text-xs text-gray-400">⋯</button>
        </div>
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-gray-300"><span className="text-lg">📚</span><span className="text-sm">Library</span></div>
          <div className="flex items-center gap-2 text-gray-300"><span className="text-lg">�</span><span className="text-sm">Academic</span></div>
          <div className="flex items-center gap-2 text-gray-300"><span className="text-lg">⚙️</span><span className="text-sm">Settings</span></div>
        </div>
        <div className="mt-auto pt-3 border-t border-white/10">
          <button className="w-full text-left text-xs text-gray-400">Upgrade</button>
        </div>
      </aside>
      <div className="flex-1 flex flex-col">
        <header className="h-14 border-b border-white/10 flex items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <span className="text-teal-400 font-semibold">perplexity</span>
            <span className="text-xs text-teal-300 bg-teal-600/20 px-2 py-0.5 rounded-full">pro</span>
          </div>
          <div className="flex items-center gap-2">
            <Button onClick={logout} className="text-xs bg-white/10 text-gray-300 px-3 py-1 rounded-lg">Logout</Button>
          </div>
        </header>
        <main className="flex-1 p-4">
          <Chat noShell />
        </main>
      </div>
    </div>
  );
};

export default App;
