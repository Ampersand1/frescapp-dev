import { Component, OnInit } from '@angular/core';
import { UnitEconomicsService } from '../../services/unit-economics.service';

interface UnitEconomicEntry {
  detalle: string;
  fecha: string;
  valor: number;
  variable: string;
}

interface IndicadorValor {
  label: string;
  valores: { periodo: string; valor: string | number }[];
}

@Component({
  selector: 'app-ue',
  templateUrl: './ue.component.html',
  styleUrls: ['./ue.component.css']
})
export class UeComponent implements OnInit {
  groupedData: { [fecha: string]: UnitEconomicEntry[] } = {};
  loading = true;
  fechaInicio: string = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  fechaFin: string = new Date().toISOString().split('T')[0];

  indicadores: IndicadorValor[] = [];
  indicadoresMensuales: IndicadorValor[] = [];
  indicadoresSemanales: IndicadorValor[] = [];
  indicadoresDiarios: IndicadorValor[] = [];
  a: ((a: IndicadorValor, b: IndicadorValor) => number) | undefined;

  constructor(private unitEconomicsService: UnitEconomicsService) { }

  ngOnInit(): void {
    this.unitEconomicsService.getUnitEconomics().subscribe(data => {
      this.groupedData = this.groupByDate(data);
      this.generarIndicadores();
      this.loading = false;
    }, error => {
      console.error('Error fetching unit economics data:', error);
      this.loading = false;
    });
  }

  groupByDate(data: UnitEconomicEntry[]): { [fecha: string]: UnitEconomicEntry[] } {
    return data.reduce((acc: { [fecha: string]: UnitEconomicEntry[] }, item) => {
      const fecha = item.fecha;
      if (!acc[fecha]) acc[fecha] = [];
      acc[fecha].push(item);
      return acc;
    }, {});
  }

  getFechas(): string[] {
    return Object.keys(this.groupedData).sort();
  }

  getFechasFiltradas(): string[] {
    const start = new Date(this.fechaInicio);
    const end = new Date(this.fechaFin);
    return this.getFechas().filter(f => {
      const d = new Date(f);
      return (!this.fechaInicio || d >= start) && (!this.fechaFin || d <= end);
    });
  }

  getMeses(): string[] {
    const meses = new Set<string>();
    this.getFechas().forEach(f => meses.add(f.slice(0, 7)));
    return Array.from(meses).sort();
  }

  getSemanas(): string[] {
    const semanas = new Set<string>();
    this.getFechas().forEach(f => {
      const d = new Date(f);
      const y = d.getFullYear();
      const week = this.getISOWeek(d);
      semanas.add(`${y}-W${week.toString().padStart(2, '0')}`);
    });
    return Array.from(semanas).sort();
  }

  getISOWeek(d: Date): number {
    const date = new Date(d.getTime());
    date.setUTCDate(date.getUTCDate() + 4 - (date.getUTCDay() || 7));
    const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
    const weekNo = Math.ceil((((date.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
    return weekNo;
  }

  getSemanaISO(fecha: string): string {
    const d = new Date(fecha);
    const y = d.getFullYear();
    const w = this.getISOWeek(d);
    return `${y}-W${w.toString().padStart(2, '0')}`;
  }

  getResumenPorPeriodo(periodo: string, variable: string, tipo: 'mes' | 'semana' | 'dia'): number {
    return this.getFechas()
      .filter(f =>
        tipo === 'mes' ? f.startsWith(periodo) :
          tipo === 'semana' ? this.getSemanaISO(f) === periodo :
            f === periodo
      )
      .flatMap(f => this.groupedData[f])
      .filter(e => e.variable === variable)
      .reduce((sum, e) => sum + e.valor, 0);
  }

  generarIndicadores() {
    const variables = [
      { key: 'gmv', label: '1. GMV', esDinero: true },
      { key: 'cogs', label: '2. COGS', esDinero: true },
      { key: 'logistics_cost', label: '4. Costo Logístico', esDinero: true },
      { key: 'perssonel', label: '5. Costo de Personal', esDinero: true },
      { key: 'cost_tech', label: '6. Costo de Tecnología', esDinero: true },
      { key: 'cost_others', label: '7. Otros Costos', esDinero: true },
      { key: 'total_orders', label: '9.1. Órdenes', esDinero: false },
      { key: 'total_lines', label: '9.2. Líneas', esDinero: false }
    ];

    const meses = this.getMeses();
    const semanas = this.getSemanas();
    const dias = this.getFechasFiltradas();

    this.indicadoresMensuales = [
      ...variables.map(v => ({
        label: v.label,
        valores: meses.map(m => {
          const valor = this.getResumenPorPeriodo(m, v.key, 'mes');
          return {
            periodo: m,
            valor: v.esDinero
              ? valor.toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
              : valor
          };
        })
      })),
      {
        label: '9.3. AOV',
        valores: meses.map(m => {
          const gmv = this.getResumenPorPeriodo(m, 'gmv', 'mes');
          const orders = this.getResumenPorPeriodo(m, 'total_orders', 'mes') || 1;
          return {
            periodo: m,
            valor: (gmv / orders).toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
          };
        })
      },
      {
        label: '9.4. AOL',
        valores: meses.map(m => {
          const gmv = this.getResumenPorPeriodo(m, 'gmv', 'mes');
          const lines = this.getResumenPorPeriodo(m, 'total_lines', 'mes') || 1;
          return {
            periodo: m,
            valor: (gmv / lines).toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
          };
        })
      },
      {
        label: '3. Margen Bruto',
        valores: meses.map(m => {
          const gmv = this.getResumenPorPeriodo(m, 'gmv', 'mes');
          const cogs = this.getResumenPorPeriodo(m, 'cogs', 'mes');
          return {
            periodo: m,
            valor: gmv ? ((1 - (cogs * -1 / gmv)) * 100).toFixed(2) + '%' : 'N/A'
          };
        })
      },
      {
        label: '4.1. Margen Logístico',
        valores: meses.map(m => {
          const gmv = this.getResumenPorPeriodo(m, 'gmv', 'mes');
          const log = this.getResumenPorPeriodo(m, 'logistics_cost', 'mes');
          return {
            periodo: m,
            valor: gmv ? ((log / gmv) * 100).toFixed(2) + '%' : 'N/A'
          };
        })
      },
      {
        label: '8. Utilidad Neta',
        valores: meses.map(m => {
          const gmv = this.getResumenPorPeriodo(m, 'gmv', 'mes');
          const cogs = this.getResumenPorPeriodo(m, 'cogs', 'mes');
          const log = this.getResumenPorPeriodo(m, 'logistics_cost', 'mes');
          const personnel = this.getResumenPorPeriodo(m, 'perssonel', 'mes');
          const tech = this.getResumenPorPeriodo(m, 'cost_tech', 'mes');
          const others = this.getResumenPorPeriodo(m, 'cost_others', 'mes');
          const utilidadNeta = gmv + cogs + log + personnel + tech + others;
          return {
            periodo: m,
            valor: utilidadNeta.toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
          };
        })
      },
      {
        label: '8.1. Utilidad Neta %',
        valores: meses.map(m => {
          const gmv = this.getResumenPorPeriodo(m, 'gmv', 'mes');
          const cogs = this.getResumenPorPeriodo(m, 'cogs', 'mes');
          const log = this.getResumenPorPeriodo(m, 'logistics_cost', 'mes');
          const personnel = this.getResumenPorPeriodo(m, 'perssonel', 'mes');
          const tech = this.getResumenPorPeriodo(m, 'cost_tech', 'mes');
          const others = this.getResumenPorPeriodo(m, 'cost_others', 'mes');
          const utilidadNeta = gmv + cogs + log + personnel + tech + others;
          return {
            periodo: m,
            valor: gmv ? ((utilidadNeta / gmv) * 100).toFixed(2) + '%' : 'N/A'
          };
        })
      }
    ];
    this.indicadoresSemanales = [
      ...variables.map(v => ({
        label: v.label,
        valores: semanas.map(s => {
          const valor = this.getResumenPorPeriodo(s, v.key, 'semana');
          return {
            periodo: s,
            valor: v.esDinero
              ? valor.toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
              : valor
          };
        })
      })),
      {
        label: '8.3. AOV',
        valores: semanas.map(s => {
          const gmv = this.getResumenPorPeriodo(s, 'gmv', 'semana');
          const orders = this.getResumenPorPeriodo(s, 'total_orders', 'semana') || 1;
          return {
            periodo: s,
            valor: (gmv / orders).toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
          };
        })
      },
      {
        label: '8.4. AOL',
        valores: semanas.map(s => {
          const gmv = this.getResumenPorPeriodo(s, 'gmv', 'semana');
          const lines = this.getResumenPorPeriodo(s, 'total_lines', 'semana') || 1;
          return {
            periodo: s,
            valor: (gmv / lines).toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
          };
        })
      },
      {
        label: '3. Margen Bruto',
        valores: semanas.map(s => {
          const gmv = this.getResumenPorPeriodo(s, 'gmv', 'semana');
          const cogs = this.getResumenPorPeriodo(s, 'cogs', 'semana');
          return {
            periodo: s,
            valor: gmv ? ((1 - (cogs * -1 / gmv)) * 100).toFixed(2) + '%' : 'N/A'
          };
        })
      },
      {
        label: '4.1. Margen Logístico',
        valores: semanas.map(s => {
          const gmv = this.getResumenPorPeriodo(s, 'gmv', 'semana');
          const log = this.getResumenPorPeriodo(s, 'logistics_cost', 'semana');
          return {
            periodo: s,
            valor: gmv ? ((log / gmv) * 100).toFixed(2) + '%' : 'N/A'
          };
        })
      }
    ];
    this.indicadoresDiarios = [
      ...variables.map(v => ({
        label: v.label,
        valores: dias.map(d => {
          const valor = this.getResumenPorPeriodo(d, v.key, 'dia');
          return {
            periodo: d,
            valor: v.esDinero
              ? valor.toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
              : valor
          };
        })
      })),
      {
        label: '8.3. AOV',
        valores: dias.map(d => {
          const gmv = this.getResumenPorPeriodo(d, 'gmv', 'dia');
          const orders = this.getResumenPorPeriodo(d, 'total_orders', 'dia') || 1;
          return {
            periodo: d,
            valor: (gmv / orders).toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
          };
        })
      },
      {
        label: '8.4. AOL',
        valores: dias.map(d => {
          const gmv = this.getResumenPorPeriodo(d, 'gmv', 'dia');
          const lines = this.getResumenPorPeriodo(d, 'total_lines', 'dia') || 1;
          return {
            periodo: d,
            valor: (gmv / lines).toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
          };
        })
      },
      {
        label: '3. Margen Bruto',
        valores: dias.map(d => {
          const gmv = this.getResumenPorPeriodo(d, 'gmv', 'dia');
          const cogs = this.getResumenPorPeriodo(d, 'cogs', 'dia');
          return {
            periodo: d,
            valor: gmv ? ((1 - (cogs * -1 / gmv)) * 100).toFixed(2) + '%' : 'N/A'
          };
        })
      },
      {
        label: '4.1. Margen Logístico',
        valores: dias.map(d => {
          const gmv = this.getResumenPorPeriodo(d, 'gmv', 'dia');
          const log = this.getResumenPorPeriodo(d, 'logistics_cost', 'dia');
          return {
            periodo: d,
            valor: gmv ? ((log / gmv) * 100).toFixed(2) + '%' : 'N/A'
          };
        })
      }
    ];

    this.indicadoresMensuales.sort((a, b) => a.label.localeCompare(b.label));
    this.indicadoresSemanales.sort((a, b) => a.label.localeCompare(b.label));
    this.indicadoresDiarios.sort((a, b) => a.label.localeCompare(b.label));
  }
}
