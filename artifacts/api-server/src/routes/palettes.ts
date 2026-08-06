import { Router, type IRouter } from "express";

const router: IRouter = Router();

// KDP-proven palettes from generate_book.py and generate_cover.py
const PALETTES = [
  {
    key: "lavender_mint",
    name: "Lavender Mint",
    primary: "#C9B8E8",
    secondary: "#A8D8C8",
    accent: "#E8D5F0",
    highlight: "#F5F0FF",
    text: "#4A4A6A",
    headerText: "#FFFFFF",
  },
  {
    key: "sage_teal",
    name: "Sage Teal",
    primary: "#7BA08C",
    secondary: "#5B8FA8",
    accent: "#A8C5B5",
    highlight: "#F0F7F4",
    text: "#2D4A3E",
    headerText: "#FFFFFF",
  },
  {
    key: "rose_gold",
    name: "Rose Gold",
    primary: "#C4847A",
    secondary: "#D4A8A0",
    accent: "#F0D0CC",
    highlight: "#FDF5F4",
    text: "#5A2D2D",
    headerText: "#FFFFFF",
  },
  {
    key: "ocean_breeze",
    name: "Ocean Breeze",
    primary: "#6B9DC2",
    secondary: "#89C4D4",
    accent: "#B8DDE8",
    highlight: "#F0F8FF",
    text: "#1A3D5C",
    headerText: "#FFFFFF",
  },
  {
    key: "sunset_peach",
    name: "Sunset Peach",
    primary: "#E8956D",
    secondary: "#F4B896",
    accent: "#FAD5B8",
    highlight: "#FFF5EE",
    text: "#6B3020",
    headerText: "#FFFFFF",
  },
  {
    key: "forest_fern",
    name: "Forest Fern",
    primary: "#5B8C5A",
    secondary: "#7BAF7A",
    accent: "#A8CCA8",
    highlight: "#F0F7F0",
    text: "#1F3D1F",
    headerText: "#FFFFFF",
  },
  {
    key: "dusty_plum",
    name: "Dusty Plum",
    primary: "#8B6B8B",
    secondary: "#A88BA8",
    accent: "#C8A8C8",
    highlight: "#F5EEF5",
    text: "#3D1F3D",
    headerText: "#FFFFFF",
  },
  {
    key: "golden_hour",
    name: "Golden Hour",
    primary: "#D4A843",
    secondary: "#E8C878",
    accent: "#F5E0A0",
    highlight: "#FFFBF0",
    text: "#5A3C00",
    headerText: "#FFFFFF",
  },
  {
    key: "arctic_blue",
    name: "Arctic Blue",
    primary: "#7098B8",
    secondary: "#90B8D8",
    accent: "#B8D5E8",
    highlight: "#F0F5FF",
    text: "#1A2D4A",
    headerText: "#FFFFFF",
  },
  {
    key: "terracotta",
    name: "Terracotta",
    primary: "#C4714A",
    secondary: "#D89070",
    accent: "#EBB898",
    highlight: "#FDF2EC",
    text: "#5C2010",
    headerText: "#FFFFFF",
  },
  {
    key: "mint_chocolate",
    name: "Mint Chocolate",
    primary: "#6BAA8C",
    secondary: "#8B5A3C",
    accent: "#A8D5C0",
    highlight: "#F0FFF8",
    text: "#1C3D2D",
    headerText: "#FFFFFF",
  },
  {
    key: "bright_momentum",
    name: "Bright Momentum",
    primary: "#275DA8",
    secondary: "#2FA594",
    accent: "#FFD45C",
    highlight: "#F8FFF8",
    text: "#173B45",
    headerText: "#FFFFFF",
  },
];

router.get("/palettes", (_req, res) => {
  res.json(PALETTES);
});

export default router;
export { PALETTES };
