import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ResponseViewerProps {
  data: any
  title?: string
}

export function ResponseViewer({ data, title = "Response" }: ResponseViewerProps) {
  if (!data) {
    return null
  }

  return (
    <Card className="mt-4">
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <pre className="bg-slate-950 text-green-400 p-4 rounded overflow-auto max-h-[500px] text-xs">
          {JSON.stringify(data, null, 2)}
        </pre>
      </CardContent>
    </Card>
  )
}
