import React, { useState, useRef, useEffect } from "react";
import { postForm } from "@genai-med-chat/shared";
import { useDispatch, useSelector } from "react-redux";
import { addMessage, sendChatQuery, fetchGraph } from "@genai-med-chat/store";
import Sidebar from "./Sidebar.jsx";
import MessageList from "./MessageList.jsx";
import Composer from "./Composer.jsx";
import GraphModal from "./GraphModal.jsx";
import Appointments from "./Appointments.jsx";
import Profile from "./Profile.jsx";

export default function Chat({ noShell = false, onLogout = null }) {
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
  const [active, setActive] = useState("interview");

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollTop = chatEndRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (text = input) => {
    if (!text.trim()) return;
    dispatch(addMessage({ sender: "user", content: text }));
    setInput("");

    const res = await dispatch(
      sendChatQuery({ text, conv_id: lastConvId })
    );
    if (res.error) {
      dispatch(addMessage({ sender: "bot", content: "❌ Unable to fetch response" }));
    }
  };

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
          const res = await postForm("/api/v1/voice", formData);
          if (res.text) await handleSend(res.text);
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

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await postForm("/api/v1/ocr", formData);
      if (res.text) await handleSend(res.text);
    } catch (err) {
      console.error(err);
      alert("OCR failed to process image");
    }
  };

  const handleShowGraph = async () => {
    if (!lastConvId) return alert("No conversation yet!");
    const res = await dispatch(fetchGraph(lastConvId));
    if (!res.error) setShowGraph(true);
  };

  const renderInterview = () => (
    messages.length === 0 ? (
      <div className="flex-1 grid place-items-center px-4">
        <div className="w-full max-w-2xl">
          <div className="text-center mb-6">
            <div className="text-3xl font-semibold text-teal-400">GenAI Medical Assistant</div>
            <div className="text-sm text-gray-400 mt-1">Ask anything. Type @ for mentions and / for shortcuts.</div>
          </div>
          <Composer
            value={input}
            onChange={setInput}
            onSubmit={() => handleSend()}
            onVoice={handleVoice}
            recording={recording}
            onUpload={handleFileUpload}
            onGraph={handleShowGraph}
            loading={loading}
          />
        </div>
      </div>
    ) : (
      <div className="flex-1 flex flex-col items-center">
        <div className="w-full max-w-3xl flex-1">
          <MessageList refEl={chatEndRef} messages={messages} loading={loading} />
        </div>
        <div className="w-full max-w-3xl px-4 pb-4">
          <Composer
            value={input}
            onChange={setInput}
            onSubmit={() => handleSend()}
            onVoice={handleVoice}
            recording={recording}
            onUpload={handleFileUpload}
            onGraph={handleShowGraph}
            loading={loading}
          />
        </div>
      </div>
    )
  );

  return (
    <div className={`w-full min-h-[70vh] bg-[#0b0f14] text-gray-100 ${noShell ? "" : "flex"} rounded-2xl overflow-hidden`}>
      {!noShell && <Sidebar active={active} onSelect={setActive} />}
      <div className="flex-1 flex flex-col">
        {!noShell && (
          <header className="h-14 border-b border-white/10 flex items-center justify-between px-4">
            <div className="flex items-center gap-2">
              <span className="text-teal-400 font-semibold capitalize">{active}</span>
              <span className="text-xs text-teal-300 bg-teal-600/20 px-2 py-0.5 rounded-full">pro</span>
            </div>
            <div className="flex items-center gap-2">
              {onLogout && (
                <button onClick={onLogout} className="text-xs bg-white/10 text-gray-300 px-3 py-1 rounded-lg">Logout</button>
              )}
            </div>
          </header>
        )}

        {noShell ? renderInterview() : (
          active === "interview" ? renderInterview() : (
            active === "appointments" ? <Appointments /> : <Profile />
          )
        )}

        {showGraph && (
          <GraphModal onClose={() => setShowGraph(false)} graph={graph} convId={lastConvId} />
        )}

        {showGraph && (
          <GraphModal onClose={() => setShowGraph(false)} graph={graph} convId={lastConvId} />
        )}
      </div>
    </div>
  );
}
