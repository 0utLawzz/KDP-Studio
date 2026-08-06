import { pgTable, serial, text, boolean, integer, timestamp, real } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const booksTable = pgTable("books", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  subtitle: text("subtitle"),
  niche: text("niche").notNull(),
  targetAudience: text("target_audience"),
  bookType: text("book_type").notNull().default("default"), // default | sobriety | chronic_pain
  colorPalette: text("color_palette").notNull().default("lavender_mint"),
  trimSize: text("trim_size").notNull().default("6x9"),
  dayCount: integer("day_count").notNull().default(60),
  interiorType: text("interior_type").notNull().default("full_color"), // full_color | black_white
  authorName: text("author_name").notNull().default("Bright Mindful Pages"),
  category: text("category"),
  templateKey: text("template_key"),
  includeHabitTracker: boolean("include_habit_tracker").notNull().default(true),
  includeWeeklyReview: boolean("include_weekly_review").notNull().default(true),
  status: text("status").notNull().default("planned"), // planned | in_progress | generated | published | legacy draft
  generationProgress: integer("generation_progress").notNull().default(0),
  publishedAt: timestamp("published_at", { withTimezone: true }),
  lastPageCount: integer("last_page_count"),
  notes: text("notes"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow().$onUpdate(() => new Date()),
});

export const insertBookSchema = createInsertSchema(booksTable).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertBook = z.infer<typeof insertBookSchema>;
export type Book = typeof booksTable.$inferSelect;

export const generatedFilesTable = pgTable("generated_files", {
  id: serial("id").primaryKey(),
  bookId: integer("book_id").notNull().references(() => booksTable.id, { onDelete: "cascade" }),
  fileType: text("file_type").notNull(), // interior | cover | listing | template
  fileName: text("file_name").notNull(),
  filePath: text("file_path").notNull(),
  pageCount: integer("page_count"),
  spineInches: real("spine_inches"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const insertGeneratedFileSchema = createInsertSchema(generatedFilesTable).omit({ id: true, createdAt: true });
export type InsertGeneratedFile = z.infer<typeof insertGeneratedFileSchema>;
export type GeneratedFile = typeof generatedFilesTable.$inferSelect;

export const tasksTable = pgTable("tasks", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  category: text("category"),
  status: text("status").notNull().default("not_started"), // not_started | in_progress | done
  notes: text("notes"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow().$onUpdate(() => new Date()),
});

export const insertTaskSchema = createInsertSchema(tasksTable).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertTask = z.infer<typeof insertTaskSchema>;
export type Task = typeof tasksTable.$inferSelect;
