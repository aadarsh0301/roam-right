import React, { useEffect, useRef } from "react";
export default function Messages({ messages}) {

  return (
    <div className="messages">
      {messages.length>0?messages.map((e,index)=> {
        return <div key={index} className="message-container">
          <div className={e.sender=="bot"?"bot-message":"user-message"} dangerouslySetInnerHTML={{__html: e.text}}/>
        </div>
      }) : <></>}
    </div>
  );
}
