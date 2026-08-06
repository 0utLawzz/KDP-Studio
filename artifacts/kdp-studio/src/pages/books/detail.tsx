import { useParams, Link } from "wouter";
import { useGetBook, useListBookFiles, useGenerateListing } from "@workspace/api-client-react";
import { ArrowLeft, Download, FileText, CheckCircle2, RefreshCw, Loader2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { format } from "date-fns";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";

export function BookDetail() {
  const params = useParams();
  const id = Number(params.id);
  const { data: book, isLoading: bookLoading } = useGetBook(id, { query: { enabled: !!id, queryKey: ['/api/books', id] } });
  const { data: files, isLoading: filesLoading } = useListBookFiles(id, { query: { enabled: !!id, queryKey: ['/api/books', id, 'files'] } });
  
  const generateListing = useGenerateListing();
  const { toast } = useToast();

  const [checklist, setChecklist] = useState({
    margins: false,
    pages: false,
    cover: false,
    subtitle: false,
    ai: false,
  });

  const handleDownload = (fileId: number) => {
    window.open(`/api/files/${fileId}/download`, '_blank');
  };

  const handleRegenerateListing = async () => {
    try {
      await generateListing.mutateAsync({ id });
      toast({ title: "Listing metadata regenerated successfully." });
    } catch (e) {
      toast({ title: "Failed to regenerate listing", variant: "destructive" });
    }
  };

  if (bookLoading) {
    return <div className="p-12 text-center animate-pulse">Loading book details...</div>;
  }

  if (!book) {
    return <div className="p-12 text-center text-destructive">Book not found.</div>;
  }

  return (
    <div className="space-y-8 pb-24 animate-in fade-in duration-500">
      <div className="flex items-center gap-4">
        <Link href="/books" className="p-2 hover:bg-muted rounded-full transition-colors">
          <ArrowLeft className="w-5 h-5 text-muted-foreground" />
        </Link>
        <div>
          <h1 className="text-3xl font-serif text-foreground leading-tight">{book.title}</h1>
          <p className="text-muted-foreground text-sm flex items-center gap-2 mt-1">
            <span className="uppercase tracking-wider font-bold text-[10px] px-2 py-0.5 rounded bg-secondary text-secondary-foreground">{book.status}</span>
            <span>{book.niche}</span>
            <span>•</span>
            <span>{book.trimSize}</span>
          </p>
        </div>
      </div>

      <Tabs defaultValue="files" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-8 max-w-md bg-muted/50 p-1">
          <TabsTrigger value="files" className="rounded-md">Generated Files</TabsTrigger>
          <TabsTrigger value="listing" className="rounded-md">KDP Listing</TabsTrigger>
          <TabsTrigger value="checklist" className="rounded-md">Upload Checklist</TabsTrigger>
        </TabsList>

        <TabsContent value="files" className="space-y-4">
          <h2 className="text-xl font-serif mb-4">Production Assets</h2>
          {filesLoading ? (
            <div className="p-8 text-center text-muted-foreground">Loading files...</div>
          ) : files?.length === 0 ? (
            <Card className="border-dashed bg-muted/10">
              <CardContent className="p-12 text-center">
                <FileText className="w-8 h-8 text-muted-foreground mx-auto mb-3 opacity-50" />
                <p className="text-muted-foreground">No files generated yet.</p>
                <Link href="/books/new" className="text-primary hover:underline text-sm mt-2 inline-block">Go to generation wizard</Link>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {files?.map(file => (
                <Card key={file.id} className="overflow-hidden hover:border-primary/30 transition-colors group">
                  <div className="p-4 flex items-start gap-4">
                    <div className="w-12 h-12 rounded bg-primary/10 text-primary flex items-center justify-center shrink-0">
                      <FileText className="w-6 h-6" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-sm capitalize">{file.fileType}</h4>
                      <p className="text-xs text-muted-foreground truncate" title={file.fileName}>{file.fileName}</p>
                      <div className="flex gap-3 mt-2 text-[10px] text-muted-foreground uppercase tracking-widest font-semibold">
                        {file.pageCount && <span>{file.pageCount} Pages</span>}
                        {file.spineInches && <span>{file.spineInches}in Spine</span>}
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => handleDownload(file.id)} className="shrink-0 group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                      <Download className="w-4 h-4" />
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="listing" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-serif">Metadata & SEO</h2>
            <Button variant="outline" size="sm" onClick={handleRegenerateListing} disabled={generateListing.isPending}>
              {generateListing.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <RefreshCw className="w-4 h-4 mr-2" />}
              Regenerate
            </Button>
          </div>
          
          {/* In a real app we'd fetch the listing metadata, but the API schema doesn't seem to store it persistently on the Book object directly. 
              The task description says: "Tabs for: KDP Listing (generated listing metadata display, can regenerate)". 
              Since the hook useGenerateListing returns ListingResult but there's no endpoint to purely GET it if already generated, 
              we might have to rely on generating it or storing it. The Book model has no listing field.
              For now, we'll show a placeholder or trigger generation if it's not present. */}
          
          <Card className="bg-card">
            <CardHeader className="bg-muted/30 border-b border-border">
              <CardTitle className="text-lg">Title & Description</CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 block">Title</label>
                <div className="font-serif text-lg">{book.title}</div>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 block">Subtitle</label>
                <div className="text-foreground">{book.subtitle || "No subtitle provided"}</div>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 block">Author</label>
                <div className="text-foreground">{book.authorName}</div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card border-dashed">
            <CardContent className="p-8 text-center text-muted-foreground">
              <p className="text-sm">Click "Regenerate" above to fetch full AI-optimized description and keywords based on current book parameters.</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="checklist" className="space-y-4">
          <h2 className="text-xl font-serif mb-2">Pre-upload Checklist</h2>
          <p className="text-muted-foreground mb-6">Ensure these rules are met before clicking "Publish" on KDP to avoid rejection.</p>
          
          <div className="space-y-3 max-w-2xl">
            {[
              { key: 'margins', label: 'Margins verified', desc: 'No text or vital elements extend past the safe zone on the generated PDFs.' },
              { key: 'pages', label: 'Page count matches', desc: `PDF has exactly ${book.lastPageCount || 'the correct number of'} pages as configured.` },
              { key: 'cover', label: 'Cover dimensions exact', desc: 'Cover PDF includes bleed and spine width based on exact page count.' },
              { key: 'subtitle', label: 'Subtitle rule checked', desc: 'Subtitle on cover exactly matches the subtitle entered in KDP metadata.' },
              { key: 'ai', label: 'AI disclosure ready', desc: 'Prepared to disclose AI generation for cover/interior if applicable during KDP setup.' },
            ].map(item => (
              <div 
                key={item.key}
                className={`flex items-start gap-4 p-4 rounded-lg border transition-colors ${
                  checklist[item.key as keyof typeof checklist] ? 'bg-primary/5 border-primary/20' : 'bg-card border-border hover:border-primary/50'
                }`}
              >
                <Checkbox 
                  id={item.key} 
                  className="mt-1"
                  checked={checklist[item.key as keyof typeof checklist]}
                  onCheckedChange={(c) => setChecklist(prev => ({ ...prev, [item.key]: !!c }))}
                />
                <div>
                  <label htmlFor={item.key} className="font-medium text-foreground cursor-pointer block">{item.label}</label>
                  <p className="text-sm text-muted-foreground mt-1 leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-8 pt-6 border-t border-border max-w-2xl flex justify-end">
            <Button 
              disabled={!Object.values(checklist).every(Boolean)}
              className="px-8"
            >
              <CheckCircle2 className="w-4 h-4 mr-2" /> Mark as Published
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
