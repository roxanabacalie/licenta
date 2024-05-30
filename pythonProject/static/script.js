let map;
let directionsService;

async function initMap() {
  console.log("map");
  const position = { lat: 47.19052, lng: 27.55848 };
  const { Map } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
  map = new Map(document.getElementById("map"), {
    zoom: 12,
    center: position,
  });

  directionsService = new google.maps.DirectionsService();
  drawRoutesFromCSV();
  //drawRoutesFromJSON();
}
/*
async function drawRoutesFromJSON() {
  try {
    const response = await fetch('../static/directions_data_list.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    data.forEach(routeData => {
      console.log(routeData)
      if (routeData.status === 'OK' && routeData.routes.length > 0) {
        const route = routeData.routes[0]; // Select the first route (if it exists)
        console.log(routeData.routes[0])
        const renderer = new google.maps.DirectionsRenderer({
          polylineOptions: {
            strokeColor: getRandomColor(),
            strokeWeight: 5,
            strokeOpacity: 0.7
          },
          suppressMarkers: true
        });
        renderer.setMap(map);

        const directions = {
          routes: [{
            bounds: route.bounds,
            legs: route.legs,
            overview_polyline: route.overview_polyline
          }],
          status: 'OK',
          request: route.request
        };

        renderer.setDirections(directions);
      } else {
        console.error('Could not load directions data: ', routeData.status);
      }
    });
  } catch (error) {
    console.error('Error fetching directions data: ', error);
  }
}

*/
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

function saveDirectionsToFile(response) {
  var jsonData = JSON.stringify(response);
  var blob = new Blob([jsonData], { type: 'application/json' });
  var filename = 'directions.json';
  if (window.navigator.msSaveOrOpenBlob) {
    window.navigator.msSaveBlob(blob, filename);
  } else {
    var elem = window.document.createElement('a');
    elem.href = window.URL.createObjectURL(blob);
    elem.download = filename;
    document.body.appendChild(elem);
    elem.click();
    document.body.removeChild(elem);
  }
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

// Ensure initMap is defined in the global scope
window.initMap = initMap;