import { Router, type IRouter } from "express";
import { db } from "@workspace/db";
import { booksTable, generatedFilesTable } from "@workspace/db";
import { eq } from "drizzle-orm";
import { calculatePageCount } from "../lib/pageCount.js";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const router: IRouter = Router();

// After esbuild bundles all routes into dist/index.mjs, import.meta.dirname
// is always <artifact-root>/dist — so ../python is stable in dev and prod.
const PYTHON_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../python");
const OUTPUT_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../generated_files");

fs.mkdirSync(OUTPUT_DIR, { recursive: true });

/** Run a Python script and return its parsed JSON stdout. */
function runPython(scriptPath: string, args: string[]): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const proc = spawn("python3", [scriptPath, ...args]);
    let stdout = "";
    let stderr = "";
    const timer = setTimeout(() => {
      proc.kill();
      reject(new Error("Python process timed out after 120 seconds"));
    }, 120_000);

    proc.stdout.on("data", (chunk: Buffer) => { stdout += chunk.toString(); });
    proc.stderr.on("data", (chunk: Buffer) => { stderr += chunk.toString(); });
    proc.on("close", (code) => {
      clearTimeout(timer);
      if (code !== 0) {
        reject(new Error(`Python exited ${code}: ${stderr.trim() || stdout.trim()}`));
        return;
      }
      try {
        resolve(JSON.parse(stdout.trim()));
      } catch {
        reject(new Error(`Failed to parse Python output: ${stdout.trim()}`));
      }
    });
    proc.on("error", (err) => {
      clearTimeout(timer);
      reject(err);
    });
  });
}

// POST /books/:id/generate-interior
router.post("/books/:id/generate-interior", async (req, res) => {
  try {
    const id = Number(req.params.id);
    const [book] = await db.select().from(booksTable).where(eq(booksTable.id, id));
    if (!book) {
      res.status(404).json({ error: "Book not found" });
      return;
    }

    const fileName = `interior_${id}_${Date.now()}.pdf`;
    const outputPath = path.join(OUTPUT_DIR, fileName);

    const args = [
      "--output", outputPath,
      "--title", book.title,
      "--author-name", book.authorName,
      "--book-type", book.bookType,
      "--color-palette", book.colorPalette,
      "--trim-size", book.trimSize,
      "--day-count", String(book.dayCount),
      "--interior-type", book.interiorType,
      ...(book.includeHabitTracker ? [] : ["--no-habit-tracker"]),
      ...(book.includeWeeklyReview ? [] : ["--no-weekly-review"]),
    ];

    const result = await runPython(path.join(PYTHON_DIR, "generate_interior.py"), args) as { page_count: number };
    const pageCount = result.page_count;

    const [file] = await db.insert(generatedFilesTable).values({
      bookId: id,
      fileType: "interior",
      fileName,
      filePath: outputPath,
      pageCount,
    }).returning();

    await db.update(booksTable)
      .set({ status: "in_progress", generationProgress: 25, lastPageCount: pageCount, updatedAt: new Date() })
      .where(eq(booksTable.id, id));

    res.json({ success: true, file, pageCount });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Failed to generate interior";
    res.status(500).json({ error: message });
  }
});

// POST /books/:id/generate-cover
router.post("/books/:id/generate-cover", async (req, res) => {
  try {
    const id = Number(req.params.id);
    const [book] = await db.select().from(booksTable).where(eq(booksTable.id, id));
    if (!book) {
      res.status(404).json({ error: "Book not found" });
      return;
    }

    const pageCount = book.lastPageCount ?? calculatePageCount({
      bookType: book.bookType,
      dayCount: book.dayCount,
      includeHabitTracker: book.includeHabitTracker,
      includeWeeklyReview: book.includeWeeklyReview,
    });

    const fileName = `cover_${id}_${Date.now()}.pdf`;
    const outputPath = path.join(OUTPUT_DIR, fileName);

    const args = [
      "--output", outputPath,
      "--title", book.title,
      "--author-name", book.authorName,
      "--color-palette", book.colorPalette,
      "--trim-size", book.trimSize,
      "--page-count", String(pageCount),
      "--day-count", String(book.dayCount),
      ...(book.subtitle ? ["--subtitle", book.subtitle] : []),
    ];

    const result = await runPython(path.join(PYTHON_DIR, "generate_cover.py"), args) as { spine_inches: number };

    const [file] = await db.insert(generatedFilesTable).values({
      bookId: id,
      fileType: "cover",
      fileName,
      filePath: outputPath,
      pageCount,
      spineInches: result.spine_inches,
    }).returning();

    await db.update(booksTable)
      .set({ status: "in_progress", generationProgress: 50, updatedAt: new Date() })
      .where(eq(booksTable.id, id));

    res.json({ success: true, file, spineInches: result.spine_inches });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Failed to generate cover";
    res.status(500).json({ error: message });
  }
});

// POST /books/:id/generate-listing
router.post("/books/:id/generate-listing", async (req, res) => {
  try {
    const id = Number(req.params.id);
    const [book] = await db.select().from(booksTable).where(eq(booksTable.id, id));
    if (!book) {
      res.status(404).json({ error: "Book not found" });
      return;
    }

    const fileName = `listing_${id}_${Date.now()}.json`;
    const outputPath = path.join(OUTPUT_DIR, fileName);

    const args = [
      "--output", outputPath,
      "--title", book.title,
      "--niche", book.niche,
      "--author-name", book.authorName,
      "--day-count", String(book.dayCount),
      "--interior-type", book.interiorType,
      ...(book.targetAudience ? ["--target-audience", book.targetAudience] : []),
      ...(book.includeHabitTracker ? [] : ["--no-habit-tracker"]),
      ...(book.includeWeeklyReview ? [] : ["--no-weekly-review"]),
    ];

    const result = await runPython(path.join(PYTHON_DIR, "generate_listing.py"), args) as {
      title: string; subtitle: string; description: string;
      keywords: string[]; categories: string[]; suggestedPrice: string; warnings: string[];
    };

    // Save listing JSON to disk
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));

    const [file] = await db.insert(generatedFilesTable).values({
      bookId: id,
      fileType: "listing",
      fileName,
      filePath: outputPath,
    }).returning();

    await db.update(booksTable)
      .set({ status: "in_progress", generationProgress: 75, updatedAt: new Date() })
      .where(eq(booksTable.id, id));

    res.json({ success: true, file, listing: result });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Failed to generate listing";
    res.status(500).json({ error: message });
  }
});

// POST /books/:id/generate-template
router.post("/books/:id/generate-template", async (req, res) => {
  try {
    const id = Number(req.params.id);
    const [book] = await db.select().from(booksTable).where(eq(booksTable.id, id));
    if (!book) {
      res.status(404).json({ error: "Book not found" });
      return;
    }

    const pageCount = book.lastPageCount ?? calculatePageCount({
      bookType: book.bookType,
      dayCount: book.dayCount,
      includeHabitTracker: book.includeHabitTracker,
      includeWeeklyReview: book.includeWeeklyReview,
    });

    const fileName = `template_${id}_${Date.now()}.zip`;
    const outputPath = path.join(OUTPUT_DIR, fileName);

    // generate_template.py uses: topic, authorName, colorPalette, trimSize, pageCount, paperType
    const paperType = book.interiorType === "full_color" ? "premium_color" : "white";
    const config = JSON.stringify({
      topic: book.title,
      authorName: book.authorName,
      colorPalette: book.colorPalette,
      trimSize: book.trimSize,
      pageCount,
      paperType,
    });

    await runPython(path.join(PYTHON_DIR, "generate_template.py"), [config, outputPath]);

    const [file] = await db.insert(generatedFilesTable).values({
      bookId: id,
      fileType: "template",
      fileName,
      filePath: outputPath,
      pageCount,
    }).returning();

    await db.update(booksTable)
      .set({ status: "generated", generationProgress: 100, updatedAt: new Date() })
      .where(eq(booksTable.id, id));

    res.json({ success: true, file });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Failed to generate template";
    res.status(500).json({ error: message });
  }
});

export default router;
