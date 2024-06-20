import { Component, OnInit } from '@angular/core';

declare var google: any;

@Component({
  selector: 'app-homepage',
  standalone: true,
  templateUrl: './homepage.component.html',
  styleUrls: ['./homepage.component.css']
})

export class HomepageComponent implements OnInit {
  
  private map: any;
  private directionsService: any;

  constructor() { }

  ngOnInit(): void {
    // load Google Maps API, initialize the map
    this.loadGoogleMapsScript().then(() => {
      this.initMap();
    });
  }
  
  
  loadGoogleMapsScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyAL9n-iu4Ata_D057iAE-Fo2sly5rhuZiA&libraries=places`;
      script.onload = (event: Event) => resolve();
      script.onerror = reject;
      document.body.appendChild(script);
    });
  }
  
 
  initMap() {
    console.log("initMap");
    const position = { lat: 47.19052, lng: 27.55848 };
    this.map = new google.maps.Map(document.getElementById("map"), {
      zoom: 12,
      center: position,
    });

    this.directionsService = new google.maps.DirectionsService();
    this.getLocalRoutesAndDraw();
    //this.getDirectionsFromCSV();
    //this.getRouteDataAndDraw();

  }

  // methods for saving the directions from Google API
  
  saveDirectionsToFile(response: any) {
    console.log("saveDirectionsToFile");
    const xhr = new XMLHttpRequest();
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

 
  saveRoute(start: any, end: any, startId: string, stopId: string) {
    const departureTime = new Date();
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

    this.directionsService.route(request, (result: any, status: string) => {
      if (status === 'OK') {
        const response = {
          ...result,
          start_id: startId,
          stop_id: stopId
        }
        this.saveDirectionsToFile(response);
      } else {
        console.error('Could not display directions due to: ' + status);
      }
    });
  }
  
  parseCSV(data: string) {
    const rows = data.split('\n').slice(1);
    return rows.map(row => {
      const [stop_id, stop_name, stop_lat, stop_lon] = row.split(',');
      return { id: stop_id, name: stop_name, lat: parseFloat(stop_lat), lng: parseFloat(stop_lon) };
    });
  }

  async getDirectionsFromCSV() {
    const response = await fetch('../assets/iasi_filtered_stops_data.csv');
    const data = await response.text();
    const stops = this.parseCSV(data);
    if (stops.length >= 2) {
      for (let i = 186; i <=191; i++) {
        for(let j=1; j<=191; j++) {
          if(i!=j) {
            const start = new google.maps.LatLng(stops[i-1].lat, stops[i-1].lng);
            const end = new google.maps.LatLng(stops[j-1].lat, stops[j-1].lng);
            this.saveRoute(start, end, stops[i-1].id, stops[j-1].id);
          }
        }
      }
    }
  }


  getRandomColor() {
    console.log("getRandomColor")
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }


  drawRoute(routeData: any, color: string) {
    console.log("drawRoute", routeData)
    const renderer = new google.maps.DirectionsRenderer({
      polylineOptions: {
        strokeColor: color,
        strokeWeight: 5,
        strokeOpacity: 0.7
      },
      suppressMarkers: true
    });
    renderer.setMap(this.map);
    renderer.setDirections(routeData);
  }


  async getRouteDataAndDraw(startId: string, stopId: string, color: string) {
    console.log("getRouteDataAndDraw");
    try {
      const response = await fetch(`http://localhost:8000/api/routes?start_id=${startId}&stop_id=${stopId}`);
      if (response.ok) {
        const routeData = await response.json();
        if (routeData) {
          delete routeData.start_id;
          delete routeData.stop_id;
          console.log('Ruta găsită:', routeData);
          this.drawRoute(routeData, color);
        } else {
          console.error('Empty route data received');
        }
      } else {
        console.error('Eroare la obținerea datelor rutei:', response.status);
      }
    } catch (error) {
      console.error('Eroare:', error);
    }
  }
  
  

  async getLocalRoutesAndDraw() {
    console.log("getLocalRoutesAndDraw");
    try {
      const response = await fetch('http://localhost:8000/api/routes');
      if (response.ok) {
        const routes = await response.json();
        routes.forEach((route: number[]) => {
          const color = this.getRandomColor();
          for (let i = 0; i < route.length - 1; i++) {
            const startId = route[i];
            const stopId = route[i + 1];
            this.getRouteDataAndDraw(startId.toString(), stopId.toString(), color);
          }
        });
      } else {
        console.error('Error fetching routes:', response.status);
      }
    } catch (error) {
      console.error('Error fetching routes:', error);
    }
  }
  
  
  
}
