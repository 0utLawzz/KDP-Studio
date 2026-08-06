// Page count calculation ported from generate_book.py
// KDP minimum: 72 pages for full color, spine text at 79+ pages

interface PageCountOptions {
  bookType: string;
  dayCount: number;
  includeHabitTracker?: boolean;
  includeWeeklyReview?: boolean;
}

export function calculatePageCount(opts: PageCountOptions): number {
  const { bookType, dayCount, includeHabitTracker = true, includeWeeklyReview = true } = opts;

  // Front matter: title, copyright, intro = 4 pages
  let pages = 4;

  if (bookType === "sobriety") {
    // Sobriety tracker: daily page + mood tracker per day
    pages += dayCount * 2;
    // Weekly milestones every 7 days
    const weeklyMilestones = Math.floor(dayCount / 7);
    pages += weeklyMilestones;
  } else {
    // Default planner: daily page per day
    pages += dayCount;
    // Habit tracker pages (weekly spread, 1 per week)
    if (includeHabitTracker) {
      pages += Math.ceil(dayCount / 7);
    }
    // Weekly review pages
    if (includeWeeklyReview) {
      pages += Math.ceil(dayCount / 7);
    }
  }

  // Back matter: notes, final page = 2 pages
  pages += 2;

  return pages;
}

export const KDP_MIN_PAGES_COLOR = 72;
export const KDP_MIN_PAGES_BW = 24;
export const KDP_SPINE_TEXT_MIN = 79;
export const PAGES_PER_INCH = 110; // KDP standard: 110 pages per inch of spine

export function getSpineInches(pageCount: number): number {
  return parseFloat((pageCount / PAGES_PER_INCH).toFixed(3));
}

export function validatePageCount(
  pageCount: number,
  interiorType: string
): { valid: boolean; minimum: number; warnings: string[] } {
  const minimum = interiorType === "full_color" ? KDP_MIN_PAGES_COLOR : KDP_MIN_PAGES_BW;
  const valid = pageCount >= minimum;
  const warnings: string[] = [];

  if (!valid) {
    warnings.push(
      `Page count ${pageCount} is below the KDP minimum of ${minimum} for ${interiorType === "full_color" ? "full-color" : "black & white"} interiors.`
    );
  }

  if (pageCount >= minimum && pageCount < KDP_SPINE_TEXT_MIN) {
    warnings.push(
      `Spine text will not be printed — KDP requires at least ${KDP_SPINE_TEXT_MIN} pages. Your book has ${pageCount}.`
    );
  }

  return { valid, minimum, warnings };
}
