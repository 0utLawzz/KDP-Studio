import {
  getListBooksQueryKey,
  type Book,
  type Palette,
  useListBooks,
  useListPalettes,
  useUpdateBook,
} from "@workspace/api-client-react";
import { useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { BookOpen, Check, CircleAlert, FilePlus2, Loader2, Plus, Search, SlidersHorizontal } from "lucide-react";
import { Link } from "wouter";
import { format } from "date-fns";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

type BoardStatus = "planned" | "in_progress" | "generated" | "published";

const columns: Array<{
  key: BoardStatus;
  label: string;
  note: string;
  accent: string;
  dot: string;
}> = [
  { key: "planned", label: "Planned", note: "shape the next idea", accent: "border-t-[#baa58a]", dot: "bg-[#baa58a]" },
  { key: "in_progress", label: "In progress", note: "in the making", accent: "border-t-[#c67d5d]", dot: "bg-[#c67d5d]" },
  { key: "generated", label: "Generated", note: "ready for a careful look", accent: "border-t-[#6b8f8d]", dot: "bg-[#6b8f8d]" },
  { key: "published", label: "Published", note: "out in the world", accent: "border-t-[#879b72]", dot: "bg-[#879b72]" },
];

const statusLabel: Record<BoardStatus, string> = {
  planned: "Planned",
  in_progress: "In progress",
  generated: "Generated",
  published: "Published",
};

function normalizedStatus(status: Book["status"]): BoardStatus {
  return status === "draft" ? "planned" : status;
}

function formatUpdated(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "recently" : format(date, "MMM d, yyyy");
}

function BookCard({
  book,
  palette,
  onStatusChange,
  isUpdating,
}: {
  book: Book;
  palette?: Palette;
  onStatusChange: (book: Book, status: BoardStatus) => void;
  isUpdating: boolean;
}) {
  const currentStatus = normalizedStatus(book.status);
  const progress = Math.min(100, Math.max(0, book.generationProgress ?? 0));

  return (
    <Card className="group overflow-hidden rounded-[3px] border-[#ddd5c7] bg-[#fffdf8] shadow-[0_5px_18px_rgba(65,54,39,0.045)] transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-[0_10px_24px_rgba(65,54,39,0.09)]">
      <div
        className="h-1"
        style={{ background: palette?.primary || "hsl(var(--primary))" }}
      />
      <CardHeader className="space-y-3 p-4 pb-3">
        <div className="flex items-start justify-between gap-3">
          <Link
            href={`/books/${book.id}`}
            className="min-w-0 text-[17px] font-serif font-medium leading-[1.15] text-[#34443e] underline-offset-4 hover:text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {book.title}
          </Link>
          <span className="shrink-0 font-mono text-[10px] tracking-[0.12em] text-[#a59b8b]">
            #{String(book.id).padStart(3, "0")}
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-[11px] font-medium uppercase tracking-[0.1em] text-[#8b8173]">
          <span>{book.category || book.niche}</span>
          {book.category && book.niche && <span className="text-[#c3b9aa]">/</span>}
          {book.category && <span className="normal-case tracking-normal text-[#9a9184]">{book.niche}</span>}
        </div>
      </CardHeader>
      <CardContent className="space-y-4 p-4 pt-0">
        <div className="flex items-center justify-between border-y border-[#eee8de] py-3 text-[12px] text-[#7c7468]">
          <span className="flex min-w-0 items-center gap-2">
            <span
              aria-label={palette ? `${palette.name} palette` : "Color palette"}
              className="h-5 w-5 shrink-0 rounded-full border border-[#d7cebf]"
              style={{
                background: palette
                  ? `linear-gradient(135deg, ${palette.primary} 0 34%, ${palette.secondary} 34% 67%, ${palette.accent} 67%)`
                  : "hsl(var(--muted))",
              }}
            />
            <span className="truncate">{palette?.name || book.colorPalette || "Unassigned palette"}</span>
          </span>
          <span className="shrink-0 font-mono text-[11px] text-[#958b7d]">{book.templateKey || "original template"}</span>
        </div>
        <div className="grid grid-cols-3 gap-2 text-[11px] text-[#8b8173]">
          <div><p className="font-mono text-[10px] uppercase tracking-[0.08em] text-[#b0a698]">Trim</p><p className="mt-1 font-medium text-[#5b655f]">{book.trimSize}</p></div>
          <div><p className="font-mono text-[10px] uppercase tracking-[0.08em] text-[#b0a698]">Days</p><p className="mt-1 font-medium text-[#5b655f]">{book.dayCount}</p></div>
          <div><p className="font-mono text-[10px] uppercase tracking-[0.08em] text-[#b0a698]">Pages</p><p className="mt-1 font-medium text-[#5b655f]">{book.lastPageCount || "—"}</p></div>
        </div>
        {(currentStatus === "in_progress" || progress > 0) && (
          <div className="space-y-1.5">
            <div className="flex justify-between font-mono text-[10px] uppercase tracking-[0.08em] text-[#a1988c]">
              <span>Production progress</span><span>{progress}%</span>
            </div>
            <div className="h-1 overflow-hidden rounded-full bg-[#e9e4da]">
              <div className="h-full rounded-full bg-[#c67d5d] transition-[width] duration-300" style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}
        <div className="flex items-center justify-between gap-2 pt-1">
          <span className="text-[11px] text-[#a1988c]">Updated {formatUpdated(book.updatedAt)}</span>
          <div className="relative">
            <Select
              value={currentStatus}
              onValueChange={(value) => onStatusChange(book, value as BoardStatus)}
              disabled={isUpdating}
            >
              <SelectTrigger
                aria-label={`Move ${book.title} to another status`}
                className="h-8 w-[122px] gap-1 rounded-[2px] border-[#ddd5c7] bg-[#faf7f0] px-2.5 text-[11px] text-[#5d685f]"
              >
                {isUpdating ? <Loader2 className="h-3 w-3 animate-spin" /> : <Check className="h-3 w-3 text-[#879b72]" />}
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {columns.map((column) => <SelectItem key={column.key} value={column.key}>{statusLabel[column.key]}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function Dashboard() {
  const queryClient = useQueryClient();
  const { data: books, isLoading, isError, refetch } = useListBooks();
  const { data: palettes } = useListPalettes();
  const updateBook = useUpdateBook();
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");

  const paletteMap = useMemo(() => new Map((palettes || []).map((palette) => [palette.key, palette])), [palettes]);
  const categories = useMemo(
    () => Array.from(new Set((books || []).map((book) => book.category || book.niche).filter(Boolean))).sort(),
    [books],
  );
  const filteredBooks = useMemo(() => {
    const query = search.trim().toLowerCase();
    return (books || []).filter((book) => {
      const matchesSearch = !query || [book.title, book.niche, book.category, book.targetAudience, book.templateKey]
        .filter(Boolean).join(" ").toLowerCase().includes(query);
      const matchesCategory = category === "all" || (book.category || book.niche) === category;
      return matchesSearch && matchesCategory;
    });
  }, [books, category, search]);

  const handleStatusChange = (book: Book, status: BoardStatus) => {
    if (status === normalizedStatus(book.status)) return;
    updateBook.mutate(
      { id: book.id, data: { status } },
      { onSuccess: () => queryClient.invalidateQueries({ queryKey: getListBooksQueryKey() }) },
    );
  };

  const updatingId = updateBook.isPending ? updateBook.variables?.id : undefined;
  const total = books?.length || 0;
  const published = (books || []).filter((book) => normalizedStatus(book.status) === "published").length;

  if (isLoading) {
    return (
      <div className="space-y-8" aria-busy="true">
        <div className="space-y-3"><div className="h-3 w-24 animate-pulse bg-[#e9e3d8]" /><div className="h-12 w-80 animate-pulse bg-[#e9e3d8]" /><div className="h-4 w-96 max-w-full animate-pulse bg-[#eee9e0]" /></div>
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">{columns.map((column) => <div key={column.key} className="h-[390px] animate-pulse rounded-[3px] border border-[#e5ded2] bg-[#f4f0e8]" />)}</div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex min-h-[55vh] items-center justify-center">
        <div className="max-w-md border border-[#dfc9bd] bg-[#fff9f5] p-8 text-center">
          <CircleAlert className="mx-auto mb-4 h-7 w-7 text-[#bd6d53]" />
          <h1 className="font-serif text-2xl text-[#4d443b]">The desk is taking a moment</h1>
          <p className="mt-2 text-sm leading-6 text-[#8b8173]">We couldn’t load your production list. Nothing has been changed.</p>
          <Button className="mt-5 rounded-[2px]" onClick={() => refetch()}>Try again</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-10">
      <header className="flex flex-col gap-6 border-b border-[#ded6c9] pb-7 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="mb-3 font-mono text-[10px] uppercase tracking-[0.22em] text-[#a08f7d]">Bright Mindful Pages / production desk</p>
          <h1 className="max-w-2xl text-4xl font-serif font-medium leading-[0.98] tracking-[-0.035em] text-[#34443e] md:text-5xl">A quiet place for good work.</h1>
          <p className="mt-4 max-w-xl text-sm leading-6 text-[#83796d]">Move each planner, journal, and tracker from first thought to the hands of its reader.</p>
        </div>
        <Link href="/books/new" className="inline-flex min-h-10 items-center justify-center gap-2 self-start rounded-[2px] border border-[#34443e] bg-[#34443e] px-4 py-2 text-sm font-medium text-[#fbf8f1] shadow-sm transition-transform hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring lg:self-end">
          <FilePlus2 className="h-4 w-4" /> Add a book
        </Link>
      </header>

      <section className="grid grid-cols-2 gap-3 border-b border-[#ded6c9] pb-6 sm:grid-cols-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[0.15em] text-[#a08f7d]">On the desk</p><p className="mt-1 font-serif text-2xl text-[#34443e]">{total}</p></div>
        <div><p className="font-mono text-[10px] uppercase tracking-[0.15em] text-[#a08f7d]">Published</p><p className="mt-1 font-serif text-2xl text-[#879b72]">{published}</p></div>
        <div className="col-span-2 flex items-end justify-end text-right"><p className="max-w-[260px] text-xs leading-5 text-[#9a9184]">Four gentle steps, one view. Use the status control on any card to keep the desk honest.</p></div>
      </section>

      <section className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between" aria-label="Board filters">
        <div className="relative w-full md:max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#a69b8d]" />
          <Input type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search titles, niches, or templates" className="h-10 rounded-[2px] border-[#dcd4c8] bg-[#fffdf8] pl-9 text-sm shadow-none placeholder:text-[#aaa092]" />
        </div>
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-[#9c9182]" />
          <Select value={category} onValueChange={setCategory}>
            <SelectTrigger className="h-10 w-full min-w-[180px] rounded-[2px] border-[#dcd4c8] bg-[#fffdf8] text-sm md:w-auto"><SelectValue placeholder="All categories" /></SelectTrigger>
            <SelectContent><SelectItem value="all">All categories</SelectItem>{categories.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
          </Select>
        </div>
      </section>

      {total === 0 ? (
        <div className="border border-dashed border-[#d7cdbf] bg-[#fffdf8] px-6 py-16 text-center">
          <BookOpen className="mx-auto mb-4 h-7 w-7 text-[#b6a996]" />
          <h2 className="font-serif text-2xl text-[#4b584f]">The desk is ready for its first idea.</h2>
          <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-[#8b8173]">Start with a planner, journal, or tracker. You can refine the details as the work takes shape.</p>
          <Link href="/books/new" className="mt-6 inline-flex min-h-9 items-center gap-2 rounded-[2px] border border-[#879b72] px-4 py-2 text-sm font-medium text-[#587051] hover:bg-[#eff2e9]"><Plus className="h-4 w-4" /> Create the first book</Link>
        </div>
      ) : filteredBooks.length === 0 ? (
        <div className="border border-dashed border-[#d7cdbf] bg-[#fffdf8] px-6 py-14 text-center">
          <Search className="mx-auto mb-4 h-6 w-6 text-[#b6a996]" />
          <h2 className="font-serif text-xl text-[#4b584f]">No books match that view.</h2>
          <p className="mt-2 text-sm text-[#8b8173]">Try a different word or clear the category filter.</p>
          <Button variant="outline" className="mt-5 rounded-[2px]" onClick={() => { setSearch(""); setCategory("all"); }}>Clear filters</Button>
        </div>
      ) : (
        <div className="-mx-4 overflow-x-auto px-4 pb-4 md:-mx-8 md:px-8 lg:-mx-12 lg:px-12" aria-label="Book production board">
          <div className="grid min-w-[1120px] grid-cols-4 gap-4">
            {columns.map((column) => {
              const columnBooks = filteredBooks.filter((book) => normalizedStatus(book.status) === column.key);
              return (
                <section key={column.key} className={cn("min-h-[300px] border-t-[3px] bg-[#f3efe7]/70 px-3 pb-3 pt-4", column.accent)} aria-labelledby={`column-${column.key}`}>
                  <div className="mb-4 flex items-start justify-between gap-2 px-1">
                    <div><h2 id={`column-${column.key}`} className="flex items-center gap-2 font-serif text-xl text-[#4b584f]"><span className={cn("h-2 w-2 rounded-full", column.dot)} />{column.label}</h2><p className="mt-1 text-[11px] text-[#a1988c]">{column.note}</p></div>
                    <span className="font-mono text-xs text-[#a1988c]">{String(columnBooks.length).padStart(2, "0")}</span>
                  </div>
                  <div className="space-y-3">
                    {columnBooks.map((book) => <BookCard key={book.id} book={book} palette={paletteMap.get(book.colorPalette)} onStatusChange={handleStatusChange} isUpdating={updatingId === book.id} />)}
                    {columnBooks.length === 0 && <div className="border border-dashed border-[#d8cfc1] px-3 py-8 text-center text-xs leading-5 text-[#aaa092]">Nothing here yet.<br />The next good move can start here.</div>}
                  </div>
                </section>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
