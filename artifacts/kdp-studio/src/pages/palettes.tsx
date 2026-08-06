import { useListPalettes } from "@workspace/api-client-react";
import { Palette as PaletteIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function Palettes() {
  const { data: palettes, isLoading } = useListPalettes();

  if (isLoading) {
    return (
      <div className="p-12 text-center animate-pulse">
        <PaletteIcon className="w-8 h-8 mx-auto text-muted-foreground opacity-50 mb-4" />
        Loading brand palettes...
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-24">
      <div>
        <h1 className="text-3xl font-serif text-foreground">Brand Palettes</h1>
        <p className="text-muted-foreground mt-1">Consistent color systems for Bright Mindful Pages.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {palettes?.map((palette) => (
          <Card key={palette.key} className="overflow-hidden hover:shadow-md transition-all group border-border">
            <CardHeader className="bg-muted/20 border-b border-border pb-4">
              <div className="flex justify-between items-center">
                <CardTitle className="text-lg font-serif">{palette.name}</CardTitle>
                <span className="text-[10px] font-mono bg-background px-2 py-1 rounded border border-border text-muted-foreground">
                  {palette.key}
                </span>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              <div className="flex gap-3 mb-6">
                {[
                  { color: palette.primary, label: "Primary" },
                  { color: palette.secondary, label: "Secondary" },
                  { color: palette.accent, label: "Accent" },
                  ...(palette.highlight ? [{ color: palette.highlight, label: "Highlight" }] : []),
                ].map((swatch, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center gap-2">
                    <div 
                      className="w-full aspect-square rounded-full shadow-sm ring-1 ring-black/5 transition-transform group-hover:scale-105"
                      style={{ backgroundColor: swatch.color }}
                      title={swatch.color}
                    />
                    <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">{swatch.label}</span>
                  </div>
                ))}
              </div>
              
              <div className="space-y-2 bg-background border border-border p-4 rounded-lg">
                <div 
                  className="font-serif text-lg tracking-tight"
                  style={{ color: palette.headerText || palette.text }}
                >
                  Sample Typography
                </div>
                <div 
                  className="text-sm leading-relaxed"
                  style={{ color: palette.text }}
                >
                  This is how body text appears within the {palette.name} palette context. The aesthetic is designed to feel warm and mindful.
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
