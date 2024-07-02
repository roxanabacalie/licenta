import { CommonModule, NgFor, NgIf } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { io } from "socket.io-client";
declare var google: any;


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
}