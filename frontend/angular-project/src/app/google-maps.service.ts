import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class GoogleMapsService {
  private apiLoaded = false;

  loadApi(): Promise<void> {
    if (this.apiLoaded) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://maps.googleapis.com/maps/api/js?key=AIzaSyAL9n-iu4Ata_D057iAE-Fo2sly5rhuZiA&callback=initMap&v=weekly&libraries=marker';
      script.async = true;
      script.defer = true;
      script.onload = () => {
        this.apiLoaded = true;
        resolve();
      };
      script.onerror = (error: any) => reject(error);
      document.head.appendChild(script);
    });
  }
}
