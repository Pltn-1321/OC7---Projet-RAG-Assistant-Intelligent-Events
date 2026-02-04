import { useMutation } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { api } from "@/lib/api/endpoints"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ResponseViewer } from "@/components/common/ResponseViewer"
import { getErrorMessage } from "@/lib/api/error-types"
import { Search, Loader2 } from "lucide-react"

const searchSchema = z.object({
  query: z.string().min(1, "Query is required"),
  top_k: z.number().min(1).max(20),
})

type SearchFormData = z.infer<typeof searchSchema>

export function SearchTab() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SearchFormData>({
    resolver: zodResolver(searchSchema),
    defaultValues: {
      top_k: 5,
    },
  })

  const { mutate, isPending, data, error } = useMutation({
    mutationFn: api.search.search,
  })

  const onSubmit = (formData: SearchFormData) => {
    mutate(formData)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Semantic Search
          </CardTitle>
          <CardDescription>
            Perform stateless semantic search without session management
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="query">Query *</Label>
              <Input
                id="query"
                placeholder="concerts ce weekend à Marseille"
                {...register("query")}
              />
              {errors.query && (
                <p className="text-sm text-red-400">{errors.query.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="top_k">Top K Results (1-20)</Label>
              <Input
                id="top_k"
                type="number"
                min={1}
                max={20}
                {...register("top_k", { valueAsNumber: true })}
              />
              {errors.top_k && (
                <p className="text-sm text-red-400">{errors.top_k.message}</p>
              )}
            </div>

            <Button type="submit" disabled={isPending} className="w-full">
              {isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Searching...
                </>
              ) : (
                "Search"
              )}
            </Button>
          </form>

          {error && (
            <div className="mt-4 p-4 rounded-md bg-red-900/20 border border-red-900 text-red-200">
              <p className="font-semibold">Error</p>
              <p className="text-sm">{getErrorMessage(error, "Search failed")}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {data && (
        <Card>
          <CardHeader>
            <CardTitle>Search Results</CardTitle>
            <CardDescription>
              Found {data.results.length} results for: {data.query}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 overflow-y-auto max-h-[60vh] pr-2">
              {data.results.map((result, index) => (
                <Card key={index} className="bg-slate-800 text-slate-100">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-base text-white">{result.title}</CardTitle>
                      <div className="flex gap-2">
                        <Badge variant="secondary">
                          Similarity: {(result.similarity * 100).toFixed(1)}%
                        </Badge>
                        <Badge variant="outline">
                          Distance: {result.distance.toFixed(3)}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-slate-300 line-clamp-3">
                      {result.content}
                    </p>
                    {result.metadata && Object.keys(result.metadata).length > 0 && (
                      <details className="mt-2">
                        <summary className="text-xs text-slate-400 cursor-pointer hover:text-slate-300">
                          View Metadata
                        </summary>
                        <pre className="mt-2 text-xs text-slate-200 bg-slate-950 p-2 rounded overflow-auto">
                          {JSON.stringify(result.metadata, null, 2)}
                        </pre>
                      </details>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {data && <ResponseViewer data={data} title="Raw Response" />}
    </div>
  )
}
