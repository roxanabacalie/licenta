import React, { useEffect, useState } from 'react';
import { APIProvider, Map, Marker, useMapsLibrary } from '@vis.gl/react-google-maps';
import './HomePage.css';

function HomePage() {
  const position = { lat: 47.19052, lng: 27.55848 };
  const [map, setMap] = useState(null);
  const [directionsService, setDirectionsService] = useState(null);
  
  useEffect(() => {
    if (map && directionsService) {
      drawRoutesFromCSV();
    }
  }, [map, directionsService]);

  const drawRoutesFromCSV = async () => {
    const response = await fetch('../static/stops_data.csv');
    const data = await response.text();
    const stops = parseCSV(data);

    if (stops.length >= 2) {
      for (let i = 0; i < 10; i++) {
        const start = new google.maps.LatLng(stops[i].lat, stops[i].lng);
        const end = new google.maps.LatLng(stops[i + 1].lat, stops[i + 1].lng);
        drawRoute(start, end, getRandomColor());
      }
    }
  };

  const saveDirectionsToFile = (response) => {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:8000/directions", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
        console.log("Data saved successfully");
      } else if (xhr.readyState === 4) {
        console.error("Error saving data");
      }
    };
    xhr.send(JSON.stringify(response));
  };

  const drawRoute = (start, end, color) => {
    var departureTime = new Date();
    departureTime.setDate(departureTime.getDate() + 1);
    departureTime.setHours(3);
    departureTime.setMinutes(30);
    departureTime.setSeconds(0);
    departureTime.setMilliseconds(0);

    const request = {
      origin: start,
      destination: end,
      travelMode: 'DRIVING',
      drivingOptions: {
        departureTime: departureTime,
      },
    };

    directionsService.route(request, function (result, status) {
      if (status === 'OK') {
        const renderer = new google.maps.DirectionsRenderer({
          polylineOptions: {
            strokeColor: color,
            strokeWeight: 5,
            strokeOpacity: 0.7,
          },
          suppressMarkers: true,
        });
        renderer.setMap(map);
        console.log("result");
        console.log(result);
        renderer.setDirections(result);
        saveDirectionsToFile(result);
      } else {
        console.error('Could not display directions due to: ' + status);
      }
    });
  };

  const parseCSV = (data) => {
    const rows = data.split('\n').slice(1); // Remove header
    return rows.map(row => {
      const [stop_id, stop_name, stop_lat, stop_lon] = row.split(',');
      return { id: stop_id, name: stop_name, lat: parseFloat(stop_lat), lng: parseFloat(stop_lon) };
    });
  };

  const getRandomColor = () => {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  };

  return (
    <APIProvider apiKey={'YOUR_API_KEY'}>
      <div>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
        <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.10.0/font/bootstrap-icons.min.css" rel="stylesheet" />
        <div className="jumbotron text-center">
          <div className="container">
            <h1>Proiectarea Rețelelor de Transport Public</h1>
          </div>
        </div>
        <div className="container">
          <div className="mb-4 d-flex flex-row">
            <select className="form-select me-4" id="transport-station-select" aria-label="Select a station">
              <option selected disabled>Choose a station</option>
              <option value="1">Station 1</option>
              <option value="2">Station 2</option>
              <option value="3">Station 3</option>
              <option value="4">Station 4</option>
              <option value="5">Station 5</option>
            </select>
            <select className="form-select me-4" id="transport-station-select" aria-label="Select a station" defaultValue="1">
              <option disabled>Choose a station</option>
              <option value="1">Station 1</option>
              <option value="2">Station 2</option>
              <option value="3">Station 3</option>
              <option value="4">Station 4</option>
              <option value="5">Station 5</option>
            </select>
            <input type="text" className="form-control me-4" id="distance-input" placeholder="Introduceți distanța" />
            <input type="text" className="form-control" id="demand-input" placeholder="Introduceți cererea" />
          </div>
        </div>
        <div className="container-map">
          <Map center={position} zoom={12} onLoad={setMap}>
            {map && <Marker position={position} />}
          </Map>
        </div>
      </div>
    </APIProvider>
  );
}

export default HomePage;
