import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import gsap from "gsap";
import { useDispatch, useSelector } from "react-redux";
import { addMessage, sendChatQuery, fetchGraph } from "@genai-med-chat/store";

export default function Chat() {
  const dispatch = useDispatch();
  const messages = useSelector((state) => state.chat.messages);
  const loading = useSelector((state) => state.chat.loading);
  const lastConvId = useSelector((state) => state.chat.lastConvId);
  const graph = useSelector((state) => state.chat.graph);
  const user = useSelector((state) => state.auth.user);

  const [input, setInput] = useState("");
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const [audioChunks, setAudioChunks] = useState([]);
  const [showGraph, setShowGraph] = useState(false);
  const chatEndRef = useRef(null);

  // 🩺 Scroll to bottom on new message
  useEffect(() => {
    gsap.to(chatEndRef.current, {
      scrollTo: { y: chatEndRef.current.scrollHeight },
      duration: 0.6,
      ease: "power2.out",
    });
  }, [messages]);

  // 🧠 Handle send text message
  const handleSend = async (text = input) => {
    if (!text.trim()) return;
    // Push user message to store
    dispatch(addMessage({ sender: "user", content: text }));
    setInput("");

    const userId = user?.id || 1;
    const res = await dispatch(
      sendChatQuery({ user_id: userId, text, conv_id: lastConvId })
    );
    if (res.error) {
      dispatch(addMessage({ sender: "bot", content: "❌ Unable to fetch response" }));
    }
  };

  // 🎙 Voice recording
  const handleVoice = async () => {
    if (recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      setAudioChunks([]);
      setRecording(true);

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) setAudioChunks((prev) => [...prev, e.data]);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("file", audioBlob, "voice.webm");

        try {
          const res = await axios.post("/api/v1/voice", formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });
          if (res.data.text) await handleSend(res.data.text);
        } catch (err) {
          console.error(err);
          dispatch(addMessage({ sender: "bot", content: "🎙 Voice processing failed." }));
        }
      };

      mediaRecorder.start();
    } catch (err) {
      console.error(err);
      alert("Microphone access denied or unavailable.");
    }
  };

  // 📄 OCR upload
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("/api/v1/ocr", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (res.data.text) await handleSend(res.data.text);
    } catch (err) {
      console.error(err);
      alert("OCR failed to process image");
    }
  };

  // 🧩 Fetch reasoning graph
  const handleShowGraph = async () => {
    if (!lastConvId) return alert("No conversation yet!");
    const res = await dispatch(fetchGraph(lastConvId));
    if (!res.error) setShowGraph(true);
  };

  return (
    <div className="max-w-2xl mx-auto p-4 md:p-6 bg-gradient-to-br from-blue-50 via-white to-blue-100 rounded-3xl shadow-inner relative">
      {/* Header */}
      <header className="flex justify-center items-center mb-4">
        <h2 className="text-2xl font-bold text-blue-700 flex items-center gap-2">
          🧬 GenAI Medical Assistant
        </h2>
      </header>

      {/* Chat messages */}
      <div
        ref={chatEndRef}
        className="bg-white/70 backdrop-blur-md rounded-2xl shadow-inner border border-blue-100 p-4 h-[420px] overflow-y-auto space-y-3 transition-all"
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"} animate-fadeIn`}
          >
            <div
              className={`px-4 py-2.5 rounded-2xl shadow-sm max-w-[80%] text-sm ${
                msg.sender === "user"
                  ? "bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-br-none"
                  : "bg-gray-100 text-gray-800 rounded-bl-none"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-600 px-4 py-2.5 rounded-2xl rounded-bl-none animate-pulse">
              Thinking...
            </div>
          </div>
        )}
      </div>

      {/* Input section */}
      <div className="mt-4 flex items-center gap-2">
        <input
          type="text"
          value={input}
          placeholder="Ask a medical question..."
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          className="flex-1 bg-white/80 border border-gray-300 rounded-xl px-4 py-2.5 shadow-sm focus:ring-2 focus:ring-blue-400 focus:outline-none transition-all"
        />
        <button
          onClick={() => handleSend()}
          className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-5 py-2.5 rounded-xl shadow-md hover:shadow-lg hover:scale-105 transition-all"
        >
          ➤
        </button>
      </div>

      {/* Control bar */}
      <div className="flex justify-between mt-4 text-sm">
        <button
          onClick={handleVoice}
          className={`px-4 py-2.5 rounded-xl shadow-sm transition-all flex items-center gap-2 ${
            recording
              ? "bg-red-500 text-white animate-pulse"
              : "bg-green-500 text-white hover:bg-green-600"
          }`}
        >
          {recording ? "⏹ Stop" : "🎙 Voice"}
        </button>

        <label
          htmlFor="ocrInput"
          className="cursor-pointer bg-yellow-400 text-white px-4 py-2.5 rounded-xl hover:bg-yellow-500 shadow-sm transition-all"
        >
          📄 Upload
        </label>
        <input
          type="file"
          accept="image/*"
          id="ocrInput"
          className="hidden"
          onChange={handleFileUpload}
        />

        <button
          onClick={handleShowGraph}
          className="bg-purple-500 text-white px-4 py-2.5 rounded-xl hover:bg-purple-600 shadow-sm transition-all"
        >
          🧠 Graph
        </button>
      </div>

      {/* Graph Modal */}
      {showGraph && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-white/90 rounded-2xl p-6 shadow-2xl w-[90%] max-w-lg overflow-auto max-h-[80vh] relative">
            <button
              onClick={() => setShowGraph(false)}
              className="absolute top-2 right-3 text-gray-500 hover:text-gray-700"
            >
              ✖
            </button>
            <h3 className="text-lg font-bold text-blue-700 mb-2">
              🧠 Reasoning Graph (Conv: {lastConvId})
            </h3>
            <pre className="text-xs bg-gray-50 border border-gray-200 rounded-lg p-3 overflow-auto">
              {JSON.stringify(graph, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
