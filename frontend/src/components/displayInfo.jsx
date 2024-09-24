import React, { useEffect, useState } from 'react';
import 'react-circular-progressbar/dist/styles.css'
import CircularProgressbar from './circularProgressbar';
import './displayInfo.css';



const WheelDisplay = () => {
    const [wheelData, setWheelData] = useState({ left_wheels: [], right_wheels: [] });

    // function for calculating the color
    const [percentage1, setPercentage1] = useState(35);

    const speedLeft_percentage = Math.round((wheelData.left_wheels.length > 0 ? wheelData.left_wheels[0] : 0) * 100 / 255);
    const speedRight_percentage = Math.round((wheelData.right_wheels.length > 0 ? wheelData.right_wheels[0] : 0) * 100 / 255);
    console.log(percentage1)

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
            <div className="card">
                <h3>Left Wheels:</h3>
                <p>{wheelData.left_wheels.join(', ')}</p>
                <h3>Right Wheels:</h3>
                <p>{wheelData.right_wheels.join(', ')}</p>
                <div className='speedDisplay'>
                    <CircularProgressbar
                        percentage={speedLeft_percentage}
                        circleWidth = '200'
                    />
                    <CircularProgressbar
                        percentage={percentage1}
                        circleWidth = '200'
                    />
                    <h3>Wheel Speed</h3>
                    <input
                        type='range'
                        min='0'
                        max='100'
                        step='1'
                        value={percentage1}
                        className='rightWheelsInput'
                        onChange={(ev) => setPercentage1(ev.target.value)}
                    />
                </div>
                <h2 className="card-title"></h2>
                <p className="card-summary"></p>
                <p className="card-publisher">Published by:</p>
            </div>
        </div>   
    );
};

export default WheelDisplay;
