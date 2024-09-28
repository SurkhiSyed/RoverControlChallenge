//File to display terminals and speed of wheels

import React, { useEffect, useState, useRef } from 'react';
import 'react-circular-progressbar/dist/styles.css';
import CircularProgressbar from './circularProgressbar';
import './displayInfo.css';

const WheelDisplay = () => {
    const [wheelData, setWheelData] = useState({
        left_wheels: [],
        right_wheels: [],
        wheel_Data: [],
        elbowMovement: [],
        wristRotation: [],
        shoulderRotation: []
    });
    const [input, setInput] = useState("");
    const [output, setOutput] = useState("");
    const [outputControls, setOutputControls] = useState("");
    const [isSocketOpen, setIsSocketOpen] = useState(false); // Track WebSocket connection status

    const inputRef = useRef();
    const socketRef = useRef(null);

    // function for calculating the color
    const [percentage1, setPercentage1] = useState(100); //Set the percentages to 100% intirially
    const [percentage2, setPercentage2] = useState(100);

    //To call out the motor speeds of different ocmponentes called from the backend python file
    const speedLeft_percentage = Math.round((wheelData.left_wheels.length > 0 ? wheelData.left_wheels[0] : 0) * 100 / 255);
    const speedRight_percentage = Math.round((wheelData.right_wheels.length > 0 ? wheelData.right_wheels[0] : 0) * 100 / 255);
    const elbowSpeed_percentage = Math.round((wheelData.elbowMovement.length > 0 ? wheelData.elbowMovement[0] : 0) * 100 / 255);
    const wristRotation_percentage = Math.round((wheelData.wristRotation.length > 0 ? wheelData.wristRotation[0] : 0) * 100 / 255);
    const shoulderRotation_percentage = Math.round((wheelData.shoulderRotation.length > 0 ? wheelData.shoulderRotation[0] : 0) * 100 / 255);

    console.log(percentage1);

    useEffect(() => {
        // Create a WebSocket connection
        socketRef.current = new WebSocket('ws://localhost:5000');

        // Listen for the open event
        socketRef.current.onopen = () => {
            setIsSocketOpen(true);
        };

        // Listen for messages from the server
        socketRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setWheelData(data);
            console.log(data);

            // Update outputControls with the latest data at the top
            setOutputControls(prevOutput => {
                const newOutputWheels = Array.isArray(data.wheel_Data) ? data.wheel_Data.join(', ') : '';
                const newOutputArms = Array.isArray(data.arm_data) ? data.arm_data.join(', ') : '';
                return newOutputWheels + "\n" + newOutputArms + "\n" + prevOutput;
            });
        };

        // Clean up the connection when the component unmounts
        return () => {
            socketRef.current.close();
        };
    }, []);

    useEffect(() => {
        inputRef.current.focus();
    }, []);

    //To send the percentage data to the backend python file
    const sendPercentageData = () => {
        if (isSocketOpen) {
            const data = {
                percentage1,
                percentage2
            };
            socketRef.current.send(JSON.stringify(data));
        }
    };

    //To change the percentage data
    useEffect(() => {
        sendPercentageData();
    }, [percentage1, percentage2]);

    return (
        <div className="card-container">            
            <div className="card">
                <h3>Left Wheels:</h3>
                <p>{wheelData.left_wheels.join(', ')}</p>
                <h3>Right Wheels:</h3>
                <p>{wheelData.right_wheels.join(', ')}</p>
                <div className='speedDisplay'>
                    <CircularProgressbar
                        percentage={speedLeft_percentage}
                        circleWidth='200'
                    />
                    <CircularProgressbar
                        percentage={speedRight_percentage}
                        circleWidth='200'
                    />
                </div>
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
                <h2 className="card-title"></h2>
                <p className="card-summary"></p>
                <p>Elbow Movement | Wrist Rotation | Shoulder Rotation</p>
                <div className='speedDisplay'>
                    <CircularProgressbar
                        percentage={elbowSpeed_percentage}
                        circleWidth='150'
                    />
                    <CircularProgressbar
                        percentage={wristRotation_percentage}
                        circleWidth='150'
                    />
                    <CircularProgressbar
                        percentage={shoulderRotation_percentage}
                        circleWidth='150'
                    />
                </div>
                <h3>Arm Speed</h3>
                <input
                    type='range'
                    min='0'
                    max='100'
                    step='1'
                    value={percentage2}
                    className='rightWheelsInput'
                    onChange={(ev) => setPercentage2(ev.target.value)}
                />
            </div>
            <div className="card"> {/* For outputting controls */}
                <div className="terminal-holder">
                    <div className="terminal-output">
                        {outputControls}
                        console.log(outputControls);
                    </div>
                </div>
                Input Terminal
                <div className="terminal-holder">
                    <input 
                        ref={inputRef}
                        type="text" 
                        value={input} 
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => {
                            if (e.key === 'Enter') {
                                let newOutput = "$" + input + " ";
                                switch (input) {
                                    case "help":
                                        newOutput += "--> Input Control To Change: Leftwheels, Rightwheels";
                                        break;
                                    case "ct":
                                        newOutput = ""; // Clear the terminal output
                                        setOutput(prevOutput => "");
                                        break;
                                    default:
                                        newOutput += "--> command not found";
                                        break;
                                }
                                newOutput += "\n";
                                setOutput(prevOutput => newOutput + prevOutput);
                                setInput('');
                            }
                        }}
                    />
                    <div className="terminal-output">
                        {output}
                    </div>
                </div>
            </div>
        </div>   
    );
};

export default WheelDisplay;