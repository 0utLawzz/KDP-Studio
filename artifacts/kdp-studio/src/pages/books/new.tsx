import { useState } from "react";
import { Link, useLocation } from "wouter";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { 
  useCreateBook, 
  useValidateBook, 
  useGenerateInterior, 
  useGenerateCover, 
  useGenerateListing, 
  useGenerateTemplate,
  useListPalettes 
} from "@workspace/api-client-react";
import { Check, ChevronRight, AlertTriangle, Loader2, Download, ArrowRight, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  title: z.string().min(1, "Title is required"),
  subtitle: z.string().optional(),
  niche: z.string().min(1, "Niche is required"),
  targetAudience: z.string().optional(),
  bookType: z.enum(["default", "sobriety", "chronic_pain"]),
  colorPalette: z.string().min(1, "Palette is required"),
  trimSize: z.enum(["6x9", "5x8", "8.5x11"]),
  dayCount: z.coerce.number().min(1).max(365),
  interiorType: z.enum(["full_color", "black_white"]),
  authorName: z.string().min(1, "Author name is required"),
  includeHabitTracker: z.boolean().default(false),
  includeWeeklyReview: z.boolean().default(false),
});

type FormValues = z.infer<typeof formSchema>;

export function NewBook() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [bookId, setBookId] = useState<number | null>(null);
  
  const { data: palettes } = useListPalettes();
  const createBook = useCreateBook();
  const validateBook = useValidateBook();
  const generateInterior = useGenerateInterior();
  const generateCover = useGenerateCover();
  const generateListing = useGenerateListing();
  const generateTemplate = useGenerateTemplate();

  const [validationData, setValidationData] = useState<any>(null);
  const [generationStates, setGenerationStates] = useState<Record<string, 'idle'|'loading'|'success'|'error'>>({
    interior: 'idle', cover: 'idle', listing: 'idle', template: 'idle'
  });

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      subtitle: "",
      niche: "",
      targetAudience: "",
      bookType: "default",
      colorPalette: "sage_calm",
      trimSize: "6x9",
      dayCount: 90,
      interiorType: "black_white",
      authorName: "Bright Mindful Pages",
      includeHabitTracker: false,
      includeWeeklyReview: false,
    },
  });

  const onConfigureSubmit = async (values: FormValues) => {
    try {
      // Validate first before creating
      const validation = await validateBook.mutateAsync({
        data: {
          bookType: values.bookType,
          dayCount: values.dayCount,
          interiorType: values.interiorType,
          includeHabitTracker: values.includeHabitTracker,
          includeWeeklyReview: values.includeWeeklyReview
        }
      });
      
      setValidationData(validation);
      setStep(2);
    } catch (err) {
      toast({ title: "Validation failed", variant: "destructive" });
    }
  };

  const handleCreateAndProceed = async () => {
    try {
      const values = form.getValues();
      const newBook = await createBook.mutateAsync({ data: values as any });
      setBookId(newBook.id);
      setStep(3);
    } catch (err) {
      toast({ title: "Failed to create book record", variant: "destructive" });
    }
  };

  const handleGenerate = async (type: 'interior' | 'cover' | 'listing' | 'template') => {
    if (!bookId) return;
    
    setGenerationStates(prev => ({ ...prev, [type]: 'loading' }));
    try {
      const fns = {
        interior: generateInterior,
        cover: generateCover,
        listing: generateListing,
        template: generateTemplate
      };
      
      await fns[type].mutateAsync({ id: bookId });
      setGenerationStates(prev => ({ ...prev, [type]: 'success' }));
      toast({ title: `Generated ${type} successfully.` });
    } catch (err) {
      setGenerationStates(prev => ({ ...prev, [type]: 'error' }));
      toast({ title: `Failed to generate ${type}`, variant: "destructive" });
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500 pb-24">
      <div className="mb-8">
        <h1 className="text-3xl font-serif text-foreground">New Publication</h1>
        <p className="text-muted-foreground mt-1">Configure and generate a new KDP asset.</p>
      </div>

      {/* Stepper */}
      <div className="flex items-center justify-between mb-8 relative">
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-0.5 bg-muted -z-10 rounded"></div>
        {[
          { num: 1, label: "Configure" },
          { num: 2, label: "Validate" },
          { num: 3, label: "Generate" }
        ].map((s) => (
          <div key={s.num} className="flex flex-col items-center gap-2 bg-background px-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-colors ${
              step === s.num ? "bg-primary text-primary-foreground ring-4 ring-primary/20" :
              step > s.num ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
            }`}>
              {step > s.num ? <Check className="w-4 h-4" /> : s.num}
            </div>
            <span className={`text-xs font-medium uppercase tracking-wider ${step === s.num ? "text-foreground" : "text-muted-foreground"}`}>
              {s.label}
            </span>
          </div>
        ))}
      </div>

      {/* Step 1: Configure */}
      {step === 1 && (
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onConfigureSubmit)} className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              
              <div className="space-y-6">
                <div className="space-y-4">
                  <h3 className="font-serif text-xl border-b border-border pb-2">Core Identity</h3>
                  <FormField control={form.control} name="title" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Book Title</FormLabel>
                      <FormControl><Input {...field} placeholder="e.g. 90-Day Mindful Journal" /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="subtitle" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Subtitle (Optional)</FormLabel>
                      <FormControl><Input {...field} placeholder="e.g. A daily path to clarity" /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <div className="grid grid-cols-2 gap-4">
                    <FormField control={form.control} name="niche" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Niche</FormLabel>
                        <FormControl><Input {...field} placeholder="e.g. Wellness" /></FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="authorName" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Author Name</FormLabel>
                        <FormControl><Input {...field} /></FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-serif text-xl border-b border-border pb-2">Design & Format</h3>
                  <FormField control={form.control} name="colorPalette" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Color Palette</FormLabel>
                      <div className="grid grid-cols-2 gap-3 mt-2">
                        {palettes?.map(palette => (
                          <div 
                            key={palette.key}
                            onClick={() => field.onChange(palette.key)}
                            className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center gap-3 ${
                              field.value === palette.key ? "border-primary bg-primary/5 ring-1 ring-primary" : "border-border hover:border-primary/50"
                            }`}
                          >
                            <div className="flex -space-x-1 shrink-0">
                              <div className="w-5 h-5 rounded-full shadow-sm" style={{ backgroundColor: palette.primary }}></div>
                              <div className="w-5 h-5 rounded-full shadow-sm" style={{ backgroundColor: palette.secondary }}></div>
                              <div className="w-5 h-5 rounded-full shadow-sm" style={{ backgroundColor: palette.accent }}></div>
                            </div>
                            <span className="text-xs font-medium truncate">{palette.name}</span>
                          </div>
                        ))}
                      </div>
                      <FormMessage />
                    </FormItem>
                  )} />

                  <div className="grid grid-cols-2 gap-4">
                    <FormField control={form.control} name="trimSize" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Trim Size</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl><SelectTrigger><SelectValue placeholder="Select size" /></SelectTrigger></FormControl>
                          <SelectContent>
                            <SelectItem value="6x9">6 x 9 in</SelectItem>
                            <SelectItem value="5x8">5 x 8 in</SelectItem>
                            <SelectItem value="8.5x11">8.5 x 11 in</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="interiorType" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Interior Print</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl><SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger></FormControl>
                          <SelectContent>
                            <SelectItem value="black_white">Black & White</SelectItem>
                            <SelectItem value="full_color">Full Color</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )} />
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="space-y-4">
                  <h3 className="font-serif text-xl border-b border-border pb-2">Content Configuration</h3>
                  
                  <FormField control={form.control} name="bookType" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Book Type / Layout</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl><SelectTrigger><SelectValue placeholder="Select layout type" /></SelectTrigger></FormControl>
                        <SelectContent>
                          <SelectItem value="default">Standard Journal</SelectItem>
                          <SelectItem value="sobriety">Sobriety Tracker</SelectItem>
                          <SelectItem value="chronic_pain">Chronic Pain Tracker</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormDescription>Determines the daily page structure.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )} />

                  <FormField control={form.control} name="dayCount" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Day Count</FormLabel>
                      <FormControl><Input type="number" {...field} /></FormControl>
                      <FormDescription>How many daily pages to generate.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )} />

                  <div className="space-y-3 bg-muted/30 p-4 rounded-lg border border-border">
                    <FormField control={form.control} name="includeHabitTracker" render={({ field }) => (
                      <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                          <FormLabel className="cursor-pointer">Include Habit Tracker pages</FormLabel>
                          <FormDescription className="text-xs">Adds 30-day visual trackers at the beginning.</FormDescription>
                        </div>
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="includeWeeklyReview" render={({ field }) => (
                      <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                          <FormLabel className="cursor-pointer">Include Weekly Reviews</FormLabel>
                          <FormDescription className="text-xs">Adds a review page after every 7 daily pages.</FormDescription>
                        </div>
                      </FormItem>
                    )} />
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-6 border-t border-border">
              <Button type="submit" size="lg" className="px-8" disabled={validateBook.isPending}>
                {validateBook.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Validate Configuration <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </form>
        </Form>
      )}

      {/* Step 2: Validate */}
      {step === 2 && validationData && (
        <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
          <div className="bg-card border border-border rounded-xl p-8 max-w-2xl mx-auto shadow-sm">
            <div className="flex items-center gap-4 mb-6">
              <div className={`p-3 rounded-full ${validationData.valid ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-destructive/10 text-destructive'}`}>
                {validationData.valid ? <Check className="w-8 h-8" /> : <AlertTriangle className="w-8 h-8" />}
              </div>
              <div>
                <h3 className="text-2xl font-serif">{validationData.valid ? "Configuration Valid" : "Issues Detected"}</h3>
                <p className="text-muted-foreground">{validationData.valid ? "Ready for generation." : "Please fix the warnings below."}</p>
              </div>
            </div>

            <div className="space-y-4 mb-8">
              <div className="grid grid-cols-2 gap-4 border-t border-b border-border py-4">
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Calculated Pages</div>
                  <div className="text-2xl font-serif">{validationData.pageCount}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground mb-1">KDP Minimum</div>
                  <div className="text-2xl font-serif">{validationData.minimum}</div>
                </div>
                <div className="col-span-2">
                  <div className="text-sm text-muted-foreground mb-1">Spine Text Status</div>
                  <div className="font-medium text-foreground">
                    {validationData.spineTextAllowed 
                      ? "Allowed (Over 79 pages)" 
                      : "Not Allowed (Under 79 pages) - Cover will be generated without spine text."}
                  </div>
                </div>
              </div>

              {validationData.warnings.length > 0 && (
                <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-900 rounded-lg p-4">
                  <h4 className="text-sm font-bold text-yellow-800 dark:text-yellow-500 mb-2 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Warnings
                  </h4>
                  <ul className="text-sm text-yellow-700 dark:text-yellow-400 list-disc pl-5 space-y-1">
                    {validationData.warnings.map((w: string, i: number) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                  {validationData.suggestedDayCount && (
                    <div className="mt-3 pt-3 border-t border-yellow-200/50">
                      <p className="text-sm font-medium">Suggestion: Change day count to {validationData.suggestedDayCount} to reach the minimum.</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="flex gap-4 justify-between">
              <Button variant="outline" onClick={() => setStep(1)} disabled={createBook.isPending}>
                <ArrowLeft className="w-4 h-4 mr-2" /> Back to Edit
              </Button>
              <Button onClick={handleCreateAndProceed} disabled={!validationData.valid || createBook.isPending}>
                {createBook.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Confirm & Proceed <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Generate */}
      {step === 3 && bookId && (
        <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <Card className="border-border">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-serif text-lg">Interior PDF</h3>
                    <p className="text-sm text-muted-foreground">The inner pages of the book.</p>
                  </div>
                </div>
                <Button 
                  onClick={() => handleGenerate('interior')} 
                  disabled={generationStates.interior === 'loading' || generationStates.interior === 'success'}
                  className="w-full"
                  variant={generationStates.interior === 'success' ? "secondary" : "default"}
                >
                  {generationStates.interior === 'loading' ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...</> : 
                   generationStates.interior === 'success' ? <><Check className="w-4 h-4 mr-2" /> Generated</> : "Generate PDF"}
                </Button>
              </CardContent>
            </Card>

            <Card className="border-border">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-serif text-lg">Full-wrap Cover PDF</h3>
                    <p className="text-sm text-muted-foreground">Calculated with exact spine width.</p>
                  </div>
                </div>
                <Button 
                  onClick={() => handleGenerate('cover')} 
                  disabled={generationStates.cover === 'loading' || generationStates.cover === 'success' || generationStates.interior !== 'success'} // require interior first for exact page count
                  className="w-full"
                  variant={generationStates.cover === 'success' ? "secondary" : "default"}
                >
                  {generationStates.cover === 'loading' ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...</> : 
                   generationStates.cover === 'success' ? <><Check className="w-4 h-4 mr-2" /> Generated</> : "Generate Cover"}
                </Button>
                {generationStates.interior !== 'success' && <p className="text-xs text-center mt-2 text-muted-foreground">Generate interior first.</p>}
              </CardContent>
            </Card>

            <Card className="border-border">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-serif text-lg">Listing Metadata</h3>
                    <p className="text-sm text-muted-foreground">Optimized title, description, keywords.</p>
                  </div>
                </div>
                <Button 
                  onClick={() => handleGenerate('listing')} 
                  disabled={generationStates.listing === 'loading' || generationStates.listing === 'success'}
                  className="w-full"
                  variant={generationStates.listing === 'success' ? "secondary" : "default"}
                >
                  {generationStates.listing === 'loading' ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...</> : 
                   generationStates.listing === 'success' ? <><Check className="w-4 h-4 mr-2" /> Generated</> : "Generate Metadata"}
                </Button>
              </CardContent>
            </Card>

            <Card className="border-border bg-muted/20">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-serif text-lg">Editable Templates</h3>
                    <p className="text-sm text-muted-foreground">Zip file for external design tweaks.</p>
                  </div>
                </div>
                <Button 
                  onClick={() => handleGenerate('template')} 
                  disabled={generationStates.template === 'loading' || generationStates.template === 'success'}
                  className="w-full"
                  variant={generationStates.template === 'success' ? "secondary" : "outline"}
                >
                  {generationStates.template === 'loading' ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Packaging...</> : 
                   generationStates.template === 'success' ? <><Check className="w-4 h-4 mr-2" /> Packaged</> : "Generate Template ZIP"}
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-center mt-12 border-t border-border pt-8">
            <Button size="lg" onClick={() => setLocation(`/books/${bookId}`)}>
              Go to Book Details <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
