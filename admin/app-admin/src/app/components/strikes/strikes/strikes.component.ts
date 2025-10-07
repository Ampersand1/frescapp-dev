import { Component, OnInit  } from '@angular/core';
import {  StrikesService, Strike } from '../../../services/strikes.service';
import { Router } from '@angular/router';
@Component({
  selector: 'app-strikes',

  templateUrl: './strikes.component.html',
  styleUrl: './strikes.component.css'
})

export class StrikesComponent implements OnInit{
  allStrikes: Strike[] = [];
  filteredStrikes: Strike[] = [];
  today = new Date();
  searchTerm: string = '';
  typeLabels: Record<string,string> = {
    quality:            'Calidad',
    partial_missing:    'Faltante parcial',
    total_missing:      'Faltante total',
    late_arrival:       'Llegada tarde',
    cancel_order:       'Cancelación'
  };
  constructor(
    private strikeService: StrikesService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadStrikes();
  }

  loadStrikes(): void {
    this.strikeService.getAll().subscribe(data => {
      this.allStrikes = data;
      this.applyFilter();
    });
  }

  applyFilter(): void {
    const term = this.searchTerm.trim().toLowerCase();
    if (!term) {
      this.filteredStrikes = [...this.allStrikes];
    } else {
      this.filteredStrikes = this.allStrikes.filter(s =>
        Object.values(s).some(val =>
          val != null &&
          val.toString().toLowerCase().includes(term)
        )
      );
    }
  }

  onSearchChange(): void {
    this.applyFilter();
  }

  delete(id: string): void {
    if (!confirm('¿Eliminar este strike?')) return;
    this.strikeService.delete(id).subscribe(() => this.loadStrikes());
  }

  goToCreate(): void {
    this.router.navigate(['/strike', 'new']);
  }

  goToEdit(id: string): void {
    this.router.navigate(['/strike', id]);
  }
}
