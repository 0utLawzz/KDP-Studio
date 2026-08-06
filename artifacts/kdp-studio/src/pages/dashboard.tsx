import { useGetDashboardStats } from "@workspace/api-client-react";
import { BookOpen, CheckSquare, FileText, Plus } from "lucide-react";
import { Link } from "wouter";
import { format } from "date-fns";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function Dashboard() {
  const { data: stats, isLoading, isError } = useGetDashboardStats();

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-10 w-48 bg-muted rounded"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-muted rounded-xl"></div>
          ))}
        </div>
      </div>
    );
  }

  if (isError || !stats) {
    return (
      <div className="py-12 text-center text-destructive">
        <p>Failed to load dashboard data. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-serif text-foreground">Studio Overview</h1>
          <p className="text-muted-foreground mt-1">Your creative production at a glance.</p>
        </div>
        <Link href="/books/new" className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 gap-2 shadow-sm">
          <Plus className="w-4 h-4" />
          Create New Book
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="shadow-sm border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Books</CardTitle>
            <BookOpen className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-serif">{stats.totalBooks}</div>
            <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
              <span className="inline-flex items-center rounded-full bg-secondary px-2 py-0.5 font-medium">{stats.byStatus.draft} drafts</span>
              <span className="inline-flex items-center rounded-full bg-primary/10 text-primary px-2 py-0.5 font-medium">{stats.byStatus.published} published</span>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Generated Files</CardTitle>
            <FileText className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-serif">{stats.totalFiles}</div>
            <p className="text-xs text-muted-foreground mt-2">Ready for upload</p>
          </CardContent>
        </Card>

        <Card className="shadow-sm border-border/50 bg-card/50 backdrop-blur-sm lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Tasks</CardTitle>
            <CheckSquare className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-6">
              <div>
                <div className="text-3xl font-serif">{stats.tasksCount.inProgress}</div>
                <p className="text-xs text-muted-foreground mt-2">In progress</p>
              </div>
              <div className="flex-1 flex gap-2 h-2 rounded-full overflow-hidden bg-muted">
                {stats.tasksCount.done > 0 && <div className="bg-primary h-full transition-all" style={{ width: `${(stats.tasksCount.done / (stats.tasksCount.done + stats.tasksCount.inProgress + stats.tasksCount.notStarted)) * 100}%` }} />}
                {stats.tasksCount.inProgress > 0 && <div className="bg-primary/40 h-full transition-all" style={{ width: `${(stats.tasksCount.inProgress / (stats.tasksCount.done + stats.tasksCount.inProgress + stats.tasksCount.notStarted)) * 100}%` }} />}
                {stats.tasksCount.notStarted > 0 && <div className="bg-muted-foreground/20 h-full transition-all" style={{ width: `${(stats.tasksCount.notStarted / (stats.tasksCount.done + stats.tasksCount.inProgress + stats.tasksCount.notStarted)) * 100}%` }} />}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-serif text-foreground">Recent Projects</h2>
        {stats.recentBooks.length === 0 ? (
          <div className="text-center py-12 bg-card rounded-xl border border-dashed border-border/50">
            <p className="text-muted-foreground mb-4">No books created yet.</p>
            <Link href="/books/new">
              <Button variant="outline">Start your first book</Button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {stats.recentBooks.map((book) => (
              <Link key={book.id} href={`/books/${book.id}`} className="block group">
                <Card className="h-full transition-all hover:shadow-md hover:border-primary/30">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start gap-2">
                      <CardTitle className="text-lg font-serif leading-tight group-hover:text-primary transition-colors line-clamp-2">
                        {book.title}
                      </CardTitle>
                      <span className={`px-2 py-1 rounded text-[10px] uppercase font-bold tracking-wider whitespace-nowrap ${
                        book.status === 'published' ? 'bg-primary/10 text-primary' : 
                        book.status === 'generated' ? 'bg-blue-500/10 text-blue-700' : 'bg-secondary text-muted-foreground'
                      }`}>
                        {book.status}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground truncate">{book.niche} • {book.trimSize}</p>
                    <p className="text-xs text-muted-foreground/70 mt-4">Updated {format(new Date(book.updatedAt), 'MMM d, yyyy')}</p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
