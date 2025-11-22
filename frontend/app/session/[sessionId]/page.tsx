import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { PaymentStatusBadge } from "@/components/payment-status-badge"
import { mockSession, mockParticipants } from "@/lib/mockData"

interface PageProps {
  params: Promise<{
    sessionId: string
  }>
}

export default async function SessionPage({ params }: PageProps) {
  const { sessionId } = await params

  // Cálculos basados en los datos mock (luego reemplazar con datos reales)
  const totalParticipantes = mockParticipants.length
  const montoTotalReembolsado = mockParticipants.reduce((sum, p) => sum + p.montoReembolsadoEnEstaCompra, 0)
  const tiempoPromedioGrupo =
    mockParticipants.reduce((sum, p) => sum + p.tiempoPromedioTransferenciaHoras, 0) / mockParticipants.length

  // Formatear moneda CLP
  const formatCLP = (amount: number) => {
    return new Intl.NumberFormat("es-CL", {
      style: "currency",
      currency: "CLP",
      minimumFractionDigits: 0,
    }).format(amount)
  }

  // Formatear tiempo en horas
  const formatHours = (hours: number) => {
    const fullHours = Math.floor(hours)
    const minutes = Math.round((hours - fullHours) * 60)

    if (minutes === 0) {
      return `${fullHours}h`
    }
    return `${fullHours}h ${minutes}min`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{mockSession.tituloCompra}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-600">
            <span>{mockSession.fecha}</span>
            <span className="hidden sm:inline">•</span>
            <span className="font-mono text-xs">ID: {sessionId.slice(0, 8)}...</span>
          </div>
          <div className="mt-4">
            <span className="text-4xl font-bold text-gray-900">{formatCLP(mockSession.montoTotal)}</span>
            <span className="ml-2 text-sm text-gray-600">Total de la compra</span>
          </div>
        </div>

        {/* Resumen General - Cards */}
        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Total Participantes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{totalParticipantes}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Monto Total Reembolsado</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{formatCLP(montoTotalReembolsado)}</div>
            </CardContent>
          </Card>

          <Card className="sm:col-span-2 lg:col-span-1">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Tiempo Promedio de Transferencia</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{formatHours(tiempoPromedioGrupo)}</div>
            </CardContent>
          </Card>
        </div>

        {/* Tabla de Participantes */}
        <Card>
          <CardHeader>
            <CardTitle>Participantes del Grupo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nombre</TableHead>
                    <TableHead className="text-center">Veces Juntos</TableHead>
                    <TableHead className="text-center">Tiempo Promedio</TableHead>
                    <TableHead className="text-right">Monto Reembolsado</TableHead>
                    <TableHead className="text-center">Estado</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockParticipants.map((participante) => (
                    <TableRow key={participante.id}>
                      <TableCell className="font-medium">{participante.nombre}</TableCell>
                      <TableCell className="text-center">{participante.vecesJuntos}</TableCell>
                      <TableCell className="text-center">
                        {formatHours(participante.tiempoPromedioTransferenciaHoras)}
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {formatCLP(participante.montoReembolsadoEnEstaCompra)}
                      </TableCell>
                      <TableCell className="text-center">
                        <PaymentStatusBadge status={participante.estadoPago} />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {/* Nota sobre datos mock */}
            <div className="mt-6 rounded-lg bg-blue-50 p-4">
              <p className="text-sm text-blue-800">
                <span className="font-semibold">Nota:</span> Estos datos son mockeados. Luego se conectarán a la base de
                datos real.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
