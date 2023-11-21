import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';


import React from 'react';
import { GoogleMap, Marker, useLoadScript } from '@react-google-maps/api';
import { useMemo } from "react";

const containerStyle = {
  width: '400px',
  height: '400px'
};

const Map = (prop) => {
    const { isLoaded } = useLoadScript({
        googleMapsApiKey: "AIzaSyDqOQUMvf6Tdsq_K7KdhHt6LqmsdChv2QI"
    });
    const center = useMemo(() => ({ lat: prop.lat, lng: prop.long }), []);

    return (
        <div className="App">
            {!isLoaded ? (
                <h1>Loading...</h1>
            ) : (
            <GoogleMap
                mapContainerClassName="map-container"
                center={center}
                zoom={10}
            >
                <Marker position={{ lat: prop.lat, lng: prop.long }} />
            </GoogleMap>
            )}
        </div>
    );
};

export default Map;
