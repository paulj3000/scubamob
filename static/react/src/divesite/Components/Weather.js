import React from 'react';

const Weather = (prop) => {
    return (
        <>
            <img src={prop.weather.condition.icon} alt={prop.weather.condition.text} />
        </>
    );
};

export default Weather;
