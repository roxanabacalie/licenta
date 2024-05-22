let map;
let directionsService;

async function initMap() {
  console.log("map");

  // Poziția inițială
  const position = { lat: 47.19052, lng: 27.55848 };

  // Request needed libraries.
  //@ts-ignore
  const { Map } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

  // The map, centered at the initial position
  map = new Map(document.getElementById("map"), {
    zoom: 12,
    center: position,
  });

  directionsService = new google.maps.DirectionsService();
  drawRoutesFromCSV();
}

async function drawRoutesFromCSV() {
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
}

function drawRoute(start, end, color) {
  const request = {
    origin: start,
    destination: end,
    travelMode: 'DRIVING'
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
      renderer.setDirections(result);
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

// Ensure initMap is defined in the global scope
window.initMap = initMap;
