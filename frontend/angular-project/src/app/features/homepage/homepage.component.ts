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
    this.getRouteDataAndDraw();

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


  saveRoute(start: any, end: any, color: string) {
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
        this.saveDirectionsToFile(result);
      } else {
        console.error('Could not display directions due to: ' + status);
      }
    });
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


  async getRouteDataAndDraw() {
    console.log("getRouteDataAndDraw");
    const routeId = "6660a679c1653b524b6e73cb";
    try {
        console.log('Salut');
        const xhr = new XMLHttpRequest();
        xhr.open("GET", 'http://localhost:8000/api/routes/' + routeId, true);
        xhr.onreadystatechange = () => { 
            if (xhr.readyState === XMLHttpRequest.DONE) {
                console.log("xhr.readyState:", xhr.readyState);
                console.log("xhr.status:", xhr.status);
                if (xhr.status === 200) {
                    const routeData = JSON.parse(xhr.responseText);
                    delete routeData._id;
                    console.log('Ruta găsită:', routeData);
                    const color = this.getRandomColor(); 
                    this.drawRoute(routeData, color); 
                } else {
                    console.error('Eroare la obținerea datelor rutei:', xhr.status);
                }
            }
        };

        console.log("here");
        xhr.send();
       
    } catch (error) {
        console.error('Eroare:', error);
    }
  }


  
}
