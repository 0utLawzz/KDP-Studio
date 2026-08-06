import { Router, type IRouter } from "express";
import healthRouter from "./health";
import booksRouter from "./books";
import filesRouter from "./files";
import generateRouter from "./generate";
import palettesRouter from "./palettes";
import statsRouter from "./stats";
import tasksRouter from "./tasks";

const router: IRouter = Router();

router.use(healthRouter);
router.use(booksRouter);
router.use(filesRouter);
router.use(generateRouter);
router.use(palettesRouter);
router.use(statsRouter);
router.use(tasksRouter);

export default router;
