import { Router, type IRouter } from "express";
import { db } from "@workspace/db";
import { generatedFilesTable } from "@workspace/db";
import { eq } from "drizzle-orm";
import fs from "fs";
import path from "path";

const router: IRouter = Router();

// GET /files/:fileId/download
router.get("/files/:fileId/download", async (req, res) => {
  try {
    const fileId = Number(req.params.fileId);
    const [file] = await db
      .select()
      .from(generatedFilesTable)
      .where(eq(generatedFilesTable.id, fileId));

    if (!file) return res.status(404).json({ error: "File not found" });

    if (!fs.existsSync(file.filePath)) {
      return res.status(404).json({ error: "File does not exist on disk" });
    }

    const ext = path.extname(file.fileName).toLowerCase();
    const contentType =
      ext === ".pdf" ? "application/pdf" :
      ext === ".zip" ? "application/zip" :
      ext === ".json" ? "application/json" :
      "application/octet-stream";

    res.setHeader("Content-Type", contentType);
    res.setHeader("Content-Disposition", `attachment; filename="${file.fileName}"`);
    fs.createReadStream(file.filePath).pipe(res);
  } catch (err) {
    res.status(500).json({ error: "Failed to download file" });
  }
});

export default router;
