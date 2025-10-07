import { Component } from '@angular/core';
import { CierresService } from '../../../services/cierres.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-cierres',
  templateUrl: './cierres.component.html',
  styleUrl: './cierres.component.css'
})
export class CierresComponent {
  newDate: string = '';
  minDate: string = ''
  cierres: any[] = [];
validando: boolean = false;
validacion: any = null;
validacionExitosa: boolean = false;
  constructor(
    private cierresService: CierresService,
        private router: Router,

  ) {}
  ngOnInit() {
    const today = new Date();
    // formatear YYYY-MM-DD
    const yyyy = today.getFullYear()-1;
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    this.minDate = `${yyyy}-${mm}-${dd}`;
    this.getCierres();
  }
validarFecha() {
  if (!this.newDate) return;

  this.validando = true;
  this.validacion = null;
  this.validacionExitosa = false;

  this.cierresService.validateCierre(this.newDate).subscribe({
    next: (res: any) => {
      this.validacion = res;

      // Bloquea solo si hay errores graves
      const tieneErroresGraves = res.errores?.some((e: { tipo: string; }) => e.tipo === 'grave');
      this.validacionExitosa = !tieneErroresGraves;
    },
    error: (err) => {
      this.validacion = {
        errores: [{ tipo: 'grave', mensaje: "Error en la validación" }]
      };
      this.validacionExitosa = false;
    },
    complete: () => this.validando = false
  });
}

  createCierre() {
    if (!this.newDate) return;
    this.cierresService.createCierre(this.newDate).subscribe(response => {
      const modalEl = document.getElementById('newCierre');
      if (modalEl) {
        // oculta el modal
        // @ts-ignore
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal?.hide();

        // quita la clase que bloquea el body
        document.body.classList.remove('modal-open');

        // elimina cualquier backdrop residual
        const backdrops = document.getElementsByClassName('modal-backdrop');
        while (backdrops.length > 0) {
          backdrops[0].parentNode?.removeChild(backdrops[0]);
        }
      }

      this.newDate = '';
      this.getCierres();
    });
  }
  getCierres() {
    this.cierresService.getCierres().subscribe(
      (data) => {
        this.cierres = data;
      },
      (error) => {
        console.error('Error al obtener cierres:', error);
        // Manejo de errores
      }
    );
  }
  toCierre(cierre:any) {
    this.router.navigate(['/cierre', cierre.close_date]);
  }
  getErroresAgrupados() {
  const agrupados: { [key: string]: any[] } = {};
  if (!this.validacion?.errores) return agrupados;

  for (const error of this.validacion.errores) {
    const clasificacion = error.clasificacion || 'general';
    if (!agrupados[clasificacion]) agrupados[clasificacion] = [];
    agrupados[clasificacion].push(error);
  }

  return agrupados;
}
}
