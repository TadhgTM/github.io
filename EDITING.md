Editing Guide

Quick edits
1. Homepage text: `index.qmd`
2. Research page: `research.qmd`
3. CV page: `cv.qmd`
4. Teaching page: `teaching.qmd`
5. Code & Data: `code.qmd`
6. Blog landing: `blog.qmd`
7. Hidden policy page: `policy-applications.qmd`
8. Styling: `styles.css`

Add a working paper (paste into `research.qmd`)
```markdown
### Title of Paper  
**Your Name**

Short 2–3 sentence description.

- [Paper (PDF)](assets/papers/your_file.pdf)
- Code & replication materials (GitHub)
- Slides (coming soon)
```

Add a blog post
1. Copy `posts/_template.qmd` to a new file in `posts/`.
2. Name it like `YYYY-MM-DD-short-title.qmd`.
3. Fill in the title, date, description, and body.

Publish changes
1. `quarto render`
2. `git add docs`
3. `git commit -m "Update site"`
4. `git push`
