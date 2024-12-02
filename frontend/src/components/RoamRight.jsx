import React, { useState, useEffect } from "react";

import Messages from "./Messages";
import Input from "./Input";


import "./styles.css";

function RoamRight() {
    const [messages, setMessages] = useState([]);
    const [sessionData, setSessionData] = useState({ messages: [] }); // Initialize session with message history


    useEffect(() => {
        setMessages([{ sender: "bot", text: "Welcome! How can I assist you with your travel plans today? Please provide me destination, dates, and budget" }]);
    }, []);

    const send = async (text) => {
        const newMessages = [...messages, { sender: "user", text: text }];
        setMessages(newMessages);
        try {
            const response = await fetch("http://127.0.0.1:5000/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: text,
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
        <div className="chatbot">
            <div className="header">Roam Right</div>
            <Messages key={messages.length} messages={messages}/>
            <Input onSend={send} />
        </div>
    );
}

export default RoamRight;
