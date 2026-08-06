import { Router, type IRouter } from "express";
import { db } from "@workspace/db";
import { tasksTable } from "@workspace/db";
import { eq, desc } from "drizzle-orm";

const router: IRouter = Router();

// GET /tasks
router.get("/tasks", async (_req, res) => {
  try {
    const tasks = await db
      .select()
      .from(tasksTable)
      .orderBy(desc(tasksTable.updatedAt));
    res.json(tasks);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch tasks" });
  }
});

// POST /tasks
router.post("/tasks", async (req, res) => {
  try {
    const { title, category, status = "not_started", notes } = req.body;
    if (!title) {
      res.status(400).json({ error: "title is required" });
      return;
    }

    const [task] = await db
      .insert(tasksTable)
      .values({ title, category, status, notes })
      .returning();

    res.status(201).json(task);
  } catch (err) {
    res.status(500).json({ error: "Failed to create task" });
  }
});

// PATCH /tasks/:id
router.patch("/tasks/:id", async (req, res) => {
  try {
    const id = Number(req.params.id);
    const [existing] = await db.select().from(tasksTable).where(eq(tasksTable.id, id));
    if (!existing) {
      res.status(404).json({ error: "Task not found" });
      return;
    }

    const allowed = ["title", "category", "status", "notes"] as const;
    const updates: Record<string, unknown> = {};
    for (const key of allowed) {
      if (key in req.body) updates[key] = req.body[key];
    }

    const [task] = await db
      .update(tasksTable)
      .set({ ...updates, updatedAt: new Date() })
      .where(eq(tasksTable.id, id))
      .returning();

    res.json(task);
  } catch (err) {
    res.status(500).json({ error: "Failed to update task" });
  }
});

// DELETE /tasks/:id
router.delete("/tasks/:id", async (req, res) => {
  try {
    const id = Number(req.params.id);
    const [existing] = await db.select().from(tasksTable).where(eq(tasksTable.id, id));
    if (!existing) {
      res.status(404).json({ error: "Task not found" });
      return;
    }
    await db.delete(tasksTable).where(eq(tasksTable.id, id));
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: "Failed to delete task" });
  }
});

export default router;
