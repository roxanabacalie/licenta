import { Component, OnInit } from '@angular/core';
import { CommonModule, NgFor, NgIf } from '@angular/common'; 
declare var google: any;

type Stop = {
  stop_id: string;
  stop_lat: number;
  stop_lon: number;
  stop_name: string;
};

type Route = {
  id: string;
  stops: string[];
};

@Component({
  selector: 'app-homepage',
  standalone: true,
  templateUrl: './homepage.component.html',
  styleUrls: ['./homepage.component.css'],
  imports: [NgFor, NgIf]
})

export class HomepageComponent implements OnInit {
  
  private map: any;
  private directionsService: any;
  private colorIndex: number = 0;
  public routes: Route[] = [];
  private stops: Stop[] = [];
  private directionsRenderer: any; 
  private directionsRenderers: any[] = []; 
  private markers: any[] = []; 
  

  private colors: string[] = [
    '#FF5733', '#33FF57', '#3357FF', '#F333FF', '#FF33A8', '#33FFF2', '#F2FF33', 
    '#FF8F33', '#8F33FF', '#33FF8F', '#FF3333', '#33FF33', '#3333FF', '#8F8F33', 
    '#FF5733', '#57FF33', '#5733FF', '#FF3357', '#33FF57', '#3357FF', '#F333FF', 
    '#FF33A8', '#33FFF2', '#F2FF33', '#FF8F33', '#8F33FF', '#33FF8F', '#FF3333', 
    '#33FF33', '#3333FF', '#8F8F33', '#FF5733', '#57FF33', '#5733FF', '#FF3357', 
    '#33FF57', '#3357FF', '#F333FF', '#FF33A8'
  ];
  constructor() { }
  
  ngOnInit(): void {
    this.loadGoogleMapsScript().then(() => {
      this.initMap();
    });
    this.fetchRoutes();
    this.fetchStops();
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
    this.directionsRenderer = new google.maps.DirectionsRenderer({ map: this.map }); 

  }


  async getStopsAndDraw() {
    try {
      const response = await fetch('http://localhost:8000/api/stops');
      if (response.ok) {
        const stops = await response.json(); 
        this.drawStops(stops); 
      } else {
        console.error('Error fetching stops:', response.status);
      }
    } catch (error) {
      console.error('Error fetching stops:', error);
    }
  }

  drawStops(stops: any[]) {
    stops.forEach(stop => {
      const position = { lat: parseFloat(stop.stop_lat), lng: parseFloat(stop.stop_lon) };
      const marker = new google.maps.Marker({
        position: position,
        map: this.map,
        title: stop.stop_name
      });
      
      this.markers.push(marker);
    
      const contentString = `
        <div>
          <h3>${stop.stop_name}</h3>
          <p>Coordonate: ${position.lat.toFixed(6)}, ${position.lng.toFixed(6)}</p>
        </div>
      `;
  

      const infowindow = new google.maps.InfoWindow({
        content: contentString
      });
  
      marker.addListener('click', () => {
        infowindow.close();
        infowindow.open(this.map, marker);
      });
    });
  }
  
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
    console.log("getColor");
    const color = this.colors[this.colorIndex];
    this.colorIndex = (this.colorIndex + 1) % this.colors.length;
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
    this.directionsRenderers.push(renderer);
  }


  async getRouteDataAndDraw(startId: string, stopId: string, color: string) {
    console.log("getRouteDataAndDraw");
    try {
      const response = await fetch(`http://localhost:8000/api/directions?start_id=${startId}&stop_id=${stopId}`);
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
      const response = await fetch('http://localhost:8000/api/directions');
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

  async fetchRoutes() {
    const routesResponse = await fetch('http://localhost:8000/api/routes');
    if (!routesResponse.ok) {
      throw new Error('Network response was not ok.');
    }
    const routes = await routesResponse.json();
    this.routes = routes;
    console.log('Routes:', this.routes);
  } 


  async fetchStops() {
    const stopsResponse = await fetch('http://localhost:8000/api/stops');
    if (!stopsResponse.ok) {
      throw new Error('Network response was not ok.');
    }
    const stops = await stopsResponse.json();
    this.stops = stops;
    console.log('Stops:', this.stops);
  } 

  getStopName(stopId: string): string {
    const stop = this.stops.find(s => s.stop_id === (parseInt(stopId, 10) + 1).toString());
    return stop ? stop.stop_name : 'Unknown';
  }

  clearPreviousRenderers() {
    this.directionsRenderers.forEach(renderer => renderer.setMap(null));
    this.directionsRenderers = [];
  }

  clearPreviousMarkers() {
    this.markers.forEach(marker => marker.setMap(null));
    this.markers = [];
  }
  
  async displayRoute(routeId: string): Promise<void> {
    this.clearPreviousRenderers(); 
    this.clearPreviousMarkers();
   
    console.log("Displaying route with ID:", routeId);
    const route = this.routes.find(r => r.id === routeId);
    if (!route) {
      console.error('Route not found:', routeId);
      return;
    }
    const color = this.getRandomColor();
    for (let i = 0; i < route.stops.length - 1; i++) {
      const startId = String(Number(route.stops[i]) + 1); 
      const stopId = String(Number(route.stops[i + 1]) + 1); 
      
      await this.getRouteDataAndDraw(startId, stopId, color);
    }
    const routeStops: Stop[] = [];
    for (let i = 0; i < route.stops.length; i++) {
      const stopId = route.stops[i];
      const stop = this.stops.find(s => s.stop_id === String(stopId+1));
      if (stop) {
        routeStops.push(stop);
      } else {
        console.warn('Stop not found for stop_id:', stopId);
      }
  }
  this.drawStops(routeStops);
  
}
}
