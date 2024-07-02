import { CommonModule, NgFor, NgIf } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { io } from "socket.io-client";
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
  selector: 'app-edit-routes',
  standalone: true,
  imports: [NgIf, NgFor, CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './edit-routes.component.html',
  styleUrl: './edit-routes.component.css'
})

export class EditRoutesComponent {
  private map: any;
  private directionsService: any;
  private colorIndex: number = 0;
  public routes: Route[] = [];
  private stops: Stop[] = [];
  private directionsRenderers: any[] = []; 
  private markers: any[] = []; 
  private colors: string[] = [
    '#FF5733', '#33FF57', '#3357FF', '#F333FF', '#FF33A8', '#33FFF2', '#F2FF33', 
    '#FF8F33', '#8F33FF', '#33FF8F', '#FF3333', '#33FF33', '#3333FF', '#8F8F33', 
    '#FF5733', '#57FF33', '#5733FF', '#FF3357', '#33FF57', '#3357FF', '#F333FF', 
    '#FF33A8', '#33FFF2', '#F2FF33', '#FF8F33', '#8F33FF', '#33FF8F', '#FF3333', 
    '#33FF33', '#3333FF', '#8F8F33', '#FF5733', '#57FF33', '#5733FF', '#FF3357', 
    '#33FF57', '#3357FF', '#F333FF', '#FF33A8'
  ]; formDatele: FormGroup;
  formParametrii: FormGroup;
  private socket: any;
  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.socket = io('http://localhost:8000');
    this.formDatele = this.fb.group({
      stationSelect1: ['', Validators.required],
      stationSelect2: ['', Validators.required],
      distanceInput: ['', [Validators.required, Validators.pattern(/^\d+(\.\d{1,2})?$/)]],
      demandInput: ['', Validators.required]
    });

    this.formParametrii = this.fb.group({
      populationSizeInput: ['', [
        Validators.required,
        Validators.pattern(/^[1-9]\d*$/), 
        Validators.min(5)
      ]],
      tournamentSizeInput: ['', [Validators.required, Validators.min(2)]],
      crossoverProbabilityInput: ['', [Validators.required, Validators.min(0), Validators.max(1)]],
      deletionProbabilityInput: ['', [Validators.required, Validators.min(0), Validators.max(1)]],
      smallMutationProbabilityInput: ['', [Validators.required, Validators.min(0), Validators.max(1)]],
      numberOfGenerationsInput: ['', [Validators.required, Validators.min(1)]],
      eliteSizeInput: ['', [Validators.required, Validators.min(1)]]
    });
  }

  ngOnInit(): void {
    this.loadGoogleMapsScript().then(() => {
      this.initMap();
    });
    

    this.socket.on('algorithm_complete', (message: any) => {
      console.log('Genetic algorithm finished:', message);
      this.routes = message.routes;
      this.fetchStops();
    });
  }

  loadGoogleMapsScript(): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyAL9n-iu4Ata_D057iAE-Fo2sly5rhuZiA&libraries=places`;
      script.onload = () => resolve();
      script.onerror = (error: any) => reject(error);
      document.body.appendChild(script);
    });
  }

  initMap(): void {
    const position = { lat: 47.19052, lng: 27.55848 };
    this.map = new google.maps.Map(document.getElementById("map"), {
      zoom: 12,
      center: position,
    });
  }

  submitDateleForm(): void {
    if (this.formDatele.valid) {
      console.log('Formular Datele din Iași submit:', this.formDatele.value);
    }
  }

  submitParametriiForm(): void {
  if (this.formParametrii.valid) {
    console.log('Formular Parametrii Algoritmului submit:', this.formParametrii.value);
    const algorithmParams = {
      populationSize: this.formParametrii.value.populationSizeInput,
      tournamentSize: this.formParametrii.value.tournamentSizeInput,
      crossoverProbability: this.formParametrii.value.crossoverProbabilityInput,
      deletionProbability: this.formParametrii.value.deletionProbabilityInput,
      smallMutationProbability: this.formParametrii.value.smallMutationProbabilityInput,
      numberOfGenerations: this.formParametrii.value.numberOfGenerationsInput,
      eliteSize: this.formParametrii.value.eliteSizeInput
    };

    const xhr = new XMLHttpRequest();
    const url = "http://localhost:8000/api/run-algorithm";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    // Adăugarea token-ului JWT în header-ul cererii
    const token = localStorage.getItem('token');
    if (token) {
      xhr.setRequestHeader("Authorization", "Bearer " + token);
    } else {
      console.error("JWT token not found!");
      return;
    }

    xhr.onreadystatechange = () => {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
          console.log("Response:", xhr.responseText);
        } else {
          console.error("Error starting algorithm:", xhr.status);
        }
      }
    };
    xhr.send(JSON.stringify(algorithmParams));
  }
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

getRandomColor() {
  console.log("getColor");
  const color = this.colors[this.colorIndex];
  this.colorIndex = (this.colorIndex + 1) % this.colors.length;
  return color;
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