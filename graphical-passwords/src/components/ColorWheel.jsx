import React from "react";

export default function ColorWheel({ colors, size, onClick, rotation = 0 }) {
    const numSlices = colors.length;
    const angle = 360 / numSlices;
    const radius = parseInt(size) / 2;
    const center = radius;

    return (
        <svg
            width={size}
            height={size}
            viewBox={`0 0 ${size} ${size}`}
            style={{ cursor: "pointer" }}
        >
            <g
                className="wheel-group"
                style={{
                    transformOrigin: "center",
                    transform: `rotate(${rotation}deg)`,
                    transition: "transform 0.7s ease-in-out"
                }}
            >
                {colors.map((color, index) => {
                    const startAngle = index * angle;
                    const endAngle = startAngle + angle;

                    const x1 = center + radius * Math.cos((startAngle * Math.PI) / 180);
                    const y1 = center + radius * Math.sin((startAngle * Math.PI) / 180);
                    const x2 = center + radius * Math.cos((endAngle * Math.PI) / 180);
                    const y2 = center + radius * Math.sin((endAngle * Math.PI) / 180);

                    return (
                        <path
                            key={index}
                            d={`M${center},${center} L${x1},${y1} A${radius},${radius} 0 0,1 ${x2},${y2} Z`}
                            fill={color}
                            stroke="white"
                            strokeWidth="2"
                            onClick={onClick}
                        />
                    );
                })}
            </g>
        </svg>
    );
}
