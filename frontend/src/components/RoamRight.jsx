import React, { useState, useEffect } from "react";
import bg from './bg1.jpg';

function RoamRight() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [sessionData, setSessionData] = useState({ messages: [] }); // Initialize session with message history

    useEffect(() => {
        setMessages([{ sender: "bot", text: "Welcome! How can I assist you with your travel plans today?" }]);
    }, []);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = input.trim();
        setMessages((prevMessages) => [
            ...prevMessages,
            { sender: "user", text: userMessage },
        ]);
        setInput("");

        try {
            const response = await fetch("http://127.0.0.1:5000/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: userMessage,
                    session_data: sessionData,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            const { reply, session_data } = data;

            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "bot", text: reply },
            ]);

            // Update session data for dynamic context
            setSessionData(session_data);
        } catch (error) {
            console.error("Error communicating with the server:", error);
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "bot", text: "Sorry, something went wrong. Please try again." },
            ]);
        }
    };

    return (
        <div
            style={{
                padding: "20px",
                backgroundColor: "#121212",
                color: "#FFFFFF",
                height: "98vh",
                backgroundImage: `url(${bg})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat",
            }}
        >
            <h1 style={{ textAlign: "center", color: "#FFD700" }}>ROAM RIGHT</h1>
            <div
                style={{
                    border: "1px solid #444",
                    backgroundColor: "#1E1E1E",
                    padding: "10px",
                    height: "600px",
                    overflowY: "scroll",
                    marginBottom: "10px",
                    opacity: 0.85,
                }}
            >
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        style={{
                            textAlign: msg.sender === "user" ? "right" : "left",
                            marginBottom: "5px",
                        }}
                    >
                        <strong style={{ color: msg.sender === "user" ? "#1E90FF" : "#FFD700" }}>
                            {msg.sender === "user" ? "You" : "Bot"}:
                        </strong>{" "}
                        <span
                            style={{color: "#FFFFFF"}}
                            dangerouslySetInnerHTML={{__html: msg.text}}
                        />
                    </div>
                ))}
            </div>
            <div style={{width: "100%" }}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && sendMessage()}
                    placeholder="Type your message..."
                    style={{
                        width: "92%",
                        padding: "10px",
                        marginRight: "10px",
                        border: "1px solid #555",
                        borderRadius: "4px",
                        backgroundColor: "#1E1E1E",
                        color: "#FFFFFF",
                        opacity: 0.95,
                    }}
                />
                <button
                    onClick={sendMessage}
                    style={{
                        padding: "10px 20px",
                        width: "5%",
                        backgroundColor: "#1E90FF",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                    }}
                >
                    Send
                </button>
            </div>
        </div>
    );
}

export default RoamRight;
