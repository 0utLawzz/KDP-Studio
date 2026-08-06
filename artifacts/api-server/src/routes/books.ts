import { Router, type IRouter } from "express";
import { db } from "@workspace/db";
import { booksTable, generatedFilesTable } from "@workspace/db";
import { eq, desc } from "drizzle-orm";
import { calculatePageCount, validatePageCount, KDP_SPINE_TEXT_MIN } from "../lib/pageCount.js";

const router: IRouter = Router();

// GET /books
router.get("/books", async (_req, res) => {
  try {
    const books = await db
      .select()
      .from(booksTable)
      .orderBy(desc(booksTable.createdAt));
    res.json(books);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch books" });
  }
});

// POST /books
router.post("/books", async (req, res) => {
  try {
    const {
      title,
      subtitle,
      niche,
      targetAudience,
      bookType = "default",
      colorPalette = "lavender_mint",
      trimSize = "6x9",
      dayCount = 60,
      interiorType = "full_color",
      authorName = "Bright Mindful Pages",
      category,
      templateKey,
      includeHabitTracker = true,
      includeWeeklyReview = true,
      notes,
    } = req.body;

    if (!title || !niche) {
      res.status(400).json({ error: "title and niche are required" });
      return;
    }

    const [book] = await db
      .insert(booksTable)
      .values({
        title,
        subtitle,
        niche,
        targetAudience,
        bookType,
        colorPalette,
        trimSize,
        dayCount,
        interiorType,
        authorName,
        category,
        templateKey,
        includeHabitTracker,
        includeWeeklyReview,
        notes,
      })
      .returning();

    res.status(201).json(book);
  } catch (err) {
    res.status(500).json({ error: "Failed to create book" });
  }
});

// POST /books/validate — must be before /books/:id
router.post("/books/validate", (req, res) => {
  try {
    const {
      bookType = "default",
      dayCount = 60,
      interiorType = "full_color",
      includeHabitTracker = true,
      includeWeeklyReview = true,
    } = req.body;

    const pageCount = calculatePageCount({ bookType, dayCount, includeHabitTracker, includeWeeklyReview });
    const { valid, minimum, warnings } = validatePageCount(pageCount, interiorType);
    const spineTextAllowed = pageCount >= KDP_SPINE_TEXT_MIN;

    // Suggest minimum day count to meet requirements if invalid
    let suggestedDayCount: number | null = null;
    if (!valid) {
      for (let d = dayCount; d <= 365; d++) {
        const pc = calculatePageCount({ bookType, dayCount: d, includeHabitTracker, includeWeeklyReview });
        if (pc >= minimum) {
          suggestedDayCount = d;
          break;
        }
      }
    }

    res.json({ valid, pageCount, minimum, spineTextAllowed, warnings, suggestedDayCount });
  } catch (err) {
    res.status(500).json({ error: "Validation failed" });
  }
});

// GET /books/:id
router.get("/books/:id", async (req, res) => {
  try {
    const id = Number(req.params.id);
    const [book] = await db.select().from(booksTable).where(eq(booksTable.id, id));
    if (!book) {
      res.status(404).json({ error: "Book not found" });
      return;
    }
    res.json(book);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch book" });
  }
});

// PATCH /books/:id
router.patch("/books/:id", async (req, res) => {
  try {
    const id = Number(req.params.id);
    const [existing] = await db.select().from(booksTable).where(eq(booksTable.id, id));
    if (!existing) {
      res.status(404).json({ error: "Book not found" });
      return;
    }

    const allowed = [
      "title", "subtitle", "niche", "targetAudience", "bookType", "colorPalette",
      "trimSize", "dayCount", "interiorType", "authorName", "category", "templateKey",
      "includeHabitTracker", "includeWeeklyReview", "status", "generationProgress",
      "publishedAt", "notes",
    ] as const;
    const updates: Record<string, unknown> = {};
    for (const key of allowed) {
      if (key in req.body) updates[key] = req.body[key];
    }

    const [book] = await db
      .update(booksTable)
      .set({
        ...updates,
        ...(updates.status === "published" && !("publishedAt" in updates)
          ? { publishedAt: new Date(), generationProgress: 100 }
          : {}),
        updatedAt: new Date(),
      })
      .where(eq(booksTable.id, id))
      .returning();

    res.json(book);
  } catch (err) {
    res.status(500).json({ error: "Failed to update book" });
  }
});

// DELETE /books/:id
router.delete("/books/:id", async (req, res) => {
  try {
    const id = Number(req.params.id);
    const [existing] = await db.select().from(booksTable).where(eq(booksTable.id, id));
    if (!existing) {
      res.status(404).json({ error: "Book not found" });
      return;
    }
    await db.delete(booksTable).where(eq(booksTable.id, id));
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: "Failed to delete book" });
  }
});

// GET /books/:id/page-count
router.get("/books/:id/page-count", async (req, res) => {
  try {
    const id = Number(req.params.id);
    const [book] = await db.select().from(booksTable).where(eq(booksTable.id, id));
    if (!book) {
      res.status(404).json({ error: "Book not found" });
      return;
    }

    const pageCount = calculatePageCount({
      bookType: book.bookType,
      dayCount: book.dayCount,
      includeHabitTracker: book.includeHabitTracker,
      includeWeeklyReview: book.includeWeeklyReview,
    });
    const minimum = book.interiorType === "full_color" ? 72 : 24;
    const spineTextAllowed = pageCount >= KDP_SPINE_TEXT_MIN;
    const meetsMinimum = pageCount >= minimum;

    res.json({ pageCount, minimum, spineTextAllowed, meetsMinimum });
  } catch (err) {
    res.status(500).json({ error: "Failed to compute page count" });
  }
});

// GET /books/:id/files
router.get("/books/:id/files", async (req, res) => {
  try {
    const id = Number(req.params.id);
    const [book] = await db.select().from(booksTable).where(eq(booksTable.id, id));
    if (!book) {
      res.status(404).json({ error: "Book not found" });
      return;
    }

    const files = await db
      .select()
      .from(generatedFilesTable)
      .where(eq(generatedFilesTable.bookId, id))
      .orderBy(desc(generatedFilesTable.createdAt));

    res.json(files);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch files" });
  }
});

export default router;
