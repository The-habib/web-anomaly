---
name: screenshot-visual-diff
description: >-
  Take responsive screenshots and perform visual regression testing / image diffing using Playwright, Pageres, Capture-Website, BlinkDiff, Pixelmatch, or Resemble.js. Use when the user asks to take website screenshots, compare UI versions, detect visual regressions, or generate visual diff heatmaps.
---

# Screenshot & Visual Diff Skill

This skill provides patterns for capturing responsive web screenshots and performing pixel-level and perceptual visual comparisons.

## Available Tools

- **Playwright Screenshots (`playwright-screenshot`)**: Headless full-page and element screenshots.
- **Pageres CLI (`pageres`)**: Capture responsive screenshots across multiple screen resolutions in one command.
- **Capture-Website CLI (`capture-website`)**: Feature-rich webpage screenshot generator.
- **BlinkDiff (`blink-diff`)**: Perceptual image comparison tool with configurable threshold.
- **Pixelmatch (`pixelmatch`)**: Fast pixel-level image comparison tool in CLI & Node/Python.
- **Resemble.js (`resemblejs`)**: Image analysis and visual difference calculation.

## Common Workflows

### 1. Capturing Screenshots
```bash
# Playwright fast full-page screenshot
playwright-screenshot "https://example.com" "fullpage.png" --full-page

# Pageres responsive capture across mobile, tablet, and desktop
pageres "https://example.com" 375x667 768x1024 1920x1080 --crop

# Capture-website with delay and custom viewport
capture-website "https://example.com" "output.png" --width 1280 --height 800 --delay 2
```

### 2. Pixel Diffing with `pixelmatch`
```bash
# Compare two PNGs and generate a diff image highlighting changed pixels in red
pixelmatch image1.png image2.png diff.png 0.1
```

### 3. Perceptual Image Comparison with `resemblejs`
```bash
# Compare two images, get JSON metrics and visual diff buffer
resemblejs image1.png image2.png diff_output.png
```

### 4. Perceptual Diffing with `blink-diff`
```bash
blink-diff --image-a image1.png --image-b image2.png --image-output diff.png --threshold 0.05
```
