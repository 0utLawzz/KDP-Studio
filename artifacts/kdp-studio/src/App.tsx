import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";

import { Layout } from "@/components/layout";
import { Dashboard } from "@/pages/dashboard";
import { BookLibrary } from "@/pages/books";
import { NewBook } from "@/pages/books/new";
import { BookDetail } from "@/pages/books/detail";
import { Palettes } from "@/pages/palettes";
import { Tasks } from "@/pages/tasks";
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient();

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/books" component={BookLibrary} />
        <Route path="/books/new" component={NewBook} />
        <Route path="/books/:id" component={BookDetail} />
        <Route path="/palettes" component={Palettes} />
        <Route path="/tasks" component={Tasks} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
