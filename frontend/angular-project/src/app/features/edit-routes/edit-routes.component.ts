import { CommonModule, NgFor, NgIf } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { AbstractControl, FormsModule, ReactiveFormsModule, ValidationErrors, ValidatorFn } from '@angular/forms';
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
  currentGeneration = 0;
  totalGenerations = 100;
  private colorIndex: number = 0;
  public notificationMessage: string = '';
  public showNotification: boolean = false;
  public notificationType: 'success' | 'error' = 'success'; 

  public algorithmNotificationMessage: string = '';
  public showAlgorithmNotification: boolean = false;
  public algorithmNotificationType: 'success' | 'error' = 'success';

  public routes: Route[] = [];
  public stops: Stop[] = [];
  public files: { id: number, filename: string }[] = [];
  public selectedFile: number | null = null;
  private directionsRenderers: any[] = []; 
  private markers: any[] = []; 
  public isAlgorithmRunning = false;
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
      stationSelect1: [null, Validators.required],
      stationSelect2: [null, Validators.required],
      distanceInput: ['', [Validators.required, this.distanceValidator()]],
      demandInput: ['', [Validators.required, Validators.pattern(/^-?\d+$/), Validators.min(0)]]
    });
    
    this.formParametrii = this.fb.group({
      populationSizeInput: ['', [
        Validators.required,
        Validators.pattern(/^[1-9]\d*$/), 
        Validators.min(5)
      ]],
      tournamentSizeInput: ['', [
        Validators.required,
        Validators.pattern(/^[1-9]\d*$/), 
        Validators.min(2)
      ]],
      crossoverProbabilityInput: ['', [Validators.required, Validators.min(0), Validators.max(1), this.realNumberValidator()]],
      deletionProbabilityInput: ['', [Validators.required, Validators.min(0), Validators.max(1), this.realNumberValidator()]],
      smallMutationProbabilityInput: ['', [Validators.required, Validators.min(0), Validators.max(1), this.realNumberValidator()]],
      numberOfGenerationsInput: ['', [
        Validators.required,
        Validators.pattern(/^[1-9]\d*$/), 
        Validators.min(1)
      ]],
      eliteSizeInput: ['', [
        Validators.required,
        Validators.pattern(/^[1-9]\d*$/), 
        Validators.min(1)
      ]]
    });
  }

  ngOnInit(): void {
    this.loadGoogleMapsScript().then(() => {
      this.fetchStops();
      this.initMap();
      this.checkAlgorithmStatus();
      this.fetchFiles();
    });
    

    this.socket.on('algorithm_complete', (message: any) => {
      console.log('Genetic algorithm finished:', message);
      this.routes = message.routes;
      this.isAlgorithmRunning = false;
      this.showAlgorithmNotificationMessage('Rularea algoritmului s-a terminat cu succes.', 'success');
    });
    
    this.formDatele.get('stationSelect1')?.valueChanges.subscribe(() => this.updateDisplayTravelInfo());
    this.formDatele.get('stationSelect2')?.valueChanges.subscribe(() => this.updateDisplayTravelInfo());
  }

  distanceValidator() {
    return (control: AbstractControl) => {
      const value = control.value;
      if (value === 'infinit' || /^[0-9]+$/.test(value)) {
        return null; 
      } else {
        return { invalidDistance: true }; 
      }
    };
  }

  realNumberValidator(): ValidatorFn {
    console.log("Validare");
    return (control: AbstractControl): { [key: string]: any } | null => {
      const value = control.value;
      const isValid = !isNaN(value) && parseFloat(value) === +value;
      return isValid ? null : { 'notRealNumber': { value: control.value } };
    };
  }
  

  checkAlgorithmStatus(): void {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://localhost:8000/api/is-algorithm-running');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

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
          const response = JSON.parse(xhr.responseText);
          this.isAlgorithmRunning = response.running;
        } else {
          console.error('Error checking algorithm status:', xhr.status);
        }
      }
    };
    xhr.send();
  }
  
  showAlgorithmNotificationMessage(message: string, type: 'success' | 'error'): void {
    this.algorithmNotificationMessage = message;
    this.algorithmNotificationType = type;
    this.showAlgorithmNotification = true;
    setTimeout(() => {
      this.showAlgorithmNotification = false;
    }, 5000);
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

  updateDisplayTravelInfo(): void {
    const fromStation = this.formDatele.get('stationSelect1')?.value;
    const toStation = this.formDatele.get('stationSelect2')?.value;
  
    if (fromStation && toStation) {
      const url = `http://localhost:8000/api/travel-info?from=${fromStation}&to=${toStation}`;
  
      const xhr = new XMLHttpRequest();
      xhr.open('GET', url, true);
      xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
      xhr.onload = () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          if (response.travel_time !== undefined && response.demand !== undefined) {
            this.formDatele.patchValue({
              distanceInput: response.travel_time,
              demandInput: response.demand
            });
            this.formDatele.get('distanceInput')?.enable();
            this.formDatele.get('demandInput')?.enable();
          } else {
            console.error('Data not found for the selected stations.');
          }
        } else {
          console.error('Error fetching travel info:', xhr.statusText);
        }
      };
      xhr.onerror = () => console.error('Network error.');
      xhr.send();
    }
  }
  
  submitDateleForm(): void {
    if (this.formDatele.valid) {
      console.log('Formular Datele din Iași submit:', this.formDatele.value);
      const { stationSelect1, stationSelect2, distanceInput, demandInput } = this.formDatele.value;

      const fromStation = stationSelect1;
      const toStation = stationSelect2;
      const travelTime = distanceInput;
      const demand = demandInput;

      this.updateTravelInfo(fromStation, toStation, travelTime, demand);
    }
  }

  showNotificationMessage(message: string, type: 'success' | 'error'): void {
    this.notificationMessage = message;
    this.notificationType = type;
    this.showNotification = true;
    setTimeout(() => {
      this.showNotification = false;
    }, 5000);
  }

  updateTravelInfo(fromStation: string, toStation: string, travelTime: number, demand: number) {
    const url = 'http://localhost:8000/api/travel-info'; 

    const xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onreadystatechange = () => {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
          console.log('Update successful', xhr.responseText);
          this.showNotificationMessage('Modificarea s-a făcut cu succes.', 'success');
        } else {
          console.error('Update failed', xhr.status);
          this.showNotificationMessage('A apărut o eroare în modificarea dorită. Vă rugăm să încercați din nou.', 'error');
        }
      }
    };

    const body = JSON.stringify({
      from: fromStation,
      to: toStation,
      travelTime: travelTime,
      demand: demand
    });
    console.log(body);
    xhr.send(body);
  }


  submitParametriiForm(): void {
    if (this.isAlgorithmRunning) {
      this.showAlgorithmNotificationMessage('Algoritmul deja rulează.', 'error');
    } else if (this.formParametrii.valid) {
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
            this.showAlgorithmNotificationMessage('Algoritmul a început să ruleze.', 'success');
          } else {
            console.error("Error starting algorithm:", xhr.status);
            this.showAlgorithmNotificationMessage('Eroare în pornirea rulării algoritmului.', 'error');
          }
        }
      };
      xhr.send(JSON.stringify(algorithmParams));
  }
  this.isAlgorithmRunning = true;
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

async fetchRoutesByFilename(filename: string) {
  console.log(`http://localhost:8000/api/routes?filename=${filename}`);
  const routesResponse = await fetch(`http://localhost:8000/api/routes?filename=${filename}`);
  
  if (!routesResponse.ok) {
    throw new Error('Network response was not ok.');
  }
  const routes = await routesResponse.json();
  this.routes = routes;
  console.log('Routes:', this.routes);
} 

setDefaultFile(): void {
  if (this.selectedFile !== null) {
    const filename = this.files.find(file => file.id === this.selectedFile)?.filename;
    if (filename) {
      const xhr = new XMLHttpRequest();
      const url = 'http://localhost:8000/api/set_default_file';
      xhr.open('POST', url, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.onreadystatechange = () => {
        if (xhr.readyState === XMLHttpRequest.DONE) {
          if (xhr.status === 200) {
            console.log('Default file set successfully:', xhr.responseText);
          } else {
            console.error('Error setting default file:', xhr.status);
          }
        }
      };
      xhr.send(JSON.stringify({ filename }));
    } else {
      console.error('Selected file not found.');
    }
  } else {
    console.error('No file selected.');
  }
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

getStopId(stopName: string): string {
  console.log("Searching for stopName:", stopName);
  const stop = this.stops.find(s => s.stop_name === stopName);
  console.log("Found stop by stopName:", stop);
  return stop ? stop.stop_id : 'Unknown';
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

fetchFiles(): void {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', 'http://localhost:8000/api/files');
  xhr.setRequestHeader('Content-Type', 'application/json');

  xhr.onreadystatechange = () => {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        console.log(response);
        response.forEach((file: { id: string | number; name: string }) => {
          file.id = +file.id; 
        });
        this.files = response;
        console.log('Files:', this.files); 
      } else {
        console.error('Error fetching files:', xhr.status);
      }
    }
  };

  xhr.send();
}

onFileSelect(event: Event) {
  const selectElement = event.target as HTMLSelectElement;
  const selectedIndex = selectElement.selectedIndex;

  if (selectedIndex !== -1) {
    const selectedOption = selectElement.options[selectedIndex];
    const filename = selectedOption.text;
    this.selectedFile = +selectedOption.value;

    console.log('Selected file:', this.selectedFile);
    this.fetchRoutesByFilename(filename);
  } else {
    console.log('Nu a fost selectat niciun fișier.');
  }
}

}