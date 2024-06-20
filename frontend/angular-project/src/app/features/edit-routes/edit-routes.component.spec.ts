import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditRoutesComponent } from './edit-routes.component';

describe('EditRoutesComponent', () => {
  let component: EditRoutesComponent;
  let fixture: ComponentFixture<EditRoutesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditRoutesComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(EditRoutesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
