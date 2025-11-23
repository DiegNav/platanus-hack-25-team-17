export interface Participante {
  id: string
  nombre: string
  vecesJuntos: number
  tiempoPromedioTransferenciaHoras: number
  montoReembolsadoEnEstaCompra: number
  estadoPago: "pagado" | "pendiente" | "atrasado"
}

export interface SessionData {
  sessionId: string
  tituloCompra: string
  fecha: string
  montoTotal: number
}

export const mockSession: SessionData = {
  sessionId: "7f3a8b2c-9e4d-4c1a-8f6e-2d7b9c5a1e3f",
  tituloCompra: "Sushi del viernes",
  fecha: "21 de noviembre 2025",
  montoTotal: 58990,
}

export const mockParticipants: Participante[] = [
  {
    id: "1",
    nombre: "Diego Navarrete",
    vecesJuntos: 12,
    tiempoPromedioTransferenciaHoras: 2.5,
    montoReembolsadoEnEstaCompra: 14720,
    estadoPago: "pagado",
  },
  {
    id: "2",
    nombre: "María González",
    vecesJuntos: 8,
    tiempoPromedioTransferenciaHoras: 4.2,
    montoReembolsadoEnEstaCompra: 14720,
    estadoPago: "pendiente",
  },
  {
    id: "3",
    nombre: "Carlos Pérez",
    vecesJuntos: 15,
    tiempoPromedioTransferenciaHoras: 1.8,
    montoReembolsadoEnEstaCompra: 14720,
    estadoPago: "pagado",
  },
  {
    id: "4",
    nombre: "Ana Martínez",
    vecesJuntos: 5,
    tiempoPromedioTransferenciaHoras: 8.5,
    montoReembolsadoEnEstaCompra: 14830,
    estadoPago: "atrasado",
  },
]
