import { Badge } from "@/components/ui/badge"

interface PaymentStatusBadgeProps {
  status: "pagado" | "pendiente" | "atrasado"
}

export function PaymentStatusBadge({ status }: PaymentStatusBadgeProps) {
  const variants = {
    pagado: "bg-green-100 text-green-800 hover:bg-green-100",
    pendiente: "bg-yellow-100 text-yellow-800 hover:bg-yellow-100",
    atrasado: "bg-red-100 text-red-800 hover:bg-red-100",
  }

  const labels = {
    pagado: "Pagado",
    pendiente: "Pendiente",
    atrasado: "Atrasado",
  }

  return (
    <Badge className={variants[status]} variant="secondary">
      {labels[status]}
    </Badge>
  )
}
