import { Component, OnInit } from '@angular/core';
import { GoogleMapsService } from '../../google-maps.service';

declare var google: any;

@Component({
  selector: 'app-homepage',
  standalone: true,
  templateUrl: './homepage.component.html',
  styleUrls: ['./homepage.component.css'],
  providers: [GoogleMapsService] // Provide the service here as well if needed
})

export class HomepageComponent implements OnInit {
  
  private map: any;
  private directionsService: any;

  constructor(private googleMapsService: GoogleMapsService) { }

  ngOnInit(): void {
    /*
    this.googleMapsService.loadApi().then(() => {
      this.initMap();
    });*/
  }
/*
  async initMap() {
    console.log("map");
    const position = { lat: 47.19052, lng: 27.55848 };
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    this.map = new Map(document.getElementById("map"), {
      zoom: 12,
      center: position,
    });

    this.directionsService = new google.maps.DirectionsService();
    this.drawRoutesFromCSV();
  }

  async drawRoutesFromCSV() {
    const response = await fetch('../assets/stops_data.csv');
    const data = await response.text();
    const stops = this.parseCSV(data);

    if (stops.length >= 2) {
      for (let i = 0; i < 10; i++) {
        const start = new google.maps.LatLng(stops[i].lat, stops[i].lng);
        const end = new google.maps.LatLng(stops[i + 1].lat, stops[i + 1].lng);
        this.drawRoute(start, end, this.getRandomColor());
      }
    }
  }

  saveDirectionsToFile(response: any) {
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

  drawRoute(start: any, end: any, color: string) {
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
        const renderer = new google.maps.DirectionsRenderer({
          polylineOptions: {
            strokeColor: color,
            strokeWeight: 5,
            strokeOpacity: 0.7
          },
          suppressMarkers: true
        });
        renderer.setMap(this.map);
        renderer.setDirections(result);
        this.saveDirectionsToFile(result);
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

  getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }*/
}
