import { CommonModule, NgFor, NgIf } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
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
  
  // Predefined list of 40 distinct colors
  private colors: string[] = [
    '#FF5733', '#33FF57', '#3357FF', '#F333FF', '#FF33A8', '#33FFF2', '#F2FF33', 
    '#FF8F33', '#8F33FF', '#33FF8F', '#FF3333', '#33FF33', '#3333FF', '#8F8F33', 
    '#FF5733', '#57FF33', '#5733FF', '#FF3357', '#33FF57', '#3357FF', '#F333FF', 
    '#FF33A8', '#33FFF2', '#F2FF33', '#FF8F33', '#8F33FF', '#33FF8F', '#FF3333', 
    '#33FF33', '#3333FF', '#8F8F33', '#FF5733', '#57FF33', '#5733FF', '#FF3357', 
    '#33FF57', '#3357FF', '#F333FF', '#FF33A8'
  ]; formDatele: FormGroup;
  formParametrii: FormGroup;

  constructor(private fb: FormBuilder) {
    this.formDatele = this.fb.group({
      stationSelect1: ['', Validators.required],
      stationSelect2: ['', Validators.required],
      distanceInput: ['', [Validators.required, Validators.pattern(/^\d+(\.\d{1,2})?$/)]],
      demandInput: ['', Validators.required]
    });

    this.formParametrii = this.fb.group({
      populationSizeInput: ['', [
        Validators.required,
        Validators.pattern(/^[1-9]\d*$/), // Verificare pentru număr întreg pozitiv
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
      // Aici poți adăuga logica pentru procesarea formularului
    }
  }

  submitParametriiForm(): void {
    if (this.formParametrii.valid) {
      console.log('Formular Parametrii Algoritmului submit:', this.formParametrii.value);
      // Aici poți adăuga logica pentru procesarea formularului
    }
  }
}