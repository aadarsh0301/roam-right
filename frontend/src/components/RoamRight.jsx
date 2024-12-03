import React, { useState, useEffect } from "react";

import Messages from "./Messages";
import Input from "./Input";


import "./styles.css";

function RoamRight() {
    const [messages, setMessages] = useState([]);
    const [sessionData, setSessionData] = useState({ messages: [] }); // Initialize session with message history


    useEffect(() => {
        const firstMessage = "Hello there! 🌍✈️ <br>" +
            "Welcome to your personalized travel planner! I'm here to help you design the perfect getaway.<br><br>" +
            "To get started, please share:<br>" +
            "1. Your travel dates.<br>" +
            "2. Your dream destination(s).<br>" +
            "3. Your budget for this trip.<br><br>" +
            "Once I have these details, we can begin crafting your unforgettable adventure!"
        setMessages([
            {
                sender: "bot",
                text:firstMessage,
                type:"firstMessage"
            }])
        setSessionData({messages: [
                {"role": "user", "content": firstMessage}
            ]})
        fetch("http://127.0.0.1:5000/intialize", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: "Intialize"
            }),
        });
    }, []);
    const getAPIResponse = async (text, requestType, sessionData) => {
        console.log("Sending to API");
        console.log(text, sessionData, requestType);

        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: text,
                session_data: sessionData,  // Pass sessionData explicitly here
                type: requestType
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const { reply, updated_session_data, replyType } = data;
        console.log("Getting from API");
        console.log(reply, updated_session_data, replyType);

        // Update the messages with the bot's reply
        setMessages((prevMessages) => [
            ...prevMessages,
            { sender: "bot", text: reply, type: replyType},
        ]);

        // Overwrite the messages in sessionData with updated_session_data.messages
        setSessionData({
            messages: updated_session_data.messages, // Directly overwrite messages
        });

        // If the reply is confirmation, request itinerary
        if (replyType === "details_received") {
            // Pass the updated session data explicitly for the next API call
            getAPIResponse("Give Itinerary", "itinerary", updated_session_data);
        }
        if (replyType === "itinerary_reply") {
            // Pass the updated session data explicitly for the next API call
            getAPIResponse(reply, "map", updated_session_data);
        }
        // if (replyType === "map_reply") {
        //     // Pass the updated session data explicitly for the next API call
        //     getAPIResponse("", "Done", updated_session_data);
        // }
    };


    const send = async (text) => {
        const newMessages = [...messages, { sender: "user", text: text, type:"chat" }];
        setMessages(newMessages);
        try {
            getAPIResponse(text, "chat", sessionData);
            // Update session data for dynamic context

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
