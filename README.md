# Soverai — Lancer (The Old Guild / Nômade) 8-Frame Isometric Sprites

Hi-bit isometric pixel art character sprites and **8-frame animation sheets** (**Breathing Idle**, **Pose-Guided Walk**, and **Pose-Guided Run** across `SE`, `SW`, `NW`, and `NE`) for the Male and Female **Lancers** (*A Velha Guilda*), designed without weapons for modular equipment and *Archeotek* / *Vharenn* effect layering.

## Interactive Browser Previewer

- **GitHub Pages (Live):** https://caio-bress.github.io/soverai-lancer-sprites/
- **Local / Offline:** Open [`index.html`](./index.html) or [`lancer_isometric_previewer.html`](./lancer_isometric_previewer.html) directly in any desktop browser — all 4 transparent 3×8 sprite sheets are embedded inside the HTML file.

---

## 3×8 Master Transparent Sprite Sheets (`1536×912` — `192×304` per cell)

- **Row 0 (8 frames — Breathing Idle):** Smooth sinusoidal ribcage expansion & rise with feet locked to the isometric tile, 1-frame secondary head/sash follow-through, and pulsing cyan/blue *Archeotek* glow.
- **Row 1 (8 frames — Walk Cycle):** Complete alternating 2-step gait (`L-Contact → L-Down → L-Passing → L-Up → R-Contact → R-Down → R-Passing → R-Up`).
- **Row 2 (8 frames — Running Cycle):** Dynamic forward-leaning sprint with deep cushion squats (`F2`, `F6`), dual airborne flight bounds (`F4`, `F8`), and streaming sashes.

| Master Sheet | Direction | Preview |
| :--- | :--- | :--- |
| [`sprites/male_lancer_isometric_se_full_sheet.png`](./sprites/male_lancer_isometric_se_full_sheet.png) | `SE` (flip for `SW`) | Male Lancer front-diagonal 3×8 |
| [`sprites/male_lancer_isometric_nw_full_sheet.png`](./sprites/male_lancer_isometric_nw_full_sheet.png) | `NW` (flip for `NE`) | Male Lancer rear-diagonal 3×8 |
| [`sprites/female_lancer_isometric_se_full_sheet.png`](./sprites/female_lancer_isometric_se_full_sheet.png) | `SE` (flip for `SW`) | Female Lancer front-diagonal 3×8 |
| [`sprites/female_lancer_isometric_nw_full_sheet.png`](./sprites/female_lancer_isometric_nw_full_sheet.png) | `NW` (flip for `NE`) | Female Lancer rear-diagonal 3×8 |

### Individual Sliced & Stabilized Frames (`24` frames per direction × `4` = `96` PNGs)
- `sprites/male_lancer/se/` & `sprites/male_lancer/nw/` (`idle_0..7.png`, `walk_0..7.png`, `run_0..7.png`)
- `sprites/female_lancer/se/` & `sprites/female_lancer/nw/` (`idle_0..7.png`, `walk_0..7.png`, `run_0..7.png`)
