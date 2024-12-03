import React, { useState, useEffect , useRef} from "react";
import Typewriter from "typewriter-effect";
import { MapContainer, TileLayer, Marker, Polyline } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet"; // Import Leaflet for custom icons
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import markerRetina from "leaflet/dist/images/marker-icon-2x.png";

// Fix the default marker icon paths
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerRetina,
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
});

export default function Messages({ messages }) {
    const messagesEndRef = useRef(null); // Create a reference to the bottom of the container

    const scrollToBottom = () => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" }); // Scroll to the referenced element
        }
    };

    useEffect(() => {
        scrollToBottom(); // Scroll down whenever messages change
    }, [messages]);
    const [htmlContent, setHtmlContent] = useState("");
    // const messages1 = [
    //     { sender: "user", type: "text", text: "Show me directions." },
    //     {
    //         sender: "bot",
    //         type: "map",
    //         text: JSON.stringify([
    //             {
    //                 from_name: "Point A",
    //                 from_lat: 21.23,
    //                 from_lon: 21.234,
    //                 to_name: "Point B",
    //                 to_lat: 23.23,
    //                 to_lon: 23.234,
    //             },
    //             {
    //                 from_name: "Point C",
    //                 from_lat: 29.23,
    //                 from_lon: 29.234,
    //                 to_name: "Point D",
    //                 to_lat: 25.23,
    //                 to_lon: 27.234,
    //             },
    //         ]),
    //     },
    // ];

    useEffect(() => {
        // Reset htmlContent when a new bot message is received
        if (messages.length > 0 && messages[messages.length - 1].sender === "bot") {
            setHtmlContent("");
        }
    }, [messages]);

    const createLabel = (name) => {
        return L.divIcon({
            className: "leaflet-label", // Optional: use a class for custom styling
            html: `<div class="label-text" style="background-color: white; color: black; padding: 5px; border-radius: 5px; font-size: 14px; font-weight: bold; text-align: center;">${name}</div>`, // Inline styles
            iconSize: [100, 40], // Size of the label box
            iconAnchor: [50, 20], // Center the label over the marker
        });
    };

    const renderMap = (data) => {
        let points;

        // Safely parse the JSON and handle errors
        try {
            points = JSON.parse(data);
        } catch (error) {
            console.error("Invalid JSON data for map:", error);
            return <div>Error: Unable to load map data.</div>;
        }

        // Validate and filter out invalid points
        const validPoints = points.filter((point) =>
            point.from_lat !== undefined &&
            point.from_lon !== undefined &&
            point.to_lat !== undefined &&
            point.to_lon !== undefined
        );

        if (validPoints.length === 0) {
            return <div>No valid data to display on the map.</div>;
        }

        const fromMarkers = validPoints.map((point) => ({
            position: [point.from_lat, point.from_lon],
            name: point.from_name,
        }));

        const toMarkers = validPoints.map((point) => ({
            position: [point.to_lat, point.to_lon],
            name: point.to_name,
        }));

        const polylinePoints = validPoints.flatMap((point) => [
            [point.from_lat, point.from_lon],
            [point.to_lat, point.to_lon],
        ]);

        // Create bounds to include all points
        const allMarkers = [...fromMarkers, ...toMarkers];
        const bounds = L.latLngBounds(allMarkers.map((marker) => marker.position));

        return (
            <MapContainer
                center={bounds.getCenter()} // Center the map based on all markers
                //zoom={2} // Set a default zoom level
                style={{ height: "400px", width: "100%" }}
                bounds={bounds} // Set the map's bounds to include all points
                whenCreated={(map) => map.fitBounds(bounds)} // Adjust zoom to fit all markers
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                {/* Render markers for 'from' locations with custom labels */}
                {fromMarkers.map((marker, index) => (
                    <Marker
                        key={`from-${index}`}
                        position={marker.position}
                        icon={createLabel(marker.name)} // Use custom label for 'from' markers
                    />
                ))}
                {/* Render markers for 'to' locations with custom labels */}
                {toMarkers.map((marker, index) => (
                    <Marker
                        key={`to-${index}`}
                        position={marker.position}
                        icon={createLabel(marker.name)} // Use custom label for 'to' markers
                    />
                ))}
                {/* Render polyline between the points */}
                <Polyline positions={polylinePoints} color="blue" />
            </MapContainer>
        );
    };


    return (
        <div className="messages">
            {messages.length > 0 &&
                messages.map((e, index) => (
                    <div key={index} className="message-container">
                        {e.type === "map_reply" ? (
                            renderMap(e.text) // Render the map for messages of type 'map'
                        ) : e.sender === "bot" && index === messages.length - 1 ? (
                            <>
                                <div className="bot-message">
                                    <Typewriter
                                        onInit={(typewriter) => {
                                            typewriter
                                                .typeString(e.text) // The message to type out
                                                .callFunction(() => {
                                                    setHtmlContent(e.text); // Set the HTML content after typing is done
                                                })
                                                .start();
                                        }}
                                        options={{
                                            delay: 10, // Typing speed
                                        }}
                                    />
                                </div>
                                {e.type == "details_received" ? <div className="bot-message"><Typewriter
                                onInit={(typewriter) => {
                                    setTimeout(()=>{ typewriter
                                               .typeString("Generating Itinerary. Please Wait ...") // The message to type out
                                               .callFunction(() => {
                                                   setHtmlContent("Generating Itinerary. Please Wait ..."); // Set the HTML content after typing is done
                                               })
                                               .start();
                                    },1500)
                                    }}
                                    options={{
                                        delay: 10, // Typing speed
                                    }}
                                /></div> : <></>
                                }
                            </>
                        ) : (
                            <div
                                className={e.sender === "bot" ? "bot-message" : "user-message"}
                                dangerouslySetInnerHTML={{__html: e.text}} // Render HTML content for all messages
                            />
                        )}
                    </div>
                ))}
            <div ref={messagesEndRef}/>
        </div>
    );
}
