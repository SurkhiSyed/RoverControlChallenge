//File for Making circular progress bars

import React from 'react'
import './displayInfo.css'

const CircularProgressbar = ({percentage, circleWidth}) => {
    //Define some math variables
    const strokeWidth = 15;
    const radius = (circleWidth - strokeWidth) / 2;
    const dashArray = radius * Math.PI * 2
    const dashOffset = dashArray - (dashArray * percentage) / 100


    //Implement the shapes using math vairables
    return (
        <div>
            <svg 
                width={circleWidth} 
                height={circleWidth} 
                viewBox={`0 0 ${circleWidth} ${circleWidth}`}
            >
                <circle 
                    cx={circleWidth / 2} 
                    cy={circleWidth / 2} 
                    strokeWidth='15px' 
                    r={radius}
                    className='circle-background'
                />

                <circle 
                    cx={circleWidth / 2} 
                    cy={circleWidth / 2} 
                    strokeWidth='15px' 
                    r={radius}
                    className='circle-progress'
                    style={{
                        strokeDasharray: dashArray,
                        strokeDashoffset: dashOffset,
                    }}
                    transform={`rotate(-90 ${circleWidth / 2} ${circleWidth / 2})`}
                />
                <text x='50%' y='50%' dy='0.3em' textAnchor='middle' className='circle-text'>
                    Throttle: {percentage}% 
                </text>
            </svg>
        </div>
    )
}

export default CircularProgressbar