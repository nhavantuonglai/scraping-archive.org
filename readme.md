# Nhavan – Vietnamese literary research platform

## Tiếng Việt

Nhavan (v26.03.39) là một framework website tĩnh mã nguồn mở, hiệu năng cao, xây dựng trên Astro 5, vận hành cho nhavan.vn – một nền tảng nghiên cứu văn học và văn hóa đọc tiếng Việt. Codebase này trước đây có mục đích kép (đồng thời vận hành cả một cửa hàng e-commerce, blur.vn) nhưng đã được cắt gọn xuống còn một ứng dụng đơn, tập trung vào bài viết; toàn bộ code liên quan product/cart/checkout đã được gỡ bỏ.

### Tính năng chính

Configuration:

– Một file `config.yaml` duy nhất là nguồn thông tin xác thực (source of truth) cho danh tính site, SEO, và hành vi blog.

– Một Astro integration tùy chỉnh (`nhavantuonglai:tasks`) expose phần config đã parse thành một virtual module (`nhavantuonglai:config`), dùng được xuyên suốt toàn bộ codebase.

SEO & structured data:

– JSON-LD schemas: `Article`, `BlogPosting`, `Organization`, `FAQ`, `Breadcrumb`.

– Tự động tạo canonical URL không có dấu `/` ở cuối.

– Meta tag OpenGraph + Twitter Card với locale `vi_VN`.

– Quy tắc robots theo từng trang (index/noindex), loại trừ các trang phân trang.

– XML sitemap tự viết, loại trừ các trang noindex.

– Endpoint IndexNow để thông báo tức thời cho công cụ tìm kiếm.

Content library:

– Bài viết Markdown/MDX với reading time tự tính (qua Remark plugin).

– Table of Contents tự sinh từ heading của bài viết.

– Lọc theo tag/category tại `/viet/[tag]` kèm phân trang.

– Bài viết liên quan dựa trên tag chung.

– Script chống sao chép nội dung (anti-copy).

– RSS 2.0 feed kèm `media:content` image enclosures.

– Lịch sử đọc gần đây lưu trong `localStorage`.

– Author taxonomy (collection `author`): trang tiểu sử riêng với title, description, và ảnh đại diện; khi một trang tag khớp với slug tác giả, SEO metadata (title, description, hero image) tự động được ghi đè bằng dữ liệu tác giả và trang trở nên indexable (`noindex: false`).

– Writing taxonomy (frontmatter field `writing`): các bài viết thuộc cùng một tác phẩm văn học được nhóm lại trên trang lưu trữ tác giả; các nhóm được lọc theo hai cấp tag (tag tác giả + tag tác phẩm), sắp xếp theo slug (numeric-aware), và chia thành batch có thể cấu hình trên mỗi trang; tối đa hai nhóm chính và một nhóm "khác" mỗi trang, kích thước batch tỉ lệ theo `postsPerPage` trong config.

Performance & UI:

– Static Site Generation (SSG) – xuất ra HTML thuần, deploy được ở bất kỳ đâu.

– Tối ưu hình ảnh qua `unpic` với responsive layout và tích hợp Pexels CDN.

– Native lazy loading được inject qua Rehype plugin.

– Google Analytics chạy ngoài main thread qua Partytown (không ảnh hưởng LCP).

– Animation Framer Motion cho chuyển động component mượt mà.

– Hiệu ứng con trỏ tùy chỉnh + canvas comet (`viral.astro`).

– Scroll reveal dựa trên Intersection Observer (class `.reveal`).

– Chế độ Dark/Light theo tùy chọn hệ thống.

– Trang 404 với đếm ngược 5 giây tự động redirect.

Developer experience:

– TypeScript strict mode trên toàn bộ utilities và system files.

– Zod schema validation cho toàn bộ frontmatter của content collection tại build time.

– ESLint + Prettier với plugin Astro và Tailwind.

– Path alias `~` trỏ về `src/`.

– Hot reload theo dõi thay đổi của `config.yaml`.

### Tech stack

| Layer | Technology |
|---|---|
| Framework | Astro 5 (SSG, `output: 'static'`) |
| UI Components | React 18 (Astro Islands pattern) |
| Styling | Tailwind CSS v3, CSS custom properties |
| Content | Astro Content Collections (Markdown/MDX) |
| Schema Validation | Zod |
| Image Optimization | unpic |
| Animations | Framer Motion |
| Analytics | Google Analytics 4 via Partytown |
| Slugification | limax |
| Config Parsing | js-yaml |
| Fonts | Be Vietnam Pro (Google Fonts) |
| Deployment | Netlify / Vercel (static) |

### Yêu cầu hệ thống

– Node.js 22.x – [nodejs.org](https://nodejs.org).

– npm ≥ 10.x (đi kèm Node).

– VS Code (khuyến nghị) – [code.visualstudio.com](https://code.visualstudio.com).

– Extension khuyến nghị: `astro-build.astro-vscode`, `bradlc.vscode-tailwindcss`.

### Cài đặt & phát triển local

#### Clone repository

```bash
git clone https://github.com/nhavantuonglai/nhavan.vn.git
cd nhavan.vn
```

#### Cài đặt dependencies

```bash
npm install
```

#### Cấu hình site

Mở `src/config.yaml` và thiết lập danh tính site:

```yaml
site:
	name: Your Site Name
	site: "https://nhavan.vn"

apps:
	blog:
		postsPerPage: 15   # controls batch sizes on all list pages including /viet
```

#### Khởi động dev server

```bash
npm run dev
```

Site chạy tại `http://localhost:4321`. Server hot-reload khi có thay đổi file, kể cả `config.yaml`.

#### Build cho production

```bash
npm run build
```

Output tĩnh được tạo trong `dist/`. Xem thử local:

```bash
npm run preview
```

#### Các Script có sẵn

| Command | Description |
|---|---|
| `npm run dev` | Khởi động dev server tại `localhost:4321` |
| `npm run build` | Build output tĩnh vào `dist/` |
| `npm run preview` | Xem thử bản production build tại local |
| `npm run format` | Format toàn bộ file với Prettier |
| `npm run lint` | Chạy ESLint |
| `npm run typecheck` | Kiểm tra kiểu TypeScript |
| `npm run validate` | Chạy lint + typecheck cùng lúc |

### Thêm nội dung

#### Bài viết mới

Tạo `src/content/van/article-slug.md`:

```markdown
---
pubDatetime: 2025-01-01T00:00:00Z
title: Article Title
description: Short description for SEO and cards.
tags:
  – van hoc
  – nghien cuu
---

Article body content here.
```

#### Bài viết mới kèm author và writing

Tạo `src/content/van/chuong-1-tac-pham-a.md`:

```markdown
---
pubDatetime: 2025-01-01T00:00:00Z
title: Chương 1 – Tiêu đề chương
description: Mô tả ngắn gọn về chương này.
author: le tran dan
writing: Bướm đêm tiến hóa
tags:
  – le-tran-dan
  – buom-dem-tien-hoa
---

Nội dung chương ở đây.
```

Quy tắc cho `author` và `writing`:

– `author` phải là tên dạng plain-text viết đúng như tên file `src/content/author/*.md` tương ứng (khoảng trắng được chuyển thành dấu gạch ngang khi so khớp slug).

– `writing` phải có một tag slug tương ứng trong mảng `tags` để kích hoạt lọc cấp 2. Slug được suy ra qua `cleanSlug(writing.replace(/\s+/g, '-'))`.

– `author` và `writing` phải được khai báo cùng nhau thì phần hiển thị theo nhóm mới kích hoạt.

#### Author entry mới

Tạo `src/content/author/le-tran-dan.md`:

```markdown
---
title: Nguyễn Đan Nguyên
description: Nhà văn, tác giả của nhiều tác phẩm văn học đương đại Việt Nam. Ông đã xuất bản hơn 15 đầu sách và nhận nhiều giải thưởng văn học trong và ngoài nước.
image: https://example.com/le-tran-dan.jpg
---
```

Slug tên file (`le-tran-dan`) phải khớp với `cleanSlug(post.author.replace(/\s+/g, '-'))` để author bio box trên trang bài viết và phần ghi đè SEO trên trang lưu trữ tác giả (`/viet/le-tran-dan/`) được kích hoạt.

### Cấu trúc thư mục

```
.
├── src/
│	 ├── assets/
│	 │	 └── tailwind.css					# Global Tailwind base styles (single source of truth)
│	 ├── components/
│	 │	 ├── article/						# Article-specific components (TOC, reading time, anticopy)
│	 │	 ├── common/						# Shared primitives (image, image-fallback, metadata)
│	 │	 ├── content/						# Page-section components (hero, about, contact, form)
│	 │	 ├── javascript/					# Client-side scripts (analytics, form, schemas, viral)
│	 │	 ├── shared/						# Cross-page components (pagination, tags list)
│	 │	 ├── ui/							# Atomic UI primitives (button, container, form input)
│	 │	 ├── van/							# Article catalogue and list components
│	 │	 └── widgets/						# Page-level composite widgets (header, footer, card, hero)
│	 ├── content/
│	 │	 ├── config.ts						# Zod schemas for van and author collections
│	 │	 ├── author/						# Author bio Markdown files (slug = author name slug)
│	 │	 └── van/							# Article Markdown files
│	 ├── integration/
│	 │	 ├── index.mjs						# Custom Astro integration (virtual module, robots.txt)
│	 │	 └── utils/config-builder.ts		# Merges config.yaml with defaults → named exports
│	 ├── layouts/
│	 │	 ├── main.astro						# Base HTML shell (head, scripts, global slots)
│	 │	 ├── markdown.astro					# Layout wrapper for static .md pages
│	 │	 └── page.astro						# Full-page layout (header + footer + main)
│	 ├── pages/
│	 │	 ├── index.astro					# Homepage
│	 │	 ├── van/							# Article list ([...page].astro) and detail ([slug].astro)
│	 │	 ├── viet/							# Tag index and tag-filtered paginated lists
│	 │	 │	 └── [tag]/[...page].astro		# Author-aware tag archive: SEO override + writing groups
│	 │	 ├── sitemap.xml.ts					# Custom XML sitemap generator
│	 │	 ├── rss.xml.ts						# RSS 2.0 feed generator
│	 │	 ├── indexnow.txt.ts				# IndexNow key endpoint
│	 │	 ├── llms.txt.ts						# LLM-readable site summary endpoint
│	 │	 └── 404.astro						# 404 with 5s auto-redirect
│	 ├── system/
│	 │	 ├── components.ts					# Article list/catalogue config (`VAN_CONFIG`, `CATALOGUE_CONFIG`, ...)
│	 │	 ├── form.ts						# Contact form field definitions + Google Forms mapping
│	 │	 └── logic.ts						# mapEntry(), buildMetadata() – article data helpers
│	 ├── utils/
│	 │	 ├── blog.ts						# Post fetching, normalization, pagination helpers
│	 │	 ├── config.ts						# Config file reader (YAML → typed interfaces)
│	 │	 ├── directories.ts					# Filesystem path helpers
│	 │	 ├── feed.ts						# Shared data for sitemap, RSS, indexnow, and llms feeds
│	 │	 ├── frontmatter.mjs				# Remark/Rehype plugins (reading time, tables, lazy images)
│	 │	 ├── optimization.ts				# Image optimization pipeline via unpic
│	 │	 ├── permalinks.ts					# cleanSlug(), getCanonical(), getPermalink(), URL builders
│	 │	 ├── pexels.ts						# Hero image fetcher (from nhavan.vn/film.txt)
│	 │	 └── utils.ts						# General utility functions
│	 ├── config.yaml						# Master configuration – single source of truth for the site
│	 ├── navigation.js						# Header navigation links
│	 ├── env.d.ts							# Astro environment type declarations
│	 └── types.d.ts							# Global TypeScript type definitions
├── astro.config.mjs						# Astro configuration (integrations, markdown plugins, Vite aliases)
├── tailwind.config.cjs						# Tailwind configuration
├── tsconfig.json							# TypeScript configuration
└── package.json							# Dependencies and npm scripts
```

### Deployment thực tế

– [nhavan.vn](https://nhavan.vn) – Trung tâm nghiên cứu văn học tiếng Việt, thúc đẩy văn hóa đọc.

### Bản quyền

© 2020 Nhà văn. Liên hệ: nhavantuonglai@icloud.com.

---

## English

Nhavan (v26.03.39) is an open-source, high-performance static website framework built on Astro 5, powering nhavan.vn – a Vietnamese literary research and reading-culture platform. The codebase was formerly dual-purpose (also powering an e-commerce store, blur.vn) but has since been trimmed down to a single, article-focused application; all product/cart/checkout code has been removed.

---

### Key features

Configuration:

– Single `config.yaml` file is the source of truth for site identity, SEO, and blog behavior.

– A custom Astro integration (`nhavantuonglai:tasks`) exposes the parsed config as a virtual module (`nhavantuonglai:config`) available throughout the entire codebase.

SEO & structured data:

– JSON-LD schemas: `Article`, `BlogPosting`, `Organization`, `FAQ`, `Breadcrumb`.

– Auto-generated canonical URLs with no trailing slash.

– OpenGraph + Twitter Card meta tags with `vi_VN` locale.

– Per-page robots rules (index/noindex) with pagination pages excluded.

– Custom-built XML sitemap excluding noindex pages.

– IndexNow endpoint for instant search engine notification.

Content library:

– Markdown/MDX articles with auto-calculated reading time (via Remark plugin).

– Auto-generated Table of Contents from article headings.

– Tag/category filtering at `/viet/[tag]` with pagination.

– Related articles based on shared tags.

– Anti-copy content protection script.

– RSS 2.0 feed with `media:content` image enclosures.

– Recent reads tracked in `localStorage`.

– Author taxonomy (`author` collection): dedicated bio pages with title, description, and avatar image; when a tag page matches an author slug, SEO metadata (title, description, hero image) is automatically overridden with the author's data and the page becomes indexable (`noindex: false`).

– Writing taxonomy (`writing` frontmatter field): articles belonging to a literary work are grouped under the author archive page; groups are filtered by two-level tag matching (author tag + writing tag), sorted numerically by slug, and distributed in configurable batches per page; up to two main groups and one "other" group per page, with batch sizes scaling to `postsPerPage` from config.

Performance & UI:

– Static Site Generation (SSG) – pure HTML output, deployable anywhere.

– Image optimization via `unpic` with responsive layout and Pexels CDN integration.

– Native lazy loading injected via Rehype plugin.

– Google Analytics off the main thread via Partytown (no LCP impact).

– Framer Motion animations for smooth component transitions.

– Custom cursor + canvas comet visual effect (`viral.astro`).

– Intersection Observer-based scroll reveal (`.reveal` class).

– Dark/light mode following system preference.

– 404 page with 5 second countdown auto-redirect.

Developer experience:

– TypeScript strict mode across all utilities and system files.

– Zod schema validation for all content collection frontmatter at build time.

– ESLint + Prettier with Astro and Tailwind plugins.

– `~` path alias resolving to `src/`.

– Hot reload watches `config.yaml` changes.

### Tech stack

| Layer | Technology |
|---|---|
| Framework | Astro 5 (SSG, `output: 'static'`) |
| UI Components | React 18 (Astro Islands pattern) |
| Styling | Tailwind CSS v3, CSS custom properties |
| Content | Astro Content Collections (Markdown/MDX) |
| Schema Validation | Zod |
| Image Optimization | unpic |
| Animations | Framer Motion |
| Analytics | Google Analytics 4 via Partytown |
| Slugification | limax |
| Config Parsing | js-yaml |
| Fonts | Be Vietnam Pro (Google Fonts) |
| Deployment | Netlify / Vercel (static) |

### Prerequisites

– Node.js 22.x – [nodejs.org](https://nodejs.org).

– npm ≥ 10.x (bundled with Node).

– VS Code (recommended) – [code.visualstudio.com](https://code.visualstudio.com).

– Recommended extensions: `astro-build.astro-vscode`, `bradlc.vscode-tailwindcss`.

### Installation & local development

#### Clone the repository

```bash
git clone https://github.com/nhavantuonglai/nhavan.vn.git
cd nhavan.vn
```

#### Install dependencies

```bash
npm install
```

#### Configure the site

Open `src/config.yaml` and set the site identity:

```yaml
site:
	name: Your Site Name
	site: "https://nhavan.vn"

apps:
	blog:
		postsPerPage: 15   # controls batch sizes on all list pages including /viet
```

#### Start the development server

```bash
npm run dev
```

The site runs at `http://localhost:4321`. The server hot-reloads on file changes, including `config.yaml`.

#### Build for production

```bash
npm run build
```

Static output is generated in `dist/`. Preview locally:

```bash
npm run preview
```

#### Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start dev server at `localhost:4321` |
| `npm run build` | Build static output to `dist/` |
| `npm run preview` | Preview the production build locally |
| `npm run format` | Format all files with Prettier |
| `npm run lint` | Run ESLint |
| `npm run typecheck` | TypeScript type checking |
| `npm run validate` | Run lint + typecheck together |

### Adding content

#### New article

Create `src/content/van/article-slug.md`:

```markdown
---
pubDatetime: 2025-01-01T00:00:00Z
title: Article Title
description: Short description for SEO and cards.
tags:
  – van hoc
  – nghien cuu
---

Article body content here.
```

#### New article with author and writing

Create `src/content/van/chuong-1-tac-pham-a.md`:

```markdown
---
pubDatetime: 2025-01-01T00:00:00Z
title: Chương 1 – Tiêu đề chương
description: Mô tả ngắn gọn về chương này.
author: le tran dan
writing: Bướm đêm tiến hóa
tags:
  – le-tran-dan
  – buom-dem-tien-hoa
---

Nội dung chương ở đây.
```

Rules for `author` and `writing`:

– `author` must be the plain-text name exactly as written in the corresponding `src/content/author/*.md` filename (spaces are converted to hyphens for slug matching).

– `writing` must have a corresponding tag slug in the `tags` array for level-2 filtering to activate. The slug is derived via `cleanSlug(writing.replace(/\s+/g, '-'))`.

– Both `author` and `writing` must be declared together for the grouped display to activate.

#### New author entry

Create `src/content/author/le-tran-dan.md`:

```markdown
---
title: Nguyễn Đan Nguyên
description: Nhà văn, tác giả của nhiều tác phẩm văn học đương đại Việt Nam. Ông đã xuất bản hơn 15 đầu sách và nhận nhiều giải thưởng văn học trong và ngoài nước.
image: https://example.com/le-tran-dan.jpg
---
```

The filename slug (`le-tran-dan`) must match `cleanSlug(post.author.replace(/\s+/g, '-'))` for the author bio box on article pages and the SEO override on the author archive page (`/viet/le-tran-dan/`) to activate.

### Folder structure

```
.
├── src/
│	 ├── assets/
│	 │	 └── tailwind.css					# Global Tailwind base styles (single source of truth)
│	 ├── components/
│	 │	 ├── article/						# Article-specific components (TOC, reading time, anticopy)
│	 │	 ├── common/						# Shared primitives (image, image-fallback, metadata)
│	 │	 ├── content/						# Page-section components (hero, about, contact, form)
│	 │	 ├── javascript/					# Client-side scripts (analytics, form, schemas, viral)
│	 │	 ├── shared/						# Cross-page components (pagination, tags list)
│	 │	 ├── ui/							# Atomic UI primitives (button, container, form input)
│	 │	 ├── van/							# Article catalogue and list components
│	 │	 └── widgets/						# Page-level composite widgets (header, footer, card, hero)
│	 ├── content/
│	 │	 ├── config.ts						# Zod schemas for van and author collections
│	 │	 ├── author/						# Author bio Markdown files (slug = author name slug)
│	 │	 └── van/							# Article Markdown files
│	 ├── integration/
│	 │	 ├── index.mjs						# Custom Astro integration (virtual module, robots.txt)
│	 │	 └── utils/config-builder.ts		# Merges config.yaml with defaults → named exports
│	 ├── layouts/
│	 │	 ├── main.astro						# Base HTML shell (head, scripts, global slots)
│	 │	 ├── markdown.astro					# Layout wrapper for static .md pages
│	 │	 └── page.astro						# Full-page layout (header + footer + main)
│	 ├── pages/
│	 │	 ├── index.astro					# Homepage
│	 │	 ├── van/							# Article list ([...page].astro) and detail ([slug].astro)
│	 │	 ├── viet/							# Tag index and tag-filtered paginated lists
│	 │	 │	 └── [tag]/[...page].astro		# Author-aware tag archive: SEO override + writing groups
│	 │	 ├── sitemap.xml.ts					# Custom XML sitemap generator
│	 │	 ├── rss.xml.ts						# RSS 2.0 feed generator
│	 │	 ├── indexnow.txt.ts				# IndexNow key endpoint
│	 │	 ├── llms.txt.ts						# LLM-readable site summary endpoint
│	 │	 └── 404.astro						# 404 with 5s auto-redirect
│	 ├── system/
│	 │	 ├── components.ts					# Article list/catalogue config (`VAN_CONFIG`, `CATALOGUE_CONFIG`, ...)
│	 │	 ├── form.ts						# Contact form field definitions + Google Forms mapping
│	 │	 └── logic.ts						# mapEntry(), buildMetadata() – article data helpers
│	 ├── utils/
│	 │	 ├── blog.ts						# Post fetching, normalization, pagination helpers
│	 │	 ├── config.ts						# Config file reader (YAML → typed interfaces)
│	 │	 ├── directories.ts					# Filesystem path helpers
│	 │	 ├── feed.ts						# Shared data for sitemap, RSS, indexnow, and llms feeds
│	 │	 ├── frontmatter.mjs				# Remark/Rehype plugins (reading time, tables, lazy images)
│	 │	 ├── optimization.ts				# Image optimization pipeline via unpic
│	 │	 ├── permalinks.ts					# cleanSlug(), getCanonical(), getPermalink(), URL builders
│	 │	 ├── pexels.ts						# Hero image fetcher (from nhavan.vn/film.txt)
│	 │	 └── utils.ts						# General utility functions
│	 ├── config.yaml						# Master configuration – single source of truth for the site
│	 ├── navigation.js						# Header navigation links
│	 ├── env.d.ts							# Astro environment type declarations
│	 └── types.d.ts							# Global TypeScript type definitions
├── astro.config.mjs						# Astro configuration (integrations, markdown plugins, Vite aliases)
├── tailwind.config.cjs						# Tailwind configuration
├── tsconfig.json							# TypeScript configuration
└── package.json							# Dependencies and npm scripts
```

### Live Deployments

– [nhavan.vn](https://nhavan.vn) – Vietnamese literary research centre, promoting reading culture

### Copyright

© 2020 Nhà văn. Contact: nhavantuonglai@icloud.com.
