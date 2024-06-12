import { Map, Marker } from '@vis.gl/react-google-maps';
import { Directions } from '@vis.gl/react-google-maps';

async function initMap() {
  console.log("map");
  const position = { lat: 47.19052, lng: 27.55848 };
  // Folosește componente pentru a desena harta și a adăuga marcatorii
  return (
    <Map center={position} zoom={12}>
      <Marker position={position} />
    </Map>
  );
}

async function drawRoutesFromCSV() {
    const response = await fetch('../static/stops_data.csv');
    const data = await response.text();
    const stops = parseCSV(data);
  
    if (stops.length >= 2) {
      for (let i = 0; i < 10; i++) {
        const start = { lat: stops[i].lat, lng: stops[i].lng };
        const end = { lat: stops[i + 1].lat, lng: stops[i + 1].lng };
        // Desenează ruta folosind componenta Directions
        return <Directions from={start} to={end} />;
      }
    }
  }


  function saveDirectionsToFile(response) {
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
  }
  
  function drawRoute(start, end, color) {
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
        departureTime: departureTime
      }
    };
  
    directionsService.route(request, function(result, status) {
      if (status === 'OK') {
        const renderer = new google.maps.DirectionsRenderer({
          polylineOptions: {
            strokeColor: color,
            strokeWeight: 5,
            strokeOpacity: 0.7 // Ajustează opacitatea pentru a permite vizibilitatea
          },
          suppressMarkers: true
        });
        renderer.setMap(map);
        console.log("result")
        console.log(result)
        renderer.setDirections(result);
        saveDirectionsToFile(result);
      } else {
        console.error('Could not display directions due to: ' + status);
      }
    });
  }
  
  function parseCSV(data) {
    const rows = data.split('\n').slice(1); // Remove header
    return rows.map(row => {
      const [stop_id, stop_name, stop_lat, stop_lon] = row.split(',');
      return { id: stop_id, name: stop_name, lat: parseFloat(stop_lat), lng: parseFloat(stop_lon) };
    });
  }
  
  
  function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }

