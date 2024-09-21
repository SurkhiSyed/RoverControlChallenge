import React, { useEffect, useState } from 'react';

const WheelDisplay = () => {
    const [wheelData, setWheelData] = useState({ left_wheels: [], right_wheels: [] });

    useEffect(() => {
        // Create a WebSocket connection
        const socket = new WebSocket('ws://localhost:5000');

        // Listen for messages from the server
        socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setWheelData(data);
        };

        // Clean up the connection when the component unmounts
        return () => {
        socket.close();
        };
    }, []);

    return (
        <div>
        <h3>Left Wheels:</h3>
        <p>{wheelData.left_wheels.join(', ')}</p>
        <h3>Right Wheels:</h3>
        <p>{wheelData.right_wheels.join(', ')}</p>
        </div>
    );
};

export default WheelDisplay;
