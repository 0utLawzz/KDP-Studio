import { Router, type IRouter } from "express";
import { db } from "@workspace/db";
import { booksTable, generatedFilesTable, tasksTable } from "@workspace/db";
import { eq, count, desc } from "drizzle-orm";

const router: IRouter = Router();

router.get("/stats", async (_req, res) => {
  try {
    const [allBooks, allFiles, allTasks] = await Promise.all([
      db.select().from(booksTable).orderBy(desc(booksTable.updatedAt)),
      db.select({ cnt: count() }).from(generatedFilesTable),
      db.select().from(tasksTable),
    ]);

    const byStatus = {
      draft: allBooks.filter((b) => b.status === "draft").length,
      generated: allBooks.filter((b) => b.status === "generated").length,
      published: allBooks.filter((b) => b.status === "published").length,
    };

    const tasksCount = {
      notStarted: allTasks.filter((t) => t.status === "not_started").length,
      inProgress: allTasks.filter((t) => t.status === "in_progress").length,
      done: allTasks.filter((t) => t.status === "done").length,
    };

    res.json({
      totalBooks: allBooks.length,
      byStatus,
      totalFiles: allFiles[0]?.cnt ?? 0,
      recentBooks: allBooks.slice(0, 5),
      tasksCount,
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch stats" });
  }
});

export default router;
