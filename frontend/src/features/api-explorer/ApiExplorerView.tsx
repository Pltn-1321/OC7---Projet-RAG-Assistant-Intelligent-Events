import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { HealthTab } from "./HealthTab"
import { SearchTab } from "./SearchTab"
import { ChatTab } from "./ChatTab"
import { SessionTab } from "./SessionTab"
import { RebuildTab } from "./RebuildTab"
import { Activity, Search, MessageSquare, History, RefreshCw } from "lucide-react"

export function ApiExplorerView() {
  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">API Explorer</h1>
        <p className="text-slate-400">
          Test all FastAPI endpoints manually with interactive forms
        </p>
      </div>

      <Tabs defaultValue="health" className="w-full">
        <TabsList className="grid w-full grid-cols-5 mb-6">
          <TabsTrigger value="health" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Health
          </TabsTrigger>
          <TabsTrigger value="search" className="flex items-center gap-2">
            <Search className="h-4 w-4" />
            Search
          </TabsTrigger>
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Chat
          </TabsTrigger>
          <TabsTrigger value="session" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            Session
          </TabsTrigger>
          <TabsTrigger value="rebuild" className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Rebuild
          </TabsTrigger>
        </TabsList>

        <TabsContent value="health">
          <HealthTab />
        </TabsContent>

        <TabsContent value="search">
          <SearchTab />
        </TabsContent>

        <TabsContent value="chat">
          <ChatTab />
        </TabsContent>

        <TabsContent value="session">
          <SessionTab />
        </TabsContent>

        <TabsContent value="rebuild">
          <RebuildTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
